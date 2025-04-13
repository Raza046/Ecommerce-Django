from django import forms

from Cart.models import Coupon
from Orders.models import Order
from Products.models import Category, ProductVariant, SubCategory, Product


class CategoryForm(forms.ModelForm):

    name = forms.CharField(
    label="Category Name",
    widget= forms.TextInput(
        attrs={
            'class':'form-control',
            'id':'addcat',
            'required':True
            }
        ),
    )

    class Meta:
        model = Category
        fields = "__all__"

    def clean(self):
        print(self.cleaned_data['name'])
        category = Category.objects.filter(name = self.cleaned_data['name'])
        if category.exists():
            raise forms.ValidationError("Category Already Exists")
        return super().clean()


class SubCategoryForm(CategoryForm):

    class Meta:
        model = SubCategory
        fields = ("name",)

    def __init__(self, *args, **kwargs):

        self.category_id = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({"id":"addsubcat"})

    def clean(self):

        subcategory_name = self.cleaned_data['name']
        if SubCategory.objects.filter(
            category_id = self.category_id, name = subcategory_name
            ).exists():
            forms.ValidationError("Sorry! SubCategory Name already Exists")

        return super().clean()


class AddProductForm(forms.ModelForm):

    widget= forms.TextInput(
        attrs={
            'class':'form-control',
            'id':'addcat',
            'required':True
            }
        )

    Name = forms.CharField( label="Product Name", widget = widget)
    Price = forms.IntegerField(label="Price", widget = widget)
    Description = forms.CharField(widget=forms.Textarea(attrs=widget.attrs))
    Image_main = forms.FileField(widget=forms.FileInput(attrs=widget.attrs))

    class Meta:
        model = Product
        fields = ('Name', 'Price', 'Description', 'Image_main')

    def clean(self):
        print("*********************")
        print(self.cleaned_data['Name'])
        print(self.cleaned_data['Image_main'])
        print("*********************")
        return super().clean()


class CouponUpdateForm(forms.ModelForm):

    class Meta:
        model = Coupon
        fields = ("id", "discount", "all_users", "code", "valid_to", )


class CouponCreateForm(forms.ModelForm):

    class Meta:
        model = Coupon
        exclude = ("usage", "is_expired", )


class ProductVariantCreateForm(forms.ModelForm):

    class Meta:
        model = ProductVariant
        exclude = ("variation", "is_active", )


class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']


class FilterGraphValidation(forms.Form):

    from_date = forms.DateField()
    to_date = forms.DateField()

