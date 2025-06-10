import os
import time
import google.generativeai as genai

from ebooklib import epub
from datetime import datetime
from .log_type import LogType
from .config import API_KEY
from .utils import write_logs, validate_book, extract_first_sentence, extract_last_sentence, build_prompt, split_html_into_chunks


class Translator:
    def __init__(self, logs: bool=False):
        self.logs = logs
        self.target_lang = "polish"
        self.save_path = "./translated_books"
        self.save_name = ""

        # model configuration
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

        self.translating_duration = 0

        #  model limit
        self.max_input_tokens = 4000 # input cant be bigger than output
        self.__max_input_chars = self.max_input_tokens * 4  # 1 token ~ 4 chars
        self.max_output_tokens = 6000
        self.max_requests_per_minute = 15
        self.max_tokens_per_minute = 1_000_000

        self.total_requests_sent = 0
        self.__requests_sent = 0
        self.__tokens_sent = 0
        self.__current_window_start = datetime.now()

        self.progress = 0.0

        if logs:
            self.logs_path = "./logs"
            if not os.path.exists(self.logs_path):
                print(f"Creating directory: {self.logs_path}")
                os.makedirs(self.logs_path)

    def config(self,  **kwargs)  -> None:
        for key, value in kwargs.items():
            match key:
                case "max_input_tokens": self.max_input_tokens = value; self.__max_input_chars = value * 4
                case "max_output_tokens": self.max_output_tokens = value
                case "max_requests_per_minute": self.max_requests_per_minute = value
                case "max_tokens_per_minute": self.max_tokens_per_minute = value
                case _: raise AttributeError(f"Unknown configuration key: {key}")

    @staticmethod
    def set_api_key(api_key: str) -> None:
        if api_key is None or api_key == "": return
        genai.configure(api_key=api_key)

    def set_save_path(self, save_path: str) -> None:
        self.save_path = save_path
        if not os.path.exists(self.save_path):
            print(f"Creating directory: {self.save_path}")
            os.makedirs(self.save_path)

    def set_save_name(self, save_name: str) -> None:
        self.save_name = save_name

    def set_logs_path(self, logs_path: str) -> None:
        self.logs_path = logs_path
        if not os.path.exists(self.logs_path):
            print(f"Creating directory: {self.logs_path}")
            os.makedirs(self.logs_path)

    def set_target_lang(self, target_lang: str) -> None:
        self.target_lang = target_lang

    def translate_book(self, path: str) -> epub.EpubBook:
        print("📖 Book translation started!")
        start_time = datetime.now()
        book = epub.read_epub(path, {"ignore_ncx": True})
        translated_book = self.__create_book_metadata(book)

        html_items = [x for x in book.get_items() if x.get_type() == 9]
        total = len(html_items)

        for i, item in enumerate(book.get_items()):
            if item.get_type() == 9:
                translated_item = self.__translate_item(item, i, total)
                self.progress = round(i/total * 100, 2)
                translated_book.add_item(translated_item)
            else:
                translated_book.add_item(item)

        translated_book.spine = book.spine
        translated_book.toc = book.toc

        self.__save_book(book, translated_book, start_time)

        return translated_book

    def translate_book_gen(self, path: str):
        print("📖 Book translation started!")
        start_time = datetime.now()
        book = epub.read_epub(path, {"ignore_ncx": True})
        translated_book = self.__create_book_metadata(book)

        html_items = [x for x in book.get_items() if x.get_type() == 9]
        total = len(html_items)

        for i, item in enumerate(book.get_items()):
            if item.get_type() == 9:
                translated_item = self.__translate_item(item, i, total)
                self.progress = round(i/total * 100, 2)
                yield self.progress
                translated_book.add_item(translated_item)
            else:
                translated_book.add_item(item)

        translated_book.spine = book.spine
        translated_book.toc = book.toc

        self.__save_book(book, translated_book, start_time)

        yield 1.0

    @staticmethod
    def __create_book_metadata(book: epub.EpubBook) -> epub.EpubBook:
        translated_book = epub.EpubBook()
        title = book.get_metadata('DC', 'title')[0][0]
        translated_book.set_title(title)
        translated_book.set_identifier(book.get_metadata('DC', 'identifier')[0][0])
        return translated_book

    def __translate_item(self, item: epub.EpubHtml, index: int, total: int) -> epub.EpubHtml:
        print(f"🔁 Translating {index + 1}/{total}: {item.file_name}")
        html = item.get_content().decode('utf-8')

        start = datetime.now()
        chunks = split_html_into_chunks(html, self.__max_input_chars)
        end = datetime.now()

        if self.logs:
            write_logs(self.logs_path, LogType.TIME, f"🔁 Item {index + 1}/{total}: {item.file_name} split into chunks time: {end - start}\n")

        translated_chunks = []
        msg = f"🔁 Translated {index + 1}/{total}: {item.file_name}\n"

        for j, chunk in enumerate(chunks):
            print(f"   ↳ Chunk {j + 1}/{len(chunks)}")
            context_before = extract_last_sentence(chunks[j - 1]) if j > 0 else ""
            context_after = extract_first_sentence(chunks[j + 1]) if j < len(chunks) - 1 else ""
            start = datetime.now()
            translated_chunk = self.__translate_chunk(context_before, chunk, context_after)
            end = datetime.now()

            if self.logs:
                write_logs(self.logs_path, LogType.TIME, f"   ↳ Chunk {j + 1}/{len(chunks)} translating time: {end - start}\n")

            translated_chunks.append(translated_chunk)

            msg += (f"   ↳ Chunk {j + 1}/{len(chunks)}\n"
                    f"       Context before: {context_before}\n"
                    f"       Translated chunk: {translated_chunk}\n"
                    f"       Context after: {context_after}\n\n")

        if self.logs:
            write_logs(self.logs_path, LogType.NORMAL, msg)

        translated_html = ''.join(translated_chunks)
        return epub.EpubHtml(
            uid=item.id,
            file_name=item.file_name,
            media_type=item.media_type,
            content=translated_html.encode("utf-8")
        )

    def __save_book(self, original: epub.EpubBook, translated: epub.EpubBook, start_time: datetime):
        print("✅ Book translation completed!")
        print("🔍 Validating translated book structure...")

        book_title = original.get_metadata('DC', 'title')[0][0]
        if self.save_name == "":
            output_path = f"{self.save_path}/{book_title}_{self.target_lang}.epub"
        else:
            output_path = f"{self.save_path}/{self.save_name}.epub"

        if validate_book(translated):
            epub.write_epub(output_path, translated)
            print(f"📦 Book saved in: {output_path}")
        else:
            print("❌ Book contains invalid HTML. Not saved.")

        end_time = datetime.now()
        self.translating_duration = end_time - start_time
        print(f"⏱️ Translation took {self.translating_duration} (hh:mm:ss)")
        print(f"Total requests sent: {self.total_requests_sent}")

    def __translate_chunk(self, context_before: str, html_chunk: str, context_after: str) -> str:
        prompt = build_prompt(self.target_lang, context_before, html_chunk, context_after)

        estimated_input_tokens = int(len(prompt) / 4)  # 1 token ~ 4 chars

        self.__wait_if_needed(estimated_input_tokens + self.max_output_tokens) # our output can have max 8000 tokens, and we add this to our token limit per minute

        try:
            response = self.model.generate_content(prompt)
            if hasattr(response, 'text') and response.text:
                return response.text
            else:
                print("⚠️ Empty response from model.")
                # writing logs
                if self.logs:
                    write_logs(self.logs_path, LogType.WARNING, f"HTML chunk: {html_chunk}\nResponse: {response}")

                # wait some seconds and try one more time
                time.sleep(15)
                response = self.model.generate_content(prompt)
                if hasattr(response, 'text') and response.text:
                    return response.text

                return html_chunk
        except Exception as e:
            print(f"❌ Error during translation: {e}")
            # writing logs
            if self.logs:
                write_logs(self.logs_path, LogType.ERROR, f"Error: {e}\nHTML chunk: {html_chunk}")
            return html_chunk

    def __wait_if_needed(self, estimated_tokens: int):
        now = datetime.now()
        elapsed = (now - self.__current_window_start).total_seconds()

        if elapsed >= 60:
            # window reset
            self.__current_window_start = now
            self.__requests_sent = 0
            self.__tokens_sent = 0

        # out of request or tokens per minute -> wait
        while (self.__requests_sent >= self.max_requests_per_minute or
               self.__tokens_sent + estimated_tokens > self.max_tokens_per_minute):
            wait_time = 60 - elapsed
            wait_time = max(wait_time, 1)
            print(f"⏳ Rate limit hit. Used {self.__requests_sent}/{self.max_requests_per_minute} request and {self.__tokens_sent}/{self.max_tokens_per_minute} tokens."
                  f"Waiting {int(wait_time)} seconds...")
            time.sleep(wait_time)
            self.__current_window_start = datetime.now()
            self.__requests_sent = 0
            self.__tokens_sent = 0
            elapsed = 0

        self.total_requests_sent += 1
        self.__requests_sent += 1
        self.__tokens_sent += estimated_tokens
