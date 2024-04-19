from captcha.fields import CaptchaField
from django import forms

from vitamins.models import Vitamin, DeliveryRequest


class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=200)


class AddVitamin(forms.ModelForm):

    class Meta:
        model = Vitamin
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'count': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'cat': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'product_code': forms.TextInput(attrs={'class': 'form-control'}),
            # Для полей ManyToManyField и ForeignKey может потребоваться использовать SelectMultiple или Select
        }


class RequestForDeliveryForm(forms.ModelForm):
    name = forms.CharField(label='Ваше Имя*', max_length=200)
    email = forms.EmailField(label='E-mail*')
    title = forms.CharField(label='Название добавки*', max_length=350)
    url = forms.CharField(label='Ссылка на добавку, URL(если есть)', required=False)
    comment = forms.CharField(label='Комментарий', widget=forms.Textarea(attrs={'rows': 3}), required=False)
    captcha = CaptchaField()

    class Meta:
        model = DeliveryRequest
        fields = ['name', 'email', 'title', 'url', 'comment']
