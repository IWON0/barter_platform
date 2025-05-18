from django import forms
from .models import Ad, ExchangeProposal

class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image_url', 'category', 'condition']

class ExchangeProposalForm(forms.ModelForm):
    ad_sender = forms.ModelChoiceField(queryset=Ad.objects.none(), label='Ваш товар для обмена')

    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'comment']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['ad_sender'].queryset = Ad.objects.filter(user=user)

