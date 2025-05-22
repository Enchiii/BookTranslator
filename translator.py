import re
import os
import time
import google.generativeai as genai

from ebooklib import epub
from datetime import datetime, timedelta
from config import API_KEY


class Translator:
    def __init__(self, save_path, target_lang: str="pl", max_chars: int = 6000):
        self.target_lang = target_lang
        self.save_path = save_path
        if not os.path.exists(self.save_path):
            print(f"Creating directory: {self.save_path}")
            os.makedirs(self.save_path)

        # max  chars per chunk
        self.max_chars = max_chars

        # model configuration
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        #gemini-2.0-flash gemini-2.0-flash-lite

        #  nax request and token per minute
        self.max_requests_per_minute = 15
        self.max_tokens_per_minute = 1_000_000

        self.requests_sent = 0
        self.tokens_sent = 0
        self.current_window_start = datetime.now()

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
                with open(f"{self.logs_path}/translation_logs", "a", encoding="utf-8") as f:
                    f.write(f"\n{'*' * 40}\n")
                    f.write(f"🔁 Translated {i + 1}/{total}: {item.file_name}\n")
                    f.write(translated_html)
                    f.write(f"\n{'*' * 40}\n")

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
            if len(current_chunk) + len(token) > self.max_chars:
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

        # estimated tokens for response
        estimated_response_tokens = 3000
        estimated_input_tokens = int(len(prompt) / 4)  # 1 token ~ 4 chars

        self.__wait_if_needed(estimated_input_tokens + estimated_response_tokens)

        try:
            response = self.model.generate_content(prompt)
            if hasattr(response, 'text') and response.text:
                return response.text
            else:
                print("⚠️ Empty response from model.")
                # writing logs
                with open(f"{self.logs_path}/warning_logs", "a", encoding="utf-8") as f:
                    f.write(f"\n{'*' * 40}\n")
                    f.write(f"HTML chunk: {html_chunk}\n")
                    f.write(f"Response: {response}\n")
                    f.write(f"\n{'*' * 40}\n")
                return html_chunk
        except Exception as e:
            print(f"❌ Error during translation: {e}")
            # writing logs
            with open(f"{self.logs_path}/error_logs", "a", encoding="utf-8") as f:
                f.write(f"\n{'*' * 40}\n")
                f.write(f"Error: {e}\n")
                f.write(f"HTML chunk: {html_chunk}\n")
                f.write(f"\n{'*' * 40}\n")
            return html_chunk

    def __wait_if_needed(self, estimated_tokens: int):
        now = datetime.now()
        elapsed = (now - self.current_window_start).total_seconds()

        if elapsed >= 60:
            # window reset
            self.current_window_start = now
            self.requests_sent = 0
            self.tokens_sent = 0

        # out of request or tokens per minute -> wait
        while (self.requests_sent >= self.max_requests_per_minute or
               self.tokens_sent + estimated_tokens > self.max_tokens_per_minute):
            wait_time = 60 - elapsed
            wait_time = max(wait_time, 1)
            print(f"⏳ Rate limit hit. Waiting {int(wait_time)} seconds...")
            time.sleep(wait_time)
            self.current_window_start = datetime.now()
            self.requests_sent = 0
            self.tokens_sent = 0
            elapsed = 0

        self.requests_sent += 1
        self.tokens_sent += estimated_tokens
