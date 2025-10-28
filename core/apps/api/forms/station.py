from django import forms

from core.apps.api.models import ConnectorModel, StationModel


class StationForm(forms.ModelForm):

    class Meta:
        model = StationModel
        fields = "__all__"


class ConnectorForm(forms.ModelForm):

    class Meta:
        model = ConnectorModel
        fields = "__all__"
