# forms.py

from django import forms

class MetadataForm(forms.Form):
    metadata = forms.CharField(widget=forms.Textarea, required=False)
