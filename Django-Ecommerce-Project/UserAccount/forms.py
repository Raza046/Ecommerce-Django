from django import forms
from django.shortcuts import redirect
from django.contrib.auth.models import User
from UserAccount.models import Users
from django.contrib.auth import authenticate

class RegistrationForm(forms.ModelForm):

    username = forms.CharField(
        widget= forms.TextInput(
            attrs={
                'class':'form-control',
                'id':'username',
                'required':True
            }
        )
    )

    email = forms.CharField(
        widget= forms.EmailInput(
            attrs={
                'class':'form-control',
                'id':'email',
                'required':True
            }
        )
    )

    full_name = forms.CharField(
        widget= forms.TextInput(
            attrs={
                'class':'form-control',
                'id':'fullname',
                'required':True
            }
        )
    )

    password = forms.CharField(
        widget= forms.PasswordInput(
            attrs={
                'class':'form-control',
                'id':'password',
                'required':True
            }
        )
    )

    confirm_password = forms.CharField(
        widget= forms.PasswordInput(
            attrs={
                'class':'form-control',
                'id':'confirm_password',
                'required':True
            }
        )
    )

    country = forms.CharField(
        widget= forms.TextInput(
            attrs={
                'class':'form-control',
                'id':'country',
                'required':True
            }
        )
    )

    city = forms.CharField(
        widget= forms.TextInput(
            attrs={
                'class':'form-control',
                'id':'city',
                'required':True
            }
        )
    )

    phone = forms.CharField(
        widget= forms.TextInput(
            attrs={
                'class':'form-control',
                'id':'phone',
                'required':True
            }
        )
    )

    zip_code = forms.CharField(
        widget= forms.TextInput(
            attrs={
                'class':'form-control',
                'id':'zip_code',
                'required':True
            }
        )
    )

    class Meta:
        model = Users
        exclude = ('user', 'user_type', 'picture', 'favourite')

    def clean(self):

        if User.objects.filter(
            username=self.cleaned_data['username'], email=self.cleaned_data['email']
            ).exists():
            raise forms.ValidationError("Username or Password already exists!")

        elif self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
            raise forms.ValidationError("password doesn't matched!")

        return self.cleaned_data


class LoginForm(RegistrationForm):

    class Meta(RegistrationForm.Meta):
        exclude = ['confirm_password', 'zip_code', 'country', 'city', 'phone', 'email', 'full_name']
        fields = ['username', 'password']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in LoginForm.Meta.exclude:
            self.fields.pop(field)

    def clean(self):
        user_obj = authenticate(
            username = self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )
        if user_obj is None:
            raise forms.ValidationError("Username or passowrd incorrect!")
        else:
            return self.cleaned_data
