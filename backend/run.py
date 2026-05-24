import os
import time

from translator import Translator


def main():
    MODEL_NAME = "facebook/nllb-200-distilled-600M"

    BOOK_PATH = "D:/Projects/Projects/BookTranslator/backend/The_Charisma_Myth.epub"

    if not os.path.exists(BOOK_PATH):
        print(f"❌ Error: File not found at {BOOK_PATH}")
        return

    translator = Translator(logs=True, model_name=MODEL_NAME)

    translator.config(
        src_lang="eng_Latn",  # Source: English
        target_lang="pol_Latn",  # Target: Polish
        save_path="./translated_books",
        logs_path="./logs",
    )

    print(f"🚀 Starting translation for: {BOOK_PATH}")
    print("📦 Output will be saved in: ./translated_books")

    start_time = time.time()

    try:
        for progress in translator.translate_book_gen(BOOK_PATH):
            print(f"⏳ Progress: {progress}%", end="\r")

        end_time = time.time()
        duration = end_time - start_time
        print(f"\n✨ Done! Total process time: {duration:.2f} seconds.")

    except Exception as e:
        print(f"\n❌ Critical Error during translation: {e}")


if __name__ == "__main__":
    main()
