from django import forms

from core.apps.api.models import ConnectorModel, ChargerModel


class ChargerForm(forms.ModelForm):

    class Meta:
        model = ChargerModel
        fields = "__all__"


class ConnectorForm(forms.ModelForm):

    class Meta:
        model = ConnectorModel
        fields = "__all__"
