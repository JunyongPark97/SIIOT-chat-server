import string

import random

from django.conf import settings
from django.db import models
from core.fields import S3ImageKeyField


PRECISION = 4
THRESHOLD = 0.1 ** PRECISION
CANDIDATES_COUNT = 100


def img_directory_path_size_crop_image(instance, filename):
    return 'size_capture/crawl_id/{}/{}'.format(instance.crawl_product_id, filename)


def get_box_filename():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12)) + '.jpg'


class SizeCaptureImage(models.Model):
    """
    Size 정보 캡쳐 저장하는 모델입니다.
    user 가 링크 업로드 시 비동기로 사이즈 캡쳐 저장해 놓습니다.
    이후 사이즈 크롭 시 client 에서 보내준 ltrb 정보를 가지고 user_crop_image를 생성하며,
    유저가 사이즈 캡쳐 수정 클릭시 ltrb정보와 같이 server_capture_image를 return 합니다.
    또한 crawl_product_id를 활용하여 이미 사이즈 캡쳐가 되어있는 상품의 경우 자동으로 사이즈 image를 return 합니다.
    """
    left = models.DecimalField(null=True, blank=True, max_digits=PRECISION + 1, decimal_places=PRECISION)
    top = models.DecimalField(null=True, blank=True, max_digits=PRECISION + 1, decimal_places=PRECISION)
    right = models.DecimalField(null=True, blank=True, max_digits=PRECISION + 1, decimal_places=PRECISION)
    bottom = models.DecimalField(null=True, blank=True, max_digits=PRECISION + 1, decimal_places=PRECISION)

    crawl_product_id = models.IntegerField(null=True, blank=True)

    server_capture_image = S3ImageKeyField()
    user_crop_image = models.ImageField(null=True, blank=True, upload_to=img_directory_path_size_crop_image)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'supplymentary_sizecaptureimage'


class PurchasedReceipt(models.Model):
    """
    유저가 구매내역 업로드를 선택했을 때 해당 모델을 사용하여 이미지를 저장합니다.
    S#ImageKeyField()를 사용할 때, uuid를 미리 저장 해 두고 client에게 전달하는 게 좋을 듯 합니다?
    """
    receipt_image_key = S3ImageKeyField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'supplymentary_purcahsedreceipt'


class ShoppingMallAddRequest(models.Model):
    """
    유저가 쇼핑몰 추가 요청 시 생성됩니다.
    생성 시 slack 연동을 하여 운영진이 알 수 있도록 합니다.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shop_add_reqs")
    shoppingmall_name = models.CharField(max_length=100)
    is_completed = models.BooleanField(default=False, help_text="크롤링 코드를 완성 후 True로 변환 시 요청한 유저에게 알림(or 알림톡)")
    completed_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'supplymentary_shoppingmalladdrequest'


class PurchasedTime(models.Model):
    year = models.PositiveIntegerField(null=True, blank=True)
    month = models.PositiveIntegerField(null=True, blank=True)
    week = models.PositiveIntegerField(null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True, help_text="현재 사용하지 않는 정확한 날짜 필드입니다.")

    class Meta:
        managed = False
        db_table = 'supplymentary_purchasedtime'

