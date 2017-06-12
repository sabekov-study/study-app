from django import forms
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Button, HTML
from crispy_forms.layout import Submit
from crispy_forms.bootstrap import InlineCheckboxes, FormActions, StrictButton


from .models import *

class ChecklistForm(forms.Form):
    checklist = forms.ModelChoiceField(
        queryset=Checklist.objects.filter(is_active=True),
        empty_label=None,
    )

class AnswerFilterForm(forms.Form):
    filter = forms.ChoiceField(
        choices=(
            ("unanswered", "unanswered"),
            ("discussion_needed", "discussion need"),
            ("revision_needed", "revision needed"),
            ("dirty", "dirty"),
        ),
        widget=forms.CheckboxSelectMultiple(attrs = {
            'onchange': 'applyFilter()',
        }),
        label='',
    )

    def __init__(self, *args, **kwargs):
        super(AnswerFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form'
        self.helper.layout = Layout(
            'filter',
        )


class ImportChecklistForm(forms.Form):
    checklist = forms.ModelChoiceField(
        queryset=Checklist.objects.filter(is_active=True),
        empty_label=None,
    )
    json = forms.CharField(
        widget=forms.Textarea,
    )

    def clean_json(self):
         jdata = self.cleaned_data['json']
         try:
             json_data = json.loads(jdata)
             return jdata
         except json.decoder.JSONDecodeError:
             raise forms.ValidationError("Invalid data in json field")

    def __init__(self, *args, **kwargs):
        super(ImportChecklistForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('survey:import-checklist')
        self.helper.add_input(Submit('submit', 'Continue'))


class HiddenImportDataForm(forms.Form):
    json = forms.CharField(
        widget=forms.HiddenInput,
    )

    def clean_json(self):
         jdata = self.cleaned_data['json']
         try:
             json_data = json.loads(jdata)
             return jdata
         except json.decoder.JSONDecodeError:
             raise forms.ValidationError("Invalid data in json field")


class UpdateControlForm(forms.Form):
    flag_dirty = forms.BooleanField(
        label='',
        required=False,
    )
