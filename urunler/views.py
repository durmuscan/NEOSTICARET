from django.shortcuts import render, redirect
from .models import *
from django.db.models import Q
from .forms import *
from django.contrib import messages
# Create your views here.
import iyzipay
import json
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import requests
import pprint
from django.core.cache import cache
# canlıya alındığında hepsinin başındaki sandbox- kısmı silinecek
api_key = 'sandbox-KI6CjrzdwUzPEE87v8QIcyaOIQ8FCQGi'
secret_key = 'sandbox-hwiwguARFWGSiNRD1TwpOeK7NnKyKC7Q'
base_url = 'sandbox-api.iyzipay.com'


options = {
    'api_key': api_key,
    'secret_key': secret_key,
    'base_url': base_url
}
sozlukToken = list()


def index(request):
    context = dict()

    context['message'] = 'Django ile Iyzico Ödeme Entegrasyonu'

    template = 'index.html'
    return render(request, template, context)


def payment(request):
    context = dict()
    kullanici = request.user
    odeme = Odeme.objects.get(user=kullanici, odendiMi=False)
    fiyat = odeme.total
    buyer = {
        'id': 'BY789',
        'name': kullanici.username,
        'surname': 'Doe',
        'gsmNumber': '+905350000000',
        'email': 'email@email.com',
        'identityNumber': '74300864791',
        'lastLoginDate': '2015-10-05 12:43:35',
        'registrationDate': '2013-04-21 15:12:09',
        'registrationAddress': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'ip': '85.34.78.112',
        'city': 'Istanbul',
        'country': 'Turkey',
        'zipCode': '34732'
    }

    address = {
        'contactName': 'Jane Doe',
        'city': 'Istanbul',
        'country': 'Turkey',
        'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'zipCode': '34732'
    }

    basket_items = [
        {
            'id': 'BI101',
            'name': 'Binocular',
            'category1': 'Collectibles',
            'category2': 'Accessories',
            'itemType': 'PHYSICAL',
            'price': '0.3'
        },
        {
            'id': 'BI102',
            'name': 'Game code',
            'category1': 'Game',
            'category2': 'Online Game Items',
            'itemType': 'VIRTUAL',
            'price': '0.5'
        },
        {
            'id': 'BI103',
            'name': 'Usb',
            'category1': 'Electronics',
            'category2': 'Usb / Cable',
            'itemType': 'PHYSICAL',
            'price': '0.2'
        }
    ]

    request = {
        'locale': 'tr',
        'conversationId': '123456789',
        'price': '1',
        'paidPrice': int(fiyat),
        'currency': 'TRY',
        'basketId': 'B67832',
        'paymentGroup': 'PRODUCT',
        "callbackUrl": "http://127.0.0.1:8000/result/",
        "enabledInstallments": ['2', '3', '6', '9'],
        'buyer': buyer,
        'shippingAddress': address,
        'billingAddress': address,
        'basketItems': basket_items,
        # 'debitCardAllowed': True
    }

    checkout_form_initialize = iyzipay.CheckoutFormInitialize().create(request, options)

    # print(checkout_form_initialize.read().decode('utf-8'))
    page = checkout_form_initialize
    header = {'Content-Type': 'application/json'}
    content = checkout_form_initialize.read().decode('utf-8')
    json_content = json.loads(content)
    print(type(json_content))
    print(json_content["checkoutFormContent"])
    print("************************")
    token = json_content['token']
    cache.set('token', token)
    print(json_content["token"])
    print("************************")
    sozlukToken.append(json_content["token"])
    return HttpResponse(f'<div id="iyzipay-checkout-form" class="popup">{json_content["checkoutFormContent"]}</div>')


@require_http_methods(['POST'])
@csrf_exempt
def result(request):
    context = dict()

    url = request.META.get('index')
    token = cache.get('token')
    request = {
        'locale': 'tr',
        'conversationId': '123456789',
        'token':token
    }
    checkout_form_result = iyzipay.CheckoutForm().retrieve(request, options)
    print("************************")
    print(type(checkout_form_result))
    result = checkout_form_result.read().decode('utf-8')
    print("************************")
    print(sozlukToken[0])   # Form oluşturulduğunda
    print("************************")
    print("************************")
    sonuc = json.loads(result, object_pairs_hook=list)
    # print(sonuc[0][1])  # İşlem sonuç Durumu dönüyor
    # print(sonuc[5][1])   # Test ödeme tutarı
    print("************************")
    for i in sonuc:
        print(i)
    print("************************")
    print(sozlukToken)
    print("************************")
    if sonuc[0][1] == 'success':
        context['success'] = 'Başarılı İŞLEMLER'
        return HttpResponseRedirect(reverse('success'), context)

    elif sonuc[0][1] == 'failure':
        context['failure'] = 'Başarısız'
        return HttpResponseRedirect(reverse('failure'), context)

    return HttpResponse(url)


def success(request):
    odeme = Odeme.objects.get(user=request.user, odendiMi=False)
    odeme.odendiMi = True
    odeme.save()
    sepetim = Sepet.objects.filter(ekleyen=request.user, odendiMi=False)
    for i in sepetim:
        i.odendiMi = True
        i.save()
    messages.success(request, 'Ödeme başarılı')
    return redirect('index')


def fail(request):
    messages.error(request, 'Ödeme başarısız Tekrar deneyin')
    return redirect('sepetim')


def index(request):
    urunler = Urun.objects.all()
    search = ''
    if request.GET.get('search'):
        search = request.GET.get('search')
        urunler = Urun.objects.filter(
            Q(isim_icontains=search) |
            Q(kategori__isim__icontains=search)
        )
    if request.method == 'POST':
        if request.user.is_authenticated:
            urunId = request.POST['urunId']
            adet = request.POST['adet']
            urunum = Urun.objects.get(id=urunId)
            if Sepet.objects.filter(ekleyen=request.user, urun=urunum, odendiMi=False).exists():
                sepet = Sepet.objects.get(
                    ekleyen=request.user, urun=urunum, odendiMi=False)
                sepet.adet += int(adet)
                sepet.total = urunum.fiyat*sepet.adet
                sepet.save()
            else:
                sepet = Sepet.objects.create(
                    ekleyen=request.user,
                    urun=urunum,
                    adet=adet,
                    total=urunum.fiyat*int(adet)
                )
            sepet.save()
        else:
            messages.warning(request, 'Giriş yapınız')
            return redirect('login')
        return redirect('index')
    context = {
        'urunler': urunler,
        'search': search
    }
    return render(request, 'index.html', context)


def urun(request, urunId):
    urunum = Urun.objects.get(id=urunId)
    context = {
        'urun': urunum
    }
    return render(request, 'detail.html', context)


def olustur(request):
    # kategoriler = Kategori.objects.all()
    # if request.method == 'POST':
    #     resim = request.FİLES['resim']
    #     isim = request.POST['isim']
    #     aciklama = request.POST['aciklama']
    #     fiyat = request.POST['fiyat']
    #     kategori=request.POST['kategori']
    #     urun = Urun.objects.create(
    #         kategori__id=kategori,
    #         isim=isim,
    #         aciklama=aciklama,
    #         fiyat=fiyat,
    #         resim=resim
    #     )
    #     urun.save()
    #     print("Ürün Oluşturuldu")
    #     return redirect('olustur')
    form = UrunForm()
    if request.method == 'POST':
        form = UrunForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index.html')
    context = {
        # 'kategoriler': kategoriler
        'form': form
    }

    return render(request, 'olustur.html', context)

# self.slug = slugify(self.isim.replace('ı', 'i'))


def sepetim(request):
    urunler = Sepet.objects.filter(ekleyen=request.user, odendiMi=False)
    toplam = 0
    for i in urunler:
        toplam += i.total
    if request.method == 'POST':
        if 'odeme' not in request.POST:
            sepetId = request.POST['sepetId']
            sepet = Sepet.objects.get(id=sepetId)
        if 'sil' in request.POST:
            sepet.delete()
            messages.success(request, 'Ürün silindi')
            return redirect('sepetim')
        elif 'guncelle' in request.POST:
            adet = request.POST['adet']
            if adet == '0':
                sepet.delete()
                messages.success(request, 'Sepet Güncellendi')
            else:
                sepet.adet = adet
                sepet.save()
                messages.success(request, 'Sepet Güncellendi')
                return redirect('sepetim')
        elif 'odeme' in request.POST:
            if Odeme.objects.filter(user=request.user, odendiMi=False).exists():
                pass
            else:
                odeme = Odeme.objects.create(
                    user=request.user,
                    total=toplam
                )
                odeme.urunler.add(*urunler)
                odeme.save()
            return redirect('payment')
    context = {
            'urunler': urunler,
            'toplam': toplam
        }
    return render(request, 'sepetim.html', context)
