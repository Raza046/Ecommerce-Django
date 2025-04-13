from django import forms
from Orders.models import Order


class OrderForm(forms.ModelForm):

    first_name = forms.CharField(
        label="First Name",
        widget= forms.TextInput(
            attrs={
                'class':'form-control',
                'id':'fname_form',
                'required':True
            }
        ),
    )
    
    last_name = forms.CharField(
        widget= forms.TextInput(
            attrs={
                'class':'form-control',
                'id':'lastname_form',
                'required':True
            }
        ),
    )

    address = forms.CharField(
        label="Address",
        widget= forms.TextInput(
            attrs={
                'class':'form-control',
                'id':'address_form',
                'required':True
            }
        ),

    )

    country = forms.CharField(
        label="Country",
        widget= forms.TextInput(
            attrs={
                'class':'form-control',
                'id':'country_form',
                'required':True
            }
        )
    )

    city = forms.CharField(
        label="City",
        widget= forms.TextInput(
            attrs={
                'class':'form-control',
                'id':'city_form',
                'required':True
            }
        )
    )

    contact = forms.CharField(
        widget= forms.TextInput(
            attrs={
                'class':'form-control',
                'id':'contact_form',
                'required':True
            }
        )
    )

    email = forms.CharField(
        widget= forms.EmailInput(
            attrs={
                'class':'form-control',
                'id':'email_form',
                'required':True
            }
        )
    )

    class Meta:
        model = Order
        exclude = ('order_id', 'cart' ,'payment_id' ,'total', 'customer', 'status', 'delivery_option')
    
