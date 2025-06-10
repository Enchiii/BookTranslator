import os

from backend.translator import Translator


if __name__ == '__main__':
    input_path = input("Enter path to EPUB file: ").strip()
    while not os.path.isfile(input_path) or not input_path.endswith('.epub'):
        print("❌ Invalid file. Please enter a valid .epub file.")
        input_path = input("Enter path to EPUB file: ").strip()

    target_lang = input("Enter target language: ")
    book_translator = Translator(logs=True)
    book_translator.set_target_lang(target_lang)

    book_translator.translate_book(input_path)
