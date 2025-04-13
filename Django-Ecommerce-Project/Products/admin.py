from django.contrib import admin
from Products.models import ProductVariant, ReviewImages, Product,Category,Reviews,ProductImage, SubCategory, Variation, VariationValue

class ProductAdmin(admin.ModelAdmin):
    list_display = ['Name','Price']

admin.site.register(Product,ProductAdmin)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Reviews)
admin.site.register(ReviewImages)
admin.site.register(ProductImage)
admin.site.register(ProductVariant)
admin.site.register(Variation)
admin.site.register(VariationValue)
