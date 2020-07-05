from django.conf import settings
from django.db import models


class UserWebSocketActivity(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                primary_key=True)
    active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)