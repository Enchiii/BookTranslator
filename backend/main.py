import uuid
import os

from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from celery.result import AsyncResult
from tasks import translate_epub_task, celery_app
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#TODO: dodac czyzczenie translated i logs co jakis czas i temp jak cos zostanie
TRANSLATED_DIR = "./translated_books"
TEMP_DIR = "./temp_uploads"
LOGS_DIR = "./logs"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/translate-book/")
async def translate_book(
    file: UploadFile,
    language: str = Form(...),
    apiKey: str = Form(...),
    maxInputTokens: int = Form(...),
    maxOutputTokens: int = Form(...),
    maxRequestsPerMinute: int = Form(...),
    maxTokensPerMinute: int = Form(...)
):
    temp_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_file_path = os.path.join(TEMP_DIR, temp_filename)
    with open(temp_file_path, "wb") as f:
        f.write(await file.read())
    task = translate_epub_task.delay(
        temp_file_path,
        language,
        apiKey,
        maxInputTokens,
        maxOutputTokens,
        maxRequestsPerMinute,
        maxTokensPerMinute,
        TRANSLATED_DIR,
        LOGS_DIR
    )
    return {"task_id": task.id}


@app.get("/task-status/{task_id}")
def get_task_progress(task_id):
    result = celery_app.AsyncResult(task_id)

    if result.state == 'PENDING':
        return {"state": "PENDING", "progress": 0}

    elif result.state == 'PROGRESS':
        return {"state": "PROGRESS", "progress": result.info.get("progress", 0)}

    elif result.state == 'SUCCESS':
        return {
            "state": "SUCCESS",
            "progress": 100,
            "output_path": result.result.get("output_path"),
            "filename": result.result.get("filename"),
        }

    elif result.state == 'FAILURE':
        return {
            "state": "FAILURE",
            "error": str(result.info),
        }

    return {"state": result.state}



@app.get("/download/{task_id}")
def download_translated(task_id: str):
    path = os.path.join(TRANSLATED_DIR, f"{task_id}.epub")
    if os.path.exists(path):
        return FileResponse(path, media_type='application/epub+zip', filename=f"translated_{task_id}.epub")
    return JSONResponse(status_code=404, content={"error": "File not ready or does not exist."})
