from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):

    def create_user(self, user_email, password, user_id, user_img, user_name, auth, **extra_fields):
        if not user_email:
            raise ValueError('user_id Required!')

        user = self.model(
            user_id=user_id,
            user_email=user_email,
            user_img = user_img,
            user_name =user_name,
            auth = auth,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_email, password, user_id=None, user_img=None, user_name=None, auth=None):

        user = self.create_user(user_email, password, user_id, user_img, user_name, auth)

        user.is_superuser = True
        user.is_staff = True
        user.is_admin = True
        user.level = 0

        user.save(using=self._db)
        return user



class User(AbstractBaseUser):
    user_email = models.EmailField(verbose_name='user_email',max_length=255, unique=True)
    password = models.CharField(max_length=256)
    user_id = models.CharField(max_length=24, unique=True)
    user_img = models.ImageField(upload_to="users/", default='basic_user.png',blank=True)
    user_name = models.CharField(max_length=24,blank=True, null=True)
    auth = models.CharField(max_length=10, verbose_name="인증번호", null=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()


    USERNAME_FIELD = 'user_email'  # user_email
    REQUIRED_FIELDS = ['user_id']  # 필수로 받고 싶은 필드들 넣기 원래 소스 코드엔 email필드가 들어가지만 우리는 로그인을 이메일로

    def __str__(self): # 관리자 페이지에 보여줄 필드
        return self.user_email

class Follow(models.Model):
    follower = models.EmailField(max_length=255)
    following = models.EmailField(max_length=255)
    active = models.BooleanField(default=False)

