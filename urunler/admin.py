from django.contrib import admin
from .models import *
# Register your models here.


class SepetAdmin(admin.ModelAdmin):
    list_display = ['ekleyen', 'urun', 'adet', 'total', 'odendiMi']
    list_filter=['ekleyen', 'urun', 'odendiMi']


admin.site.register(Kategori)
admin.site.register(Urun)
admin.site.register(SeriNo)
admin.site.register(AltKategori)
admin.site.register(Sepet, SepetAdmin)
admin.site.register(Odeme)