# Book Translator

**Book Translator** is a tool designed for translating `.epub` e-books into any language using Google's powerful **Gemini 2.0 Flash** language model. It offers both a convenient web interface and a command-line option, preserving the original HTML structure and delivering high-quality, contextually aware translations.

---

## 🌐 Web Interface (Recommended)

Experience a user-friendly web application for seamless e-book translation.

### 🚀 Setup and Run

#### 1. Backend

The backend handles the translation logic and API.

* **Navigate to the backend directory:**
    ```
    cd backend
    ```
* **Install Python dependencies:**
    ```
    pip install -r requirements.txt
    ```
  
* **Configure the translation in `backend/translator/config.py` (create this file if not exist):**
    ```
    API_KEY = "YOUR_API_KEY"
    ```

* **Configure `REDIS_URL`:**
    The backend uses Redis for task queuing with Celery. You'll need to configure your Redis server URL.
    Create a file named `config.py` inside the `backend/` directory (if it doesn't exist) and set your `REDIS_URL`:
    ```
    # backend/config.py
    REDIS_URL = "redis://localhost:6379/0" # Default local Redis URL
    ```
    You can install Redis locally (e.g., via Docker Compose or directly), use a local alternative, or opt for an online service. For cloud-based Redis services like [Upstash](https://upstash.com/), your URL might look something like this:
    ```
    redis://default:<password>@<hostname>.upstash.io:<port>
    ```

* **Run Backend Services:**
    You'll need two separate terminals for these processes:

    **a) FastAPI Server:**
    ```
    uvicorn main:app --reload
    ```

    **b) Celery Worker:**
    ```
    celery -A tasks.celery_app worker --loglevel=info
    ```
  

#### 2. Frontend

The frontend provides the user interface.

* **Navigate to the frontend directory:**
    ```
    cd frontend
    ```

* **Install Node.js dependencies:**
    ```
    npm install
    ```

* **Run the development server:**
    ```
    npm run dev
    ```
    Your web interface should now be accessible in your browser (usually at `http://localhost:5173/` or similar).

---

## 🖥️ Command-Line Interface (CLI) Version

For users who prefer a console-based approach.

### Install dependencies:
```
pip install -r requirements.txt
```
### Configure the translation in `backend/translator/config.py` (create this file if not exist):
```python
API_KEY = "YOUR_API_KEY"
```
### Run the translation:
```
python main.py
```


## 🛣️ Todo:
- 🚀 Automated translated books clearing cache
- 📂 Support for more file types: `.pdf`, `.txt`, `.docx`, `mobi` etc.
- Option to download logs
- Saving translating progress and continuing from this point
- Download history

