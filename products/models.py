from django.conf import settings
from django.db import models
from core.fields import S3ImageKeyField
from products.category.models import MixCategory, Size, Color, SecondCategory
from products.shopping_mall.models import ShoppingMall
from products.supplymentary.models import SizeCaptureImage, PurchasedTime, PurchasedReceipt
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from django.core.files.uploadedfile import InMemoryUploadedFile


def img_directory_path_profile(instance, filename):
    return 'user/{}/profile/{}'.format(instance.user.nickname, filename)


class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="products", on_delete=models.CASCADE)

    # receipt
    receipt = models.OneToOneField(PurchasedReceipt, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="products")

    # products condition
    UNOPENED = 1
    TEST = 2
    ONCETWICE = 3
    OVER = 4
    OTHER = 0
    CONDITION = (
        (UNOPENED, '미개봉'),
        (TEST, '시험 착용'),
        (ONCETWICE, '한두번 착용'),
        (OVER, '여러번 착용'),
        (OTHER, '기타'),
    )
    condition = models.IntegerField(choices=CONDITION)

    # shopping mall
    shopping_mall = models.ForeignKey(ShoppingMall, on_delete=models.CASCADE, related_name="products")

    # shop products url
    product_url = models.CharField(max_length=500, null=True, blank=True, help_text="추후 링크 없는 상품을 위해 null 가능 처리")

    # check url valid -> detail page 접속시 check 하여 save, 상세페이지 return 을 결정합니다.
    valid_url = models.BooleanField(default=True,
                                    help_text="링크 유효성 검증을 위해 사용합니다. 링크가 내려간 경우 False,"
                                              "(나중)링크 없는 상품 업로드시 False로서, False 인 경우 임시 페이지를 보여줍니다.")

    temp_save = models.BooleanField(default=True, help_text="임시저장 중인 상품을 확인하기 위해 만들었습니다. upload complete = False")

    # crawl products id
    crawl_product_id = models.IntegerField(null=True, blank=True)

    # user input data
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='상품명',
                            help_text="쇼핑몰 상품명과 다르게 저장하기 위해 사용")
    price = models.IntegerField(null=True, blank=True, verbose_name='가격')
    content = models.TextField(null=True, blank=True, verbose_name="설명")
    free_delivery = models.BooleanField(default=False, help_text="무료배송 여부")

    # category
    category = models.ForeignKey(SecondCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                 help_text="카테고리 참고 모델입니다. SecondCategory만 참고합니다.")
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')

    # size capture
    size_capture = models.ForeignKey(SizeCaptureImage, on_delete=models.SET_NULL, null=True, blank=True)

    # 구매 시기
    purchased_time = models.ForeignKey(PurchasedTime, on_delete=models.CASCADE, null=True, blank=True)

    # 업로드 가능 여부 (모든 정보 입력시 True)
    possible_upload = models.BooleanField(default=False,
                                          help_text="업로드 가능성 여부입니다. True 이면 main에 노출됩니다."
                                                    "운영진이 직접 올릴 때 사용합니다.")
    # 끌올 (optional)
    refresh_date = models.DateTimeField(null=True, blank=True,
                                        help_text="끌어올리기 기능을 구현하기 위해 사용합니다. 하루에 1번 제한 등을 위해 참고합니다.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True, help_text="상품 삭제시 False")

    def __str__(self):
        if self.temp_save:
            if self.receipt:
                return '[업로드 요청]' + self.name
            if self.name:
                return '[임시 저장]' + self.name
            else:
                return '[임시 저장 (상품명 미입력)]'
        else:
            if self.name:
                return '[업로드]' + self.name
        return ''

    class Meta:
        managed = False
        db_table = 'products_product'


class ProductStatus(models.Model):
    # sold 처리 주체 : by 결제, by seller -> 이 경우 다시 sold 해제 가능
    SOLD_STATUS = [
        (1, 'by payment'),
        (2, 'by seller')
    ]

    sold = models.BooleanField(default=False, verbose_name='판매여부')
    sold_status = models.IntegerField(choices=SOLD_STATUS, null=True, blank=True, verbose_name='판매 과정')

    product = models.OneToOneField(Product, related_name='status', on_delete=models.CASCADE)
    editing = models.BooleanField(default=False, help_text="판매자가 상품 정보를 수정시 True 입니다. 결제가 되지 않도록 해야합니다.")

    purchasing = models.BooleanField(default=False, help_text='구매중일 경우 True 입니다. 다른 유저 결제가 되지 않도록 해야합니다.')

    hiding = models.BooleanField(default=False, help_text="숨기기 기능을 구현하기 위해 만들었습니다. True 이면 숨김 처리가 됩니다.")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        managed = False
        db_table = 'products_productstatus'


class ProductImages(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image_key = S3ImageKeyField()

    class Meta:
        managed = False
        db_table = 'products_productimages'


def thumb_directory_path(instance, filename):
    return 'user/{}/products/thumbnail_{}'.format(instance.product.seller.id, filename)


class ProdThumbnail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    # image_key = S3ImageKeyField() # client key 저장 후 save 시 image 저장
    thumbnail = ProcessedImageField(
        upload_to=thumb_directory_path,  # 저장 위치
        processors=[ResizeToFill(350, 350)],  # 사이즈 조정
        format='JPEG',  # 최종 저장 포맷
        options={'quality': 90},
        null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'products_prodthumbnail'


class ProductViews(models.Model):
    product = models.OneToOneField(Product, related_name='views', on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'products_productviews'


class ProductLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='liker', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='liked', on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        managed = False
        db_table = 'products_productlike'