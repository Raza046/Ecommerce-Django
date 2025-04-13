from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg


class Product(models.Model):

    Name = models.CharField(max_length=150)
    Price = models.IntegerField()
    Description = models.TextField()
    Image_main = models.FileField(upload_to="static")
    subcategory = models.ForeignKey("SubCategory", related_name="products", on_delete=models.PROTECT)
    variations = models.ManyToManyField("Variation",blank=True)
    sale = models.PositiveIntegerField(default=0)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return self.Name

    @property
    def rating_value(self):
        reviews = Reviews.objects.filter(product=self).values_list("rating").aggregate(
            avg_rating=Avg('rating')
        )
        return reviews["avg_rating"]

    def get_absolute_url(self):
        return f"/product/{self.id}"

class ProductImage(models.Model):   

    Image = models.FileField(upload_to="static", null=True)
    cover_image = models.BooleanField(default=False)
    product_variant = models.ForeignKey("ProductVariant", related_name="images", on_delete=models.CASCADE, null=True, blank=True)


class Category(models.Model):

    name = models.CharField(max_length=100)
    # objects = CategoryManager()

    def __str__(self):
        return self.name

    @classmethod
    def FilterCategory(self):
        categories = Category.objects.all()
        return categories


class SubCategory(models.Model):
    
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, verbose_name=("Cat_subcategory"), on_delete=models.CASCADE)
    def __str__(self):
        return self.name


class Reviews(models.Model):

    product = models.ForeignKey("Product", verbose_name=("product_reviews"), related_name="reviews", on_delete=models.CASCADE, null=True)
    users = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE, null=True)
    # datetime = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(max_length=254)
    name = models.CharField(max_length=250)
    comment = models.CharField(max_length=100)
    rating = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.users.username} rated this product (self.product.name)"


class ReviewImages(models.Model):

    review = models.ForeignKey("Reviews", verbose_name=("review_images"), related_name="images", on_delete=models.CASCADE)
    image = models.FileField(upload_to="static")
    video = models.FileField(upload_to="static")


class ProductVariant(models.Model):
    sku = models.CharField(max_length = 150,null=True,blank=True)
    product = models.ForeignKey("Product", related_name="variants", on_delete=models.CASCADE)
    variation = models.ManyToManyField("VariationValue", related_name="variations")
    price = models.IntegerField()
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.Name} {[variants.value for variants in self.variation.all()]}"

    def is_available(self):
        return bool(self.stock)


class Variation(models.Model):

    name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return self.name


class VariationValue(models.Model):

    variation = models.ForeignKey("Variation", related_name="value", on_delete=models.CASCADE)
    value = models.CharField(max_length=300, null=True)

    def __str__(self):
        return f'{self.variation} : {self.value}'

