from django.db import models

from django.core.validators import MaxValueValidator, MinValueValidator


class ProductCategory(models.Model):
	title = models.CharField(max_length=100, unique=True)

	class Meta:
		db_table = 'product_category'

	def __str__(self):
		return self.title


class ProductBrand(models.Model):
	title = models.CharField(max_length=50, unique=True)
	logo = models.ImageField(upload_to='brand_logos/', null=True, blank=True)

	class Meta:
		db_table = 'product_brand'

	def __str__(self):
		return self.title


class Shop(models.Model):
	title = models.CharField(max_length=50, unique=True)
	url = models.URLField(max_length=200, unique=True)
	logo = models.ImageField(upload_to='shop_logos/', null=True, blank=True)

	class Meta:
		db_table = 'shop'

	def __str__(self):
		return self.title


class Product(models.Model):
	title = models.CharField(max_length=150)
	source_link = models.URLField(max_length=350)
	brand = models.ForeignKey(ProductBrand, on_delete=models.CASCADE)
	category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
	shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
	image = models.ImageField(upload_to='product_images/', null=True, blank=True)
	description = models.CharField(max_length=1000)

	class Meta:
		db_table = 'product'

	def __str__(self):
		return f"{self.title}, url: {self.source_link}"


class Offer(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	price_without_discount = models.PositiveIntegerField()
	discount = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )
	size = models.CharField(max_length=20)
	is_available = models.BooleanField()

	@property
	def price_with_discount(self):
		return self.price_with_discount - self.price_with_discount * self.discount

	class Meta:
		db_table = 'offer'

	def __str__(self):
		return f"Товар: {self.product}, цена без скидки: {self.price_without_discount}"