import os

from translator import Translator
from ebooklib import epub

BOOKS_DIR = "./Books"

if __name__ == '__main__':
    target_lang = input("Enter target language: ")
    book_translator = Translator()
    book_translator.set_target_lang(target_lang)

    all_books = os.listdir(BOOKS_DIR)
    for book_name in all_books:
        book_translator.translate_book(f"{BOOKS_DIR}/{book_name}")
