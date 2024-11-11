import os
from celery import Celery
import logging


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "almazgeobur_test.settings")
app = Celery("almazgeobur_test")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

LOG_FILE_PATH = 'logs/celery.log'
LOG_DIR = os.path.dirname(LOG_FILE_PATH)

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),  
        logging.StreamHandler()  
    ]
)