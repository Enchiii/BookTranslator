import re
import os
import time
import google.generativeai as genai

from ebooklib import epub
from datetime import datetime
from log_type import LogType
from config import API_KEY

from bs4 import BeautifulSoup


class Translator:
    def __init__(self):
        self.target_lang = "polish"
        self.save_path = "./TranslatedBooks"
        if not os.path.exists(self.save_path):
            print(f"Creating directory: {self.save_path}")
            os.makedirs(self.save_path)

        # model configuration
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

        #  model limit
        self.max_input_tokens = 6_000 # input cant be bigger than output
        self.__max_input_chars = self.max_input_tokens * 4  # 1 token ~ 4 chars
        self.max_output_tokens = 8_000
        self.max_requests_per_minute = 15
        self.max_tokens_per_minute = 1_000_000

        self.requests_per_day = 500
        self.__requests_left_per_day = 500
        self.__requests_sent = 0
        self.__tokens_sent = 0
        self.__current_window_start = datetime.now()

        self.logs_path = "./logs"
        if not os.path.exists(self.logs_path):
            print(f"Creating directory: {self.logs_path}")
            os.makedirs(self.logs_path)

    def config(self,  **kwargs)  -> None:
        for key, value in kwargs.items():
            if key == "max_input_tokens":
                self.max_input_tokens = value
                self.__max_input_chars = value * 4
            match key:
                case "save_path": self.save_path = value
                case "target_lang": self.target_lang = value
                case "max_input_tokens": self.max_input_tokens = value; self.__max_input_chars = value * 4
                case "max_output_tokens": self.max_output_tokens = value
                case "max_requests_per_minute": self.max_requests_per_minute = value
                case "max_tokens_per_minute": self.max_tokens_per_minute = value
                case "requests_per_day": self.requests_per_day = value
                case _: raise AttributeError(f"Unknown configuration key: {key}")

    def set_target_lang(self, target_lang: str) -> None:
        self.target_lang = target_lang

    def translate_book(self, path: str) -> epub.EpubBook:
        print("📖 Book translation started!")
        start_time = datetime.now()
        book = epub.read_epub(path, {"ignore_ncx": True})
        translated_book = epub.EpubBook()

        book_title = book.get_metadata('DC', 'title')[0][0]
        translated_book.set_title(book_title)
        translated_book.set_identifier(book.get_metadata('DC', 'identifier')[0][0])

        html_items = [x for x in book.get_items() if x.get_type() == 9]
        total = len(html_items)

        for i, item in enumerate(book.get_items()):
            if item.get_type() == 9:
                print(f"🔁 Translating {i + 1}/{total}: {item.file_name}")
                html = item.get_content().decode('utf-8')

                start = datetime.now()
                chunks = self.__split_html_into_chunks(html)
                end = datetime.now()
                self.__write_logs(LogType.TIME, f"🔁 Item {i + 1}/{total}: {item.file_name} split into chunks time: {end - start}\n")
                translated_chunks = []

                msg = f"🔁 Translated {i + 1}/{total}: {item.file_name}\n"
                for j, chunk in enumerate(chunks):
                    print(f"   ↳ Chunk {j + 1}/{len(chunks)}")
                    start = datetime.now()
                    context_before = self.__extract_last_sentence(chunks[j - 1]) if j > 0 else ""
                    context_after = self.__extract_first_sentence(chunks[j + 1]) if j < len(chunks) - 1 else ""
                    translated_chunk = self.__translate_chunk(context_before, chunk, context_after)
                    end = datetime.now()
                    self.__write_logs(LogType.TIME, f"   ↳ Chunk {j + 1}/{len(chunks)} translating time: {end - start}\n")
                    translated_chunks.append(translated_chunk)

                    msg += f"   ↳ Chunk {j + 1}/{len(chunks)}\n"
                    msg += f"       Context before: {context_before}\n"
                    msg += f"       Translated chunk: {translated_chunk}\n"
                    msg += f"       Context after: {context_after}\n\n"

                translated_html = ''.join(translated_chunks)

                # writing logs
                self.__write_logs(LogType.NORMAL, msg)

                new_item = epub.EpubHtml(
                    uid=item.id,
                    file_name=item.file_name,
                    media_type=item.media_type,
                    content=translated_html.encode("utf-8")
                )
                translated_book.add_item(new_item)
            else:
                translated_book.add_item(item)

        # copy spine i toc
        translated_book.spine = book.spine
        translated_book.toc = book.toc

        print("✅ Book translation completed!")

        # validate whole book before saving
        print("🔍 Validating translated book structure...")
        if self.__validate_book(translated_book):
            output_path = f"{self.save_path}/{book_title}_{self.target_lang}.epub"
            epub.write_epub(output_path, translated_book)
            print(f"📦 Book saved in: {output_path}")
        else:
            print("❌ Book contains invalid HTML. Not saved.")

        end_time = datetime.now()
        duration = end_time - start_time
        print(f"⏱️ Translation took {duration} (hh:mm:ss)")
        print(f"Total requests sent: {self.requests_per_day - self.__requests_left_per_day}. Requests left for today: {self.__requests_left_per_day}")

        return  translated_book

    def __split_html_into_chunks(self, html: str) -> list[str]:
        chunks = []
        current_chunk = ""
        tokens = re.split(r"(\s+|<[^>]+>)", html)

        for token in tokens:
            if token is None:
                continue
            if len(current_chunk) + len(token) > self.__max_input_chars:
                chunks.append(current_chunk)
                current_chunk = token
            else:
                current_chunk += token

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def __translate_chunk(self, context_before: str, html_chunk: str, context_after: str) -> str:
        prompt = (
            f"Translate the following HTML fragment into {self.target_lang}.\n\n"

            "🛑 Do NOT modify the HTML structure in any way:\n"
            "- Do NOT add, remove, or change any HTML tags or attributes.\n"
            "- Keep all HTML entities (e.g., &nbsp;, &amp;, &lt;) exactly as they are.\n"
            "- Do NOT wrap your answer in code blocks (e.g., no triple backticks ```).\n"

            "📝 Translate ONLY the human-visible **text content** between HTML tags.\n"
            "- Leave all HTML tags and attributes untouched.\n"
            "- If there is no translatable text in the fragment, return it unchanged.\n"

            "🧠 Maintain context and consistency:\n"
            f"- Use the previous and next context to guide your translation and ensure coherence.\n"
            f"- Do NOT translate names of people, places, or fictional entities unless a well-known {self.target_lang} equivalent exists.\n\n"

            f"Context before:\n{context_before}\n\n"
            f"🔽 HTML fragment to translate (only translate the visible text):\n{html_chunk}\n\n"
            f"Context after:\n{context_after}\n\n"

            "✅ Final output: ONLY the translated HTML fragment with the original structure preserved. DO NOT include any explanation, markdown formatting, or comments."
        )

        estimated_input_tokens = int(len(prompt) / 4)  # 1 token ~ 4 chars

        self.__wait_if_needed(estimated_input_tokens + self.max_output_tokens) # our output can have max 8000 tokens, and we add this to our token limit per minute

        try:
            response = self.model.generate_content(prompt)
            if hasattr(response, 'text') and response.text:
                return response.text
            else:
                print("⚠️ Empty response from model.")
                # writing logs
                self.__write_logs(LogType.WARNING, f"HTML chunk: {html_chunk}\nResponse: {response}")
                return html_chunk
        except Exception as e:
            print(f"❌ Error during translation: {e}")
            # writing logs
            self.__write_logs(LogType.ERROR, f"Error: {e}\nHTML chunk: {html_chunk}")
            return html_chunk

    def __extract_last_sentence(self, html: str) -> str:
        text = re.sub(r'<[^>]+>', '', html)
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return sentences[-1] if sentences else ""

    def __extract_first_sentence(self, html: str) -> str:
        text = re.sub(r'<[^>]+>', '', html)
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return sentences[0] if sentences else ""

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

        self.__requests_left_per_day -= 1
        self.__requests_sent += 1
        self.__tokens_sent += estimated_tokens

    def __validate_book(self, book: epub.EpubBook) -> bool:
        valid = True
        for i, item in enumerate(book.get_items()):
            if item.get_type() == 9:  # HTML
                html = item.get_content().decode("utf-8", errors="ignore")
                try:
                    soup = BeautifulSoup(html, "html.parser")
                    if not soup or not soup.html:
                        raise ValueError("HTML root missing")
                except Exception as e:
                    valid = False
                    self.__write_logs(LogType.ERROR, f"❌ Invalid HTML in {item.file_name}: {e}")
        return valid

    def __write_logs(self, log_type: LogType, msg: str):
        name = ""
        match log_type:
            case LogType.NORMAL: name = "translation_logs"
            case LogType.WARNING: name = "warning_logs"
            case LogType.ERROR: name = "error_logs"
            case LogType.TIME:name = "time_logs"

        with open(f"{self.logs_path}/{name}", "a", encoding="utf-8") as f:
            f.write(f"\n{'*' * 40}\n")
            f.write(msg)
            f.write(f"\n{'*' * 40}\n")
