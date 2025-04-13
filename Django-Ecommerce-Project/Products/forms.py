from django import forms

from Products.models import Reviews


class ReviewForm(forms.ModelForm):

    widget= forms.TextInput(
        attrs={
            'class':'form-control',
            'required':True
        }
    )

    class Meta:
        model = Reviews
        fields = ("name", "email", "comment")

    name = forms.CharField(label="Name", widget = widget)
    email = forms.EmailField(label="Email", widget = widget)
    comment = forms.CharField(widget=forms.Textarea(attrs=widget.attrs))
    # image = forms.FileField(widget=forms.FileInput(attrs=widget.attrs))
