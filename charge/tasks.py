# from celery import shared_task
from utils.loggers import stdout_logger


# @shared_task
def task_set_charge_on_phone(phone_number, amount, currency):
    stdout_logger.info(f"Charged {phone_number} for {amount} {currency}")
