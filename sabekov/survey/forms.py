from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Button
from crispy_forms.bootstrap import InlineCheckboxes, FormActions


from .models import *

class ChecklistForm(forms.Form):
    checklist = forms.ModelChoiceField(
        queryset=Checklist.objects.filter(is_active=True),
        empty_label=None,
    )

class AnswerFilterForm(forms.Form):
    filter = forms.ChoiceField(
        choices=(
            ("revision", "revision"),
            ("discussion", "discussion"),
            ("unanswered", "unanswered"),
        ),
        widget=forms.CheckboxSelectMultiple(),
    )

    def __init__(self, *args, **kwargs):
        super(AnswerFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            InlineCheckboxes('filter'),
            FormActions(
                Button('apply', 'Apply', ontrigger='applyFilter()')
            )
        )



