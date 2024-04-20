from django import forms

from .models import Shop, ProductCategory

class ProductsImportForm(forms.Form):
    shop_choices = [(shop.title, shop.title) for shop in Shop.objects.all()]
    shop_choice = forms.ChoiceField(choices=shop_choices)

    category_choices = [(category.title, category.title) for category in ProductCategory.objects.all()]
    category_choice = forms.ChoiceField(choices=category_choices)

    url = forms.URLField()