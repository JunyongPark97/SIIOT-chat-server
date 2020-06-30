from django.db import models
from django.conf import settings

from datetime import timedelta, datetime


class Payment(models.Model):
    """
    유저 결제시 생성되는 모델입니다.
    여러개의 상품을 한번에 결제하면 하나의 Payment obj 가 생성됩니다.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='유저')
    receipt_id = models.CharField(max_length=100, verbose_name='영수증키', db_index=True)
    status = models.IntegerField(verbose_name='결제상태', default=0)

    price = models.IntegerField(verbose_name='결제금액', null=True)
    name = models.CharField(max_length=100, verbose_name='대표상품명')

    # bootpay data
    tax_free = models.IntegerField(verbose_name='면세금액', null=True)
    remain_price = models.IntegerField(verbose_name='남은금액', null=True)
    remain_tax_free = models.IntegerField(verbose_name='남은면세금액',null=True)
    cancelled_price = models.IntegerField(verbose_name='취소금액', null=True)
    cancelled_tax_free = models.IntegerField(verbose_name='취소면세금액', null=True)
    pg = models.TextField(default='inicis', verbose_name='pg사')
    method = models.TextField(verbose_name='결제수단')
    payment_data = models.TextField(verbose_name='raw데이터')
    requested_at = models.DateTimeField(blank=True, null=True)
    purchased_at = models.DateTimeField(blank=True, null=True)
    revoked_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return

    class Meta:
        managed = False
        db_table = 'payment_payment'


class Deal(models.Model):  # 돈 관련 (스토어 별로)
    """
    셀러별 한번에 결제를 구현하기 위해 만들었습니다.
    """

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='Deal_seller')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='Deal_buyer')

    payment = models.ForeignKey(Payment, null=True, blank=True, on_delete=models.SET_NULL)
    total = models.IntegerField(verbose_name='결제금액')
    remain = models.IntegerField(verbose_name='잔여금(정산금액)')  # 수수료계산이후 정산 금액., 정산이후는 0원, 환불시 감소 등.
    delivery_charge = models.IntegerField(verbose_name='배송비(참고)')
    status = models.IntegerField(db_index=True)
    is_settled = models.BooleanField(default=False, help_text="정산 여부(신중히 다뤄야 함)", verbose_name="정산여부(신중히)")

    transaction_completed_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'payment_deal'
