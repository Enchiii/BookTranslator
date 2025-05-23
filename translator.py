import re
import os
import time
import google.generativeai as genai

from ebooklib import epub
from datetime import datetime
from log_type import LogType
from config import API_KEY


class Translator:
    def __init__(self, save_path, target_lang: str="pl"):
        self.target_lang = target_lang
        self.save_path = save_path
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
        self.max_requests_per_day = 500
        self.max_tokens_per_minute = 1_000_000

        self.__requests_per_day_left = 500
        self.__requests_sent = 0
        self.__tokens_sent = 0
        self.__current_window_start = datetime.now()

        self.logs_path = "./logs"
        if not os.path.exists(self.logs_path):
            print(f"Creating directory: {self.logs_path}")
            os.makedirs(self.logs_path)


    def set_target_lang(self, target_lang: str) -> None:
        self.target_lang = target_lang

    def translate_book(self, path: str) -> None:
        print("📖 Book translation started!")
        book = epub.read_epub(path)
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

                chunks = self.__split_html_into_chunks(html)
                translated_chunks = []

                for j, chunk in enumerate(chunks):
                    print(f"   ↳ Chunk {j + 1}/{len(chunks)}")
                    translated_chunk = self.__translate_chunk(chunk)
                    translated_chunks.append(translated_chunk)

                translated_html = ''.join(translated_chunks)

                # writing logs
                self.__write_logs(LogType.NORMAL, f"🔁 Translated {i + 1}/{total}: {item.file_name}\n{translated_html}")
                # with open(f"{self.logs_path}/translation_logs", "a", encoding="utf-8") as f:
                #     f.write(f"\n{'*' * 40}\n")
                #     f.write(f"🔁 Translated {i + 1}/{total}: {item.file_name}\n")
                #     f.write(translated_html)
                #     f.write(f"\n{'*' * 40}\n")

                new_item = epub.EpubHtml(
                    uid=item.id,
                    file_name=item.file_name,
                    media_type=item.media_type,
                    content=translated_html
                )
                translated_book.add_item(new_item)
            else:
                translated_book.add_item(item)

        # copy spine i toc
        translated_book.spine = book.spine
        translated_book.toc = book.toc

        # save book
        output_path = f"{self.save_path}/{book_title}_{self.target_lang}.epub"
        epub.write_epub(output_path, translated_book)

        print("✅ Book translation completed!")
        print(f"📦 Book saved in: {output_path}")

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

    def __translate_chunk(self, html_chunk: str) -> str:
        prompt = (
            f"Translate the following HTML to {self.target_lang} language.\n"
            "Keep the HTML tags untouched and translate only the visible text.\n"
            "Do not remove or add any tags, and preserve the original structure:\n\n"
            f"{html_chunk}"
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
                # with open(f"{self.logs_path}/warning_logs", "a", encoding="utf-8") as f:
                #     f.write(f"\n{'*' * 40}\n")
                #     f.write(f"HTML chunk: {html_chunk}\n")
                #     f.write(f"Response: {response}")
                #     f.write(f"\n{'*' * 40}\n")
                return html_chunk
        except Exception as e:
            print(f"❌ Error during translation: {e}")
            # writing logs
            self.__write_logs(LogType.ERROR, f"Error: {e}\nHTML chunk: {html_chunk}")
            # with open(f"{self.logs_path}/error_logs", "a", encoding="utf-8") as f:
            #     f.write(f"\n{'*' * 40}\n")
            #     f.write(f"Error: {e}\n")
            #     f.write(f"HTML chunk: {html_chunk}")
            #     f.write(f"\n{'*' * 40}\n")
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

        self.__requests_per_day_left -= 1
        self.__requests_sent += 1
        self.__tokens_sent += estimated_tokens

    def __write_logs(self, log_type: LogType, msg: str):
        name = ""
        match log_type:
            case LogType.NORMAL:
                name = "translation_logs"
            case LogType.WARNING:
                name = "warning_logs"
            case LogType.ERROR:
                name = "error_logs"

        with open(f"{self.logs_path}/{name}", "a", encoding="utf-8") as f:
            f.write(f"\n{'*' * 40}\n")
            f.write(msg)
            f.write(f"\n{'*' * 40}\n")
