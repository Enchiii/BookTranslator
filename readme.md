# Book Translator

**Book Translator** is a command-line tool for translating `.epub` e-books into any language using Google's **Gemini 2.0 Flash** language model. It maintains the original HTML structure while providing high-quality translations with contextual understanding.

### Install dependencies: 
``` 
pip install -r requirements.txt 
```

### Configure the translation in `translator/config.py` (create this file if not exist):
```python
API_KEY = "YOUR_API_KEY"
```

### Run the translation:
```
python main.py
```

## 🛣️ Todo:

- 🌍 Web interface (backend + frontend)
- 🚀 Speed up translation
- 📂 Support for more file types: `.pdf`, `.txt`, `.docx`, `mobi` etc.
