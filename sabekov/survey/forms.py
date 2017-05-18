from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Button, HTML
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
        ),
        widget=forms.CheckboxSelectMultiple(),
        label='',
    )

    def __init__(self, *args, **kwargs):
        super(AnswerFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form'
        self.helper.layout = Layout(
            'filter',
            FormActions(
                StrictButton('Apply Filter', css_class='btn-block',
                    onclick='applyFilter()'),
            )
        )



