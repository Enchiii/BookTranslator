import re

from bs4 import BeautifulSoup, Comment
from ebooklib import epub

from .log_type import LogType


def write_logs(path: str, log_type: LogType, msg: str):
    name = ""
    match log_type:
        case LogType.NORMAL:
            name = "translation_logs.txt"
        case LogType.WARNING:
            name = "warning_logs.txt"
        case LogType.ERROR:
            name = "error_logs.txt"
        case LogType.TIME:
            name = "time_logs.txt"

    with open(f"{path}/{name}", "a", encoding="utf-8") as f:
        f.write(f"\n{'*' * 40}\n")
        f.write(msg)
        f.write(f"\n{'*' * 40}\n")


def validate_book(book: epub.EpubBook, logs_path: str = "./logs") -> bool:
    valid = True
    for _, item in enumerate(book.get_items()):
        if item.get_type() == 9:  # HTML
            raw_content = item.get_content()
            html = (
                raw_content.decode("utf-8", errors="ignore")
                if isinstance(raw_content, bytes)
                else str(raw_content)
            )

            try:
                soup = BeautifulSoup(html, "html.parser")
                if not soup or not soup.html:
                    raise ValueError("HTML root missing")
            except Exception as e:
                valid = False
                write_logs(
                    logs_path,
                    LogType.ERROR,
                    f"❌ Invalid HTML in {item.file_name}: {e}",
                )
    return valid


def translate_html_soup(
    html_content: str, translate_func, logs_path: str, logs: bool
) -> str:
    soup = BeautifulSoup(html_content, "html.parser")

    # Przeszukujemy absolutnie WSZYSTKIE węzły tekstowe w dokumencie.
    # Dzięki temu nie ominie nas żaden zapomniany tag <a> czy rzadki element struktury.
    text_nodes = soup.find_all(text=True)

    for node in text_nodes:
        # Pomijamy komentarze HTML, skrypty JS oraz style CSS wewnątrz dokumentu
        if isinstance(node, Comment) or node.parent.name in [
            "script",
            "style",
            "head",
            "title",
            "meta",
        ]:
            continue

        text_content = str(node).strip()

        # Ignorujemy całkowicie puste fragmenty tekstu
        if not text_content:
            continue

        # --- BLOKADA HALUCYNACJI "SAMOCHÓD" (Dla liczb i znaków) ---
        # Jeśli tekst to tylko cyfry, rzymskie liczby (np. I, II, X, v) lub pojedyncze znaki,
        # zostawiamy go w oryginale. Model NLLB na 95% zrobiłby tu halucynację.
        if (
            re.match(r"^\d+$", text_content)
            or re.match(r"^[IVXLCDMivxlcdm]+$", text_content)
            or len(text_content) < 2
        ):
            continue

        try:
            # Wykonujemy paczkowane, bezpieczne tłumaczenie fragmentu tekstu
            translated_text = translate_func(text_content)

            # --- UNIWERSALNA BLOKADA HALUCYNACJI DLA KAŻDEGO JĘZYKA ---
            lower_trans = translated_text.lower()

            # Sprawdzamy, czy w tłumaczeniu pojawił się niesławny kaprys modelu NLLB
            if "samochód" in lower_trans or "auto" in lower_trans:
                orig_len = len(text_content)
                trans_len = len(translated_text)

                # Jeśli tekst źródłowy był krótki, a tłumaczenie urosło ponad 2-krotnie,
                # to matematyczny dowód na to, że model "wymyślił" słowo samochód z niczego.
                if orig_len < 15 and trans_len > (orig_len * 2):
                    if logs:
                        from .log_type import LogType
                        from .utils import write_logs

                        write_logs(
                            logs_path,
                            LogType.WARNING,
                            f"⚠️ Zablokowano wielojęzyczną halucynację: '{text_content}' -> '{translated_text}'",
                        )
                    continue  # Odrzucamy to tłumaczenie, zostawiając bezpieczny oryginał

            # Jeśli wszystko jest w porządku, podmieniamy tekst w strukturze DOM książki
            node.replace_with(translated_text)

            if logs:
                from .log_type import LogType
                from .utils import write_logs

                write_logs(
                    logs_path,
                    LogType.NORMAL,
                    f"Original text: {text_content}\nTranslated: {translated_text}",
                )

        except Exception as e:
            if logs:
                from .log_type import LogType
                from .utils import write_logs

                write_logs(
                    logs_path,
                    LogType.ERROR,
                    f"Error replacing HTML node: {e}\nText: {text_content}",
                )

    return str(soup)
