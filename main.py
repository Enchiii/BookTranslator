import os

from translator import Translator


BOOKS_DIR = "./Books"
TRANSLATED_BOOKS_DIR = "./TranslatedBooks"

if __name__ == '__main__':
    target_lang = input("Enter target language: ")
    book_translator = Translator(TRANSLATED_BOOKS_DIR, target_lang)

    all_books = os.listdir(BOOKS_DIR)
    for book in all_books:
        book_translator.translate_book(f"{BOOKS_DIR}/{book}")
