from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
from django import forms

import json



class Catalog(models.Model):
    label = models.SlugField(max_length=30, unique=True)
    name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.label


class Question(models.Model):
    ALTERNATIVES = "AL"
    MULTINOM = "MU"
    INPUT = "IN"
    ANSWER_TYPES = (
        (ALTERNATIVES, "Alternatives"),
        (MULTINOM, "Multiple nominations"),
        (INPUT, "Input"),
    )
    label = models.SlugField(max_length=30, unique=True)
    question_text = models.CharField(max_length=200, blank=True)
    comment = models.CharField(max_length=300, blank=True)
    answer_type = models.CharField(max_length=2, choices=ANSWER_TYPES, default=ALTERNATIVES, blank=True)
    catalog = models.ForeignKey(Catalog, on_delete=models.CASCADE, related_name="questions")
    reference = models.ForeignKey(Catalog, on_delete=models.CASCADE, related_name="references", blank=True, null=True)

    def __str__(self):
        return self.label

    def get_choices(self, empty=False):
        if self.answer_type in (self.ALTERNATIVES, self.MULTINOM):
            l = [ (o.name, o.name) for o in self.answer_options.all() ]
            return [("n.n.", "-- choose --")] + l if empty else l
        else:
            raise ValueError("No choices for this answer type.")


class Checklist(models.Model):
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=200)
    catalogs = models.ManyToManyField(Catalog, related_name="+")
    sequence = models.ManyToManyField(Catalog, related_name="checklist_sequences")

    def __str__(self):
        return self.name

    @staticmethod
    @transaction.atomic
    def import_from_json(path):
        import json
        with open(path, "r") as f:
            obj = json.load(f)
            cl = Checklist.objects.create(
                    name=obj.get("name", "n.n."),
                    version=obj.get("version"),
                )
            for cn in obj.get("subcategories"):
                c = Catalog.objects.create(label=cn)
                c.save()
                cl.catalogs.add(c)
            for step in obj.get("steps"):
                cl.sequence.add(Catalog.objects.get(label=step))
            for cn in obj.get("subcategories"):
                ql = obj.get("subcategories").get(cn)
                for qd in ql:
                    q = Question.objects.create(
                            label=qd.get("label"),
                            question_text=qd.get("question") if qd.get("question") else "",
                            catalog=Catalog.objects.get(label=cn)
                        )
                    if qd.get("reference"):
                        q.reference = Catalog.objects.get(label=qd.get("reference"))
                    if qd.get("answer_type") == "selection":
                        q.answer_type = Question.ALTERNATIVES
                    elif qd.get("answer_type") == "multiselection":
                        q.answer_type = Question.MULTINOM
                    elif qd.get("answer_type") == "input":
                        q.answer_type = Question.INPUT
                    else:
                        q.answer_type = ""
                    ansl = qd.get("answers") if qd.get("answers") else []
                    for ans in ansl:
                        q.answer_options.create(
                            name=ans,
                            negativ=(ans.startswith("_") and ans.endswith("_")),
                        )
                    q.save()
            cl.save()



class Site(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class SiteEvaluation(models.Model):
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name="evaluations")
    tester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="evaluations")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="evaluations")
    note = models.CharField(max_length=300, blank=True)
    finished = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return "Evaluation of %s by %s".format(str(self.site), str(self.tester))

    @transaction.atomic
    def populate_answers(self):
        for catalog in self.checklist.sequence.all():
            self.__populate_with_catalog(catalog)

    def __populate_with_catalog(self, catalog, path=[]):
        for q in catalog.questions.all():
            if q.reference:
                self.__populate_with_catalog(q.reference, path + [catalog])
            else:
                ac = self.answers.create(
                    question=q,
                    value="",
                )
                ac.path = path

    def generate_forms(self, data=None):
        """Returns a list of AnswerChoice/AnswerForm tuples."""
        forms = list()
        for ans in self.answers.all():
            f = AnswerForm(
                    data,
                    instance=ans,
                    prefix=ans.get_full_label()
            )
            forms.append((ans, f))
        return forms


class AnswerOption(models.Model):
    name = models.CharField(max_length=200)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answer_options")
    negativ = models.BooleanField(default=False)

    class Meta:
        order_with_respect_to = 'question'

class AnswerChoice(models.Model):
    evaluation = models.ForeignKey(SiteEvaluation, on_delete=models.CASCADE, related_name="answers")
    path = models.ManyToManyField(Catalog, related_name="+")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    value = models.CharField(max_length=200)
    note = models.CharField(max_length=300, blank=True)
    discussion_needed = models.BooleanField(default=False)
    revision_needed = models.BooleanField(default=False)

    def get_full_label(self):
        #return self.question.label
        return "_".join([c.label for c in self.path.all()] + [self.question.label])

    def __str__(self):
        return self.get_full_label()

class AnswerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        ans = kwargs.get('instance', None)

        # unmarshal multinom values for field initialization
        if ans and ans.question.answer_type == Question.MULTINOM:
            initial = kwargs.get('initial', {})
            initial['value'] = json.loads(ans.value) if ans.value != "" else []
            kwargs['initial'] = initial

        super(AnswerForm, self).__init__(*args, **kwargs)

        # adjust value field type to question type
        if ans:
            if ans.question.answer_type == Question.ALTERNATIVES:
                self.fields['value'] = forms.ChoiceField(
                        choices=ans.question.get_choices(empty=True),
                        label='Answer',
                )
            elif ans.question.answer_type == Question.MULTINOM:
                self.fields['value'] = forms.MultipleChoiceField(
                        choices=ans.question.get_choices(),
                        label='Answer',
                        widget=forms.CheckboxSelectMultiple,
                )

        # add information about negative selections for JS-based collapsing
        if ans and ans.question.answer_type == Question.ALTERNATIVES:
            self.fields['negatives'] = forms.CharField(
                    initial=json.dumps([o.name for o in ans.question.answer_options.filter(negativ=True)]),
                    disabled=True,
                    widget=forms.HiddenInput,
            )

    def clean(self):
        cleaned_data=super(AnswerForm, self).clean()
        if self.instance.question.answer_type != Question.MULTINOM:
            return cleaned_data
        # marshal multinom selection into single str value with json encoding
        val = cleaned_data.get("value")
        cleaned_data['value'] = json.dumps(val)
        return cleaned_data

    class Meta:
        model = AnswerChoice
        fields = ['value', 'note', 'discussion_needed', 'revision_needed']
        widgets = {
            'note': forms.Textarea,
        }
        labels = {
            'value': 'Answer',
        }

