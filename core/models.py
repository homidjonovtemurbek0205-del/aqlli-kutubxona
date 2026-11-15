from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

<<<<<<< HEAD

class UserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError('Email kiritilishi shart')

        email = self.normalize_email(email)
        username = username or email.split('@', 1)[0]
        if not username:
            raise ValueError('Username kiritilishi shart')

        extra_fields.setdefault('username', username)
        user = self.model(email=email, **extra_fields)

        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()

=======
class UserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Email kiritilishi shart")
        email = self.normalize_email(email)
        if not username:
            username = email.split('@')[0]
        extra_fields.setdefault('username', username)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
>>>>>>> abd65b8 (yana)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
<<<<<<< HEAD
            raise ValueError('Superuser is_staff=True bo\'lishi kerak.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser is_superuser=True bo\'lishi kerak.')

        extra_fields.setdefault('username', email.split('@', 1)[0])
=======
            raise ValueError("Superuser is_staff=True bo'lishi kerak.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser is_superuser=True bo'lishi kerak.")

>>>>>>> abd65b8 (yana)
        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
<<<<<<< HEAD
    email = models.EmailField(unique=True, verbose_name='Email manzili')
=======
    email = models.EmailField(unique=True, verbose_name="Email manzili")
>>>>>>> abd65b8 (yana)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
<<<<<<< HEAD
        blank=True,
=======
        blank=True
>>>>>>> abd65b8 (yana)
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
<<<<<<< HEAD
        blank=True,
=======
        blank=True
>>>>>>> abd65b8 (yana)
    )

    def __str__(self):
        return self.email


class Book(models.Model):
<<<<<<< HEAD
    title = models.CharField(max_length=255, verbose_name='Kitob nomi')
    author = models.CharField(max_length=255, default="Noma'lum", verbose_name='Muallif')
    genre = models.CharField(max_length=100, default='PDF', verbose_name='Janr')
    description = models.TextField(blank=True, null=True, verbose_name='Qisqacha tavsif')
    content = models.TextField(blank=True, null=True, verbose_name='Matn kontenti')
    file = models.FileField(upload_to='books/', null=True, blank=True)
    toc = models.JSONField(default=list, blank=True, null=True, verbose_name='Mundarija')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kitob'
        verbose_name_plural = 'Kitoblar'
        ordering = ['-id']

    def __str__(self):
        return self.title
=======
    title = models.CharField(max_length=255, verbose_name="Kitob nomi")
    author = models.CharField(max_length=255, default="Noma'lum", verbose_name="Muallif")
    genre = models.CharField(max_length=100, default="PDF", verbose_name="Janr")
    description = models.TextField(blank=True, null=True, verbose_name="Qisqacha tavsif")
    content = models.TextField(blank=True, null=True, verbose_name="Matn kontenti")
    file = models.FileField(upload_to='books/', null=True, blank=True, verbose_name="PDF fayli")
    audio_file = models.FileField(upload_to='audio/', null=True, blank=True, verbose_name="Audio kitob fayli")
    audiobook_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Audio kitob havolasi")
    toc = models.JSONField(default=list, blank=True, null=True, verbose_name="Mundarija")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def has_audio(self):
        return bool(self.audio_file or self.audiobook_url)


    class Meta:
        verbose_name = "Kitob"
        verbose_name_plural = "Kitoblar"
        ordering = ['-id']

    def __str__(self):
        return self.title
>>>>>>> abd65b8 (yana)
