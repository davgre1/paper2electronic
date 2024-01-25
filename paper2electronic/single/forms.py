from django import forms
from single.models import Image


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'image']