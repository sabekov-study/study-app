from django import forms

from .models import *

class ChecklistForm(forms.Form):
    checklist = forms.ModelChoiceField(
        queryset=Checklist.objects.filter(is_active=True),
        empty_label=None,
    )
