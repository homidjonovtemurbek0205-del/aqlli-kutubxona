from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name="Kitob nomi")
    author = models.CharField(max_length=255, default="Noma'lum", verbose_name="Muallif")
    genre = models.CharField(max_length=100, default="General", verbose_name="Janr")
    description = models.TextField(blank=True, null=True, verbose_name="Qisqacha tavsif")
    content = models.TextField(blank=True, null=True, verbose_name="Matn kontenti")
    file = models.FileField(upload_to="uploads/pdfs/", blank=True, null=True, verbose_name="PDF fayl")
    toc = models.JSONField(default=list, blank=True, null=True, verbose_name="Mundarija (TOC)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kitob"
        verbose_name_plural = "Kitoblar"
        ordering = ['-id']

    def __str__(self):
        return f"{self.title} - {self.author}"