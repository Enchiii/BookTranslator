import os

from ebooklib import epub
from translator import Translator


if __name__ == '__main__':
    input_path = input("Enter path to EPUB file: ").strip()
    while not os.path.isfile(input_path) or not input_path.endswith('.epub'):
        print("❌ Invalid file. Please enter a valid .epub file.")
        input_path = input("Enter path to EPUB file: ").strip()
    # input_path = "./books/Gardens of the Moon (The Malazan Book of the Fallen, Book 1) -- Erikson, Steven.epub"

    target_lang = input("Enter target language: ")
    book_translator = Translator()
    book_translator.set_target_lang(target_lang)

    book_translator.translate_book(input_path)
