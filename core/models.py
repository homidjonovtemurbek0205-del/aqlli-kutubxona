from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email kiritilishi shart")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Email manzil")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name="Kitob nomi")
    author = models.CharField(max_length=255, default="Noma'lum", verbose_name="Muallif")
    genre = models.CharField(max_length=100, default="PDF", verbose_name="Janr")
    description = models.TextField(blank=True, null=True, verbose_name="Qisqacha tavsif")
    content = models.TextField(blank=True, null=True, verbose_name="Matn kontenti")
    file = models.FileField(upload_to="uploads/pdfs/", verbose_name="Asl PDF fayl")
    toc = models.JSONField(default=list, blank=True, null=True, verbose_name="Mundarija")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kitob"
        verbose_name_plural = "Kitoblar"
        ordering = ['-id']

    def __str__(self):
        return self.title