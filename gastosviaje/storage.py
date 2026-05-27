from django.conf import settings
from django.core.files.storage import default_storage


def build_expense_voucher_photo_storage():
    from storages.backends.s3boto3 import S3Boto3Storage

    class ExpenseVoucherPhotoStorage(S3Boto3Storage):
        bucket_name = settings.GASTOS_VIAJE_R2_BUCKET_NAME

    return ExpenseVoucherPhotoStorage()


def get_expense_voucher_photo_storage():
    if getattr(settings, "USE_R2_STORAGE", False):
        return build_expense_voucher_photo_storage()
    return default_storage
