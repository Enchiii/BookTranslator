import re
from ebooklib import epub
from .log_type import LogType
from bs4 import BeautifulSoup


def write_logs(path:  str, log_type: LogType, msg: str):
    name = ""
    match log_type:
        case LogType.NORMAL:
            name = "translation_logs"
        case LogType.WARNING:
            name = "warning_logs"
        case LogType.ERROR:
            name = "error_logs"
        case LogType.TIME:
            name = "time_logs"

    with open(f"{path}/{name}", "a", encoding="utf-8") as f:
        f.write(f"\n{'*' * 40}\n")
        f.write(msg)
        f.write(f"\n{'*' * 40}\n")


def validate_book(book: epub.EpubBook, logs_path: str = "./logs") -> bool:
    valid = True
    for i, item in enumerate(book.get_items()):
        if item.get_type() == 9:  # HTML
            html = item.get_content().decode("utf-8", errors="ignore")
            try:
                soup = BeautifulSoup(html, "html.parser")
                if not soup or not soup.html:
                    raise ValueError("HTML root missing")
            except Exception as e:
                valid = False
                write_logs(logs_path, LogType.ERROR, f"❌ Invalid HTML in {item.file_name}: {e}")
    return valid


def extract_first_sentence(html: str) -> str:
    text = re.sub(r'<[^>]+>', '', html)
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return sentences[0] if sentences else ""


def extract_last_sentence(html: str) -> str:
    text = re.sub(r'<[^>]+>', '', html)
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return sentences[-1] if sentences else ""


def build_prompt(target_lang: str, context_before: str, html_chunk: str, context_after: str) -> str:
    return (
            f"Translate the following HTML fragment into {target_lang}.\n\n"

            "🛑 Do NOT modify the HTML structure in any way:\n"
            "- Do NOT add, remove, or change any HTML tags or attributes.\n"
            "- Keep all HTML entities (e.g., &nbsp;, &amp;, &lt;) exactly as they are.\n"
            "- Do NOT wrap your answer in code blocks (e.g., no triple backticks ```).\n"

            "📝 Translate ONLY the human-visible **text content** between HTML tags.\n"
            "- Leave all HTML tags and attributes untouched.\n"
            "- If there is no translatable text in the fragment, return it unchanged.\n"

            "🧠 Maintain context and consistency:\n"
            f"- Use the previous and next context to guide your translation and ensure coherence.\n"
            f"- Do NOT translate names of people, places, or fictional entities unless a well-known {target_lang} equivalent exists.\n\n"

            f"Context before:\n{context_before}\n\n"
            f"🔽 HTML fragment to translate (only translate the visible text):\n{html_chunk}\n\n"
            f"Context after:\n{context_after}\n\n"

            "✅ Final output: ONLY the translated HTML fragment with the original structure preserved. DO NOT include any explanation, markdown formatting, or comments."
        )


def split_html_into_chunks(html: str, max_input_chars: int) -> list[str]:
    chunks = []
    current_chunk = ""
    tokens = re.split(r"(\s+|<[^>]+>)", html)

    for token in tokens:
        if token is None:
            continue
        if len(current_chunk) + len(token) > max_input_chars:
            chunks.append(current_chunk)
            current_chunk = token
        else:
            current_chunk += token

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
