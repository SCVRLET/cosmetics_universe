from django import forms

from products_import.models import Shop, ProductCategory, ProductBrand

class ProductsFilterForm(forms.Form):
    shop_choices = [(shop.id, shop.title) for shop in Shop.objects.all().order_by('title')]
    shop_choice = forms.MultipleChoiceField(choices=shop_choices, label="Магазины", widget=forms.CheckboxSelectMultiple, required=False)

    category_choices = [(category.id, category.title) for category in ProductCategory.objects.all().order_by('title')]
    category_choice = forms.MultipleChoiceField(choices=category_choices, label="Категории", widget=forms.CheckboxSelectMultiple, required=False)

    brand_choices = [(brand.id, brand.title) for brand in ProductBrand.objects.all().order_by('title')]
    brand_choice = forms.MultipleChoiceField(choices=brand_choices, label="Производители", widget=forms.CheckboxSelectMultiple, required=False)