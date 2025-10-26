# app/forms.py
from django import forms

class ChatForm(forms.Form):
    prompt = forms.CharField(
        required=True,
        max_length=2000,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Digite sua pergunta...'})
    )
    max_new_tokens = forms.IntegerField(required=False, min_value=1, max_value=512, initial=128)
    temperature = forms.FloatField(required=False, min_value=0.0, max_value=2.0, initial=0.7)