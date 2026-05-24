import os
import shutil
import time
import uuid
from typing import Any, Dict

from fastapi import BackgroundTasks, FastAPI, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Assuming your Translator class is located in a file named translator.py
from translator import Translator

app = FastAPI()

# Configure CORS to allow communication with your frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Application directories
TRANSLATED_DIR = "./translated_books"
TEMP_DIR = "./temp_uploads"
LOGS_DIR = "./logs"

# Ensure all necessary working directories exist on startup
for folder in [TRANSLATED_DIR, TEMP_DIR, LOGS_DIR]:
    os.makedirs(folder, exist_ok=True)

# In-memory dictionary to track task statuses and progress across endpoints
tasks_registry: Dict[str, Dict[str, Any]] = {}


def cleanup_old_files():
    """
    Scans working directories and permanently removes any files or
    folders that haven't been modified in the last 24 hours.
    """
    now = time.time()
    cutoff = now - (24 * 3600)  # 24 hours converted to seconds

    for folder in [TRANSLATED_DIR, TEMP_DIR, LOGS_DIR]:
        if not os.path.exists(folder):
            continue
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                # Check the last modification timestamp
                if os.path.getmtime(file_path) < cutoff:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to clean up old file/folder at {file_path}: {e}")


def run_translation_background(
    task_id: str, temp_file_path: str, src_lang: str, target_lang: str, title: str
):
    """
    Asynchronous worker task managed directly by FastAPI's BackgroundTasks.
    Fires up the NLLB model, tracks generator progress, and cleans up temp uploads.
    """
    # Safeguard filename format to avoid any path traversal issues
    safe_title = "".join(
        c for c in title if c.isalnum() or c in (" ", "_", "-")
    ).rstrip()
    output_filename = f"{safe_title}_{target_lang}.epub"
    output_path = os.path.join(TRANSLATED_DIR, output_filename)

    try:
        # Move state from PENDING to PROGRESS
        tasks_registry[task_id] = {"state": "PROGRESS", "progress": 0.0}

        # Instantiate and configure the ML translator engine
        translator = Translator(logs=True)
        translator.config(
            src_lang=src_lang,
            target_lang=target_lang,
            save_path=TRANSLATED_DIR,
            save_name=f"{safe_title}_{target_lang}",
            logs_path=LOGS_DIR,
        )

        # Stream and capture the incremental progress yield from the generator
        for progress in translator.translate_book_gen(temp_file_path):
            tasks_registry[task_id]["progress"] = progress

        # Mark as completely successful once the generator finishes execution
        tasks_registry[task_id] = {
            "state": "SUCCESS",
            "progress": 100.0,
            "output_path": output_path,
            "filename": output_filename,
        }

    except Exception as e:
        # Catch unexpected pipeline failures gracefully and log the state
        tasks_registry[task_id] = {
            "state": "FAILURE",
            "error": str(e),
            "progress": tasks_registry[task_id].get("progress", 0.0),
        }
    finally:
        # Guarantee removal of the raw uploaded file to optimize disk space
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as cleanup_err:
                print(
                    f"Failed to delete temporary file {temp_file_path}: {cleanup_err}"
                )


@app.post("/translate-book/")
async def translate_book(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    src_lang: str = Form(...),  # e.g., "eng_Latn"
    target_lang: str = Form(...),  # e.g., "pol_Latn"
    title: str = Form(...),  # User-defined book title for the output filename
):
    # Passively execute housecleaning on file age upon new submissions
    cleanup_old_files()

    # Generate a secure tracking hash for the user session
    task_id = str(uuid.uuid4())

    # Establish a temporary workspace file
    temp_filename = f"{task_id}_{file.filename}"
    temp_file_path = os.path.join(TEMP_DIR, temp_filename)

    # Stream the multipart upload data onto the storage volume
    with open(temp_file_path, "wb") as f:
        f.write(await file.read())

    # Map the task index inside our state tracking dictionary
    tasks_registry[task_id] = {"state": "PENDING", "progress": 0.0}

    # Delegate execution to FastAPI worker context without blocking request thread
    background_tasks.add_task(
        run_translation_background,
        task_id=task_id,
        temp_file_path=temp_file_path,
        src_lang=src_lang,
        target_lang=target_lang,
        title=title,
    )

    # Hand back the tracking reference key to the polling frontend app
    return {"task_id": task_id}


@app.get("/task-status/{task_id}")
def get_task_progress(task_id: str):
    # Routine passive cleanup execution
    cleanup_old_files()

    task = tasks_registry.get(task_id)

    if not task:
        return {"state": "NOT_FOUND", "progress": 0.0}

    if task["state"] == "PENDING":
        return {"state": "PENDING", "progress": 0.0}

    elif task["state"] == "PROGRESS":
        return {"state": "PROGRESS", "progress": task["progress"]}

    elif task["state"] == "SUCCESS":
        return {
            "state": "SUCCESS",
            "progress": 100.0,
            "output_path": task["output_path"],
            "filename": task["filename"],
        }

    elif task["state"] == "FAILURE":
        return {
            "state": "FAILURE",
            "error": task["error"],
        }

    return {"state": task["state"]}


@app.get("/download/{task_id}")
def download_translated(task_id: str):
    task = tasks_registry.get(task_id)

    if not task or task.get("state") != "SUCCESS":
        raise HTTPException(
            status_code=404, detail="File is not processed or job ID does not exist."
        )

    path = task.get("output_path", "")
    display_filename = task.get("filename", f"translated_{task_id}.epub")

    if os.path.exists(path):
        return FileResponse(
            path, media_type="application/epub+zip", filename=display_filename
        )

    raise HTTPException(
        status_code=404, detail="The file was missing from the server storage layer."
    )
