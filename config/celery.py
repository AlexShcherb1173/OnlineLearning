from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("onlinelearning")

# Берём настройки Celery из Django settings с префиксом CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически ищем tasks.py во всех приложениях из INSTALLED_APPS
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
