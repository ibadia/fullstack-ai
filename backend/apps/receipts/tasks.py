from celery import shared_task
from .services import ReceiptService


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def process_receipt_task(self, receipt_id):
    try:
        service = ReceiptService(receipt_id=receipt_id)
        service.process_receipt()
    except Exception as exc:
        raise self.retry(exc=exc)