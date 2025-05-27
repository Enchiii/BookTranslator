from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from translator import Translator
import os
import shutil
import uuid

app = FastAPI()
BOOKS_DIR = "books"
OUTPUT_DIR = "output"

os.makedirs(BOOKS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/translate/")
async def translate_book(file: UploadFile = File(...), target_lang: str = Form(...)):
    # Save uploaded file
    file_id = str(uuid.uuid4())
    input_path = os.path.join(BOOKS_DIR, f"{file_id}.epub")
    output_path = os.path.join(OUTPUT_DIR, f"{file_id}_translated.epub")

    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Translate using translator
    translator = Translator()
    translator.set_target_lang(target_lang)
    translated_book = translator.translate_book(input_path)
    title = translated_book.get_metadata('DC', 'title')[0][0]

    return FileResponse(translator.save_path, media_type="application/epub+zip", filename=f"{title}_{target_lang}.epub")
