import os
import ssl

from celery import Celery
from translator import Translator
from config import REDIS_URL

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

ssl_options = {"ssl_cert_reqs": ssl.CERT_NONE}

celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    broker_use_ssl=ssl_options,
    redis_backend_use_ssl=ssl_options,
)


@celery_app.task(bind=True)
def translate_epub_task(
    self,
    epub_path,
    language,
    api_key,
    max_input_tokens,
    max_output_tokens,
    max_requests_per_minute,
    max_tokens_per_minute,
    output_dir,
    logs_dir
):
    output_path = os.path.join(output_dir, f"{self.request.id}.epub")
    translator = Translator()
    translator.set_target_lang(language)
    translator.set_api_key(api_key)
    translator.set_logs_path(logs_dir)
    translator.set_save_path(output_dir)
    translator.set_save_name(self.request.id)
    translator.config(max_input_tokens=max_input_tokens, max_output_tokens=max_output_tokens,
                      max_requests_per_minute=max_requests_per_minute, max_tokens_per_minute=max_tokens_per_minute)
    for progress in translator.translate_book_gen(epub_path):
        self.update_state(
            state='PROGRESS',
            meta={'progress': progress}
        )

    os.remove(epub_path)

    return {'status': 'done', 'output_path': output_path}
