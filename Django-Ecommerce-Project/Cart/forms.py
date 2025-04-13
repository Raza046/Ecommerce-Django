from .models import CartItem, Product
from django import forms
from django.db import models


class CartItemsForm(forms.ModelForm):

    widget= forms.RadioSelect(
        attrs={
            'class':'radio_input',
            'id':'{{i.id}}',
            'required':True
            }
        )
    widget1= forms.TextInput(
        attrs={
            'class':'form-control',
            'required':True
            }
        )

    COLORS = (
        ('red', 'Red'),
        ('green', 'Green'),
        ('blue', 'Blue'),
    )
    color = forms.ChoiceField(choices=COLORS, widget=widget)

    # color = forms.RadioSelect()
    size = forms.IntegerField(label="size", widget = widget1)
    quantity = forms.IntegerField(label="quantity", widget = widget1)

    class Meta:
        model = CartItem
        exclude = ('product_variant','price','cart')

    def clean(self):
        return super().clean()


class CartUpdateForm(forms.Form):
    """ This class will be used to update the Cart """
    class ActionTypes(models.TextChoices):
        INCREMENT = 'increment'
        DECREMENT = 'decrement'

    item_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=1)
    action = forms.ChoiceField(choices=ActionTypes.choices)


class AddItemToCartForm(forms.Form):
    """ This class will be used to update the Cart """

    product_variant_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=1)

