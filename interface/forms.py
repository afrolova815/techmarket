from django import forms
from .validators import FilledAndPatternValidator


class AddRecordForm(forms.Form):
    title = forms.CharField(
        min_length=5,
        max_length=100,
        widget=forms.TextInput(attrs={
            "required": True,
            "minlength": 5,
            "maxlength": 100,
            "class": "select",
        }),
        validators=[FilledAndPatternValidator()],
    )
    quantity = forms.IntegerField(
        min_value=1,
        max_value=10000,
        widget=forms.NumberInput(attrs={
            "required": True,
            "min": 1,
            "max": 10000,
            "class": "select",
        }),
    )
    event_date = forms.DateField(
        widget=forms.DateInput(attrs={
            "type": "date",
            "required": True,
            "class": "select",
        }),
    )

class UploadFileForm(forms.Form):
    file = forms.FileField(
        label="Файл",
        widget=forms.ClearableFileInput(attrs={"class": "select"}),
    )
