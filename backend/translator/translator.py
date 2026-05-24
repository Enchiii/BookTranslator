import os
import re
from datetime import datetime
from typing import Generator

import torch
from ebooklib import epub
from transformers.models.auto.modeling_auto import AutoModelForSeq2SeqLM
from transformers.models.auto.tokenization_auto import AutoTokenizer

from .log_type import LogType
from .utils import (
    translate_html_soup,
    validate_book,
    write_logs,
)


class Translator:
    def __init__(
        self, logs: bool = True, model_name: str = "facebook/nllb-200-distilled-600M"
    ):
        """
        Models: "facebook/nllb-200-3.3B", facebook/nllb-200-distilled-1.3B, facebook/nllb-200-distilled-600M
        """
        self.logs = logs
        self.save_path = "./translated_books"
        self.save_name = ""

        # NLLB requires FLORES-200 language codes
        self.src_lang = "eng_Latn"
        self.target_lang = "pol_Latn"

        # Model configuration
        print(f"🤖 Loading model {model_name}...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"⚙️ Using device: {self.device.upper()}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)

        self.translating_duration = 0
        self.max_tokens = 512  # Optimal context window for NLLB
        self.progress = 0.0

        if logs:
            self.logs_path = "./logs"
            if not os.path.exists(self.logs_path):
                print(f"Creating directory: {self.logs_path}")
                os.makedirs(self.logs_path)

    def config(self, **kwargs) -> None:
        """
        Configuration method for all translator settings.
        Supported keys: src_lang, target_lang, save_path, save_name, logs_path
        """
        for key, value in kwargs.items():
            match key:
                case "src_lang":
                    self.src_lang = value
                case "target_lang":
                    self.target_lang = value
                case "save_name":
                    self.save_name = value
                case "save_path":
                    self.save_path = value
                    self.__ensure_dir(self.save_path)
                case "logs_path":
                    self.logs_path = value
                    self.__ensure_dir(self.logs_path)
                case _:
                    raise AttributeError(f"Unknown configuration key: {key}")

    def __ensure_dir(self, path: str) -> None:
        """Helper to create directory if it doesn't exist."""
        if not os.path.exists(path):
            print(f"Creating directory: {path}")
            os.makedirs(path, exist_ok=True)

    def translate_book_gen(self, path: str) -> Generator[float, None, None]:
        print("📖 Book translation started!")
        start_time = datetime.now()
        book = epub.read_epub(path, {"ignore_ncx": True})
        translated_book = self.__create_book_metadata(book)

        html_items = [x for x in book.get_items() if x.get_type() == 9]
        total = len(html_items)

        for i, item in enumerate(book.get_items()):
            if item.get_type() == 9:
                translated_item = self.__translate_item(item, i, total)
                self.progress = round((i + 1) / total * 100, 2)
                yield self.progress
                translated_book.add_item(translated_item)
            else:
                translated_book.add_item(item)

        translated_book.spine = book.spine
        translated_book.toc = book.toc

        self.__save_book(book, translated_book, start_time)
        yield 100.0

    @staticmethod
    def __create_book_metadata(book: epub.EpubBook) -> epub.EpubBook:
        translated_book = epub.EpubBook()
        title = book.get_metadata("DC", "title")[0][0]
        translated_book.set_title(title)
        translated_book.set_identifier(book.get_metadata("DC", "identifier")[0][0])
        return translated_book

    def __translate_item(
        self, item: epub.EpubHtml, index: int, total: int
    ) -> epub.EpubHtml:
        print(f"🔁 Translating {index}/{total}: {item.file_name}")

        raw_content = item.get_content()
        html = (
            raw_content.decode("utf-8", errors="ignore")
            if isinstance(raw_content, bytes)
            else str(raw_content)
        )

        start = datetime.now()
        translated_html = translate_html_soup(
            html_content=html,
            translate_func=self.__translate_text,
            logs_path=self.logs_path if self.logs else "",
            logs=self.logs,
        )
        end = datetime.now()

        if self.logs:
            write_logs(
                self.logs_path,
                LogType.TIME,
                f"🔁 Item {index}/{total}: {item.file_name} translation time: {end - start}\n",
            )

        return epub.EpubHtml(
            uid=item.id,
            file_name=item.file_name,
            media_type=item.media_type,
            content=translated_html.encode("utf-8"),
        )

    def __save_book(
        self, original: epub.EpubBook, translated: epub.EpubBook, start_time: datetime
    ):
        print("✅ Book translation completed!")
        print("🔍 Validating translated book structure...")

        book_title = original.get_metadata("DC", "title")[0][0]
        if self.save_name == "":
            output_path = f"{self.save_path}/{book_title}_{self.target_lang}.epub"
        else:
            output_path = f"{self.save_path}/{self.save_name}.epub"

        if validate_book(translated, self.logs_path if self.logs else "./logs"):
            epub.write_epub(output_path, translated)
            print(f"📦 Book saved in: {output_path}")
        else:
            print("❌ Book contains invalid HTML. Not saved.")

        end_time = datetime.now()
        self.translating_duration = end_time - start_time
        print(f"⏱️ Translation took {self.translating_duration} (hh:mm:ss)")

    def __translate_text(self, text: str) -> str:
        if not text.strip():
            return text

        self.tokenizer.src_lang = self.src_lang

        # Split text into sentences intelligently using regex (lookbehind for punctuation)
        sentences = re.split(r"(?<=[.!?])\s+", text)

        translated_chunks = []
        current_chunk = []
        current_tokens_count = 0

        # Safe NLLB context window calculation (512 total - 4 for mandatory system tokens)
        max_safe_capacity = self.max_tokens - 4

        for sentence in sentences:
            if not sentence.strip():
                continue

            # Measure exactly how many tokens this sentence contains
            sentence_tokens = len(
                self.tokenizer.encode(sentence, add_special_tokens=False)
            )

            # Scenario A: Single sentence is an absolute behemoth that exceeds the full block size on its own
            if sentence_tokens > max_safe_capacity:
                if current_chunk:
                    translated_chunks.append(
                        self.__execute_model_generation(" ".join(current_chunk))
                    )
                    current_chunk = []
                    current_tokens_count = 0

                # Force chunking by words/sub-tokens for this extreme edge case
                translated_chunks.append(self.__execute_model_generation(sentence))
                continue

            # Scenario B: Sentence overflows the current ongoing bucket pool
            if current_tokens_count + sentence_tokens > max_safe_capacity:
                translated_chunks.append(
                    self.__execute_model_generation(" ".join(current_chunk))
                )
                current_chunk = [sentence]
                current_tokens_count = sentence_tokens
            else:
                current_chunk.append(sentence)
                current_tokens_count += sentence_tokens

        # Process any remaining sentences trapped inside the buffer pipeline
        if current_chunk:
            translated_chunks.append(
                self.__execute_model_generation(" ".join(current_chunk))
            )

        return " ".join(translated_chunks)

    def __execute_model_generation(self, text_block: str) -> str:
        """Executes raw pipeline compilation and inference via the GPU/CPU hardware."""
        inputs = self.tokenizer(
            text_block, return_tensors="pt", max_length=self.max_tokens, truncation=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        try:
            forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(self.target_lang)
            translated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_length=self.max_tokens,
                num_beams=2,
            )
            return self.tokenizer.batch_decode(
                translated_tokens, skip_special_tokens=True
            )[0]
        except Exception as e:
            print(f"❌ NLLB Translation Error: {e}")
            if self.logs:
                write_logs(
                    self.logs_path, LogType.ERROR, f"Error: {e}\nRaw Text: {text_block}"
                )
            return text_block
