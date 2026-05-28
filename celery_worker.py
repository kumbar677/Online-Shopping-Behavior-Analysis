import os
from celery import Celery

# Instantiate explicitly configured message broker routing natively
REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
celery = Celery(
    'data_ingestion',
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Structuring explicit fallback matrix for OS isolation limits
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_pool='gevent', # Safe fallback structurally overriding standard threading blocks
    task_always_eager=True # Always run synchronously/eagerly in local development without Redis
)

@celery.task(name="process_dataset_upload", bind=True)
def process_dataset_upload_task(self, users_path, products_path, orders_path, business_id, dataset_id, clear_data, column_mappings=None):
    """
    How Celery handles background jobs:
    This task executes outside the main Flask web server thread. It prevents 
    the UI from freezing while processing massive 10 Lakh row datasets.
    It relies on Redis to queue tasks.
    In local eager mode, it executes immediately and transparently.
    """
    from data_import import process_multi_upload
    return process_multi_upload(users_path, products_path, orders_path, business_id, dataset_id, clear_data, column_mappings)
