from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from django.contrib.auth.models import PermissionsMixin


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, password, phone, **kwargs):
        if not phone:
            raise ValueError('핸드폰 번호를 입력해주세요')
        user = self.model(phone=phone, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **kwargs):
        kwargs.setdefault('is_staff', False)
        kwargs.setdefault('is_superuser', False)
        return self._create_user(password, phone, **kwargs)

    def create_superuser(self, password, phone, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError('superuser must have is_staff=True')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('superuser must have is_superuser=True')
        return self._create_user(password, phone, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    # username = None
    nickname = models.CharField(max_length=30, unique=True, null=True, blank=True, verbose_name='nickname')
    phone = models.CharField(max_length=20, blank=True, null=True,
                             help_text="탈퇴 후 재 가입 시 같은 번호로 사용할 수 있으므로 unique 설정하지 않음")
    uid = models.UUIDField(unique=True, null=True, blank=True, help_text="phone 대신 USERNAME_FIELD를 대체할 field입니다.")
    USERNAME_FIELD = 'uid'
    REQUIRED_FIELDS = ['phone']

    objects = UserManager()
    is_active = models.BooleanField(default=True, help_text="탈퇴/밴 시 is_active = False")
    is_banned = models.BooleanField(default=False, help_text="밴 여부")
    is_staff = models.BooleanField(default=False, help_text="super_user와의 권한 구분을 위해서 새로 만들었습니다. 일반적 운영진에게 부여됩니다.")

    created_at = models.DateTimeField(auto_now_add=True)
    quit_at = models.DateTimeField(blank=True, null=True, default=None)

    email = models.EmailField(max_length=100, unique=True, db_index=True, blank=True, null=True,
                              help_text="운영진 staff page에서 로그인 시 사용합니다.")

    def __str__(self):
        if self.is_anonymous:
            return 'anonymous'
        if self.is_staff:
            return '[staff] {}'.format(self.email)
        if self.nickname:
            return self.nickname
        return self.phone

    class Meta:
        managed = False
        db_table = 'accounts_user'
