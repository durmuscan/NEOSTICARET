from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
# Create your models here.


class Kategori(models.Model):

    isim = models.CharField(max_length=100)

    def __str__(self):
        return self.isim


class SeriNo(models.Model):
    no = models.CharField(max_length=100)

    def __str__(self):
        return self.no


class AltKategori(models.Model):
    isim = models.CharField(max_length=100)

    def __str__(self):
        return self.isim


class Urun(models.Model):
    kategori = models.ForeignKey(
        Kategori, on_delete=models.SET_NULL, null=True)
    seri_no = models.OneToOneField(
        SeriNo, on_delete=models.CASCADE, null=True, blank=True)
    altKategori = models.ManyToManyField(AltKategori, blank=True)
    isim = models.CharField(max_length=100)
    acıklama = RichTextField(max_length=500)
    fiyat = models.IntegerField()
    resim = models.FileField(upload_to='urunler/', null=True)

    def __str__(self):
        return self.isim


class Sepet(models.Model):
    ekleyen = models.ForeignKey(User, on_delete=models.CASCADE)
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE)
    adet = models.IntegerField()
    total = models.IntegerField()
    odendiMi = models.BooleanField(default=False)

    def __str__(self):
        return self.ekleyen.username


class Odeme(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    urunler=models.ManyToManyField(Urun)
    total=models.IntegerField()
    odendiMi=models.BooleanField(default=False)
    odeme_tarih=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username