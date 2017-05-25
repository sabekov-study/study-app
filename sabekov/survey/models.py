from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Button, Field, Div
from crispy_forms.bootstrap import InlineCheckboxes, FormActions

from simple_history.models import HistoricalRecords

import json


class Checklist(models.Model):
    name = models.SlugField(max_length=200, unique=True)
    version = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_sequence(self):
        return self.catalogs.filter(is_top_level=True)

    def list_expanded_labels(self):
        l = list()
        for cat in self.get_sequence():
            l.extend(cat.expand(labels_only=True))
        return l

    @staticmethod
    @transaction.atomic
    def import_from_json(path):
        import json
        with open(path, "r") as f:
            obj = json.load(f)
            cl = Checklist.objects.create(
                    name=obj.get("name", "imported"),
                    version=obj.get("version"),
                    is_active=True,
                )
            # add top-level cats first to achieve proper ordering
            top_cats = obj.get("steps")
            for cn in top_cats:
                cl.catalogs.create(label=cn, is_top_level=True)
            # add remaining cats
            for cn in obj.get("subcategories"):
                if cn in top_cats:
                    continue # already added before
                cl.catalogs.create(label=cn)
            # add questions
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
                        negative = (ans.startswith("_") and ans.endswith("_"))
                        q.answer_options.create(
                            name=ans if not negative else ans[1:-1],
                            negativ=negative,
                        )
                    q.save()
            cl.save()


class Catalog(models.Model):
    label = models.SlugField(max_length=30)
    name = models.CharField(max_length=200, blank=True)
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name="catalogs")
    is_top_level = models.BooleanField(default=False)

    def __str__(self):
        return self.label

    def expand(self, labels_only=False):
        l = list()
        self.__build_full_list(self, l, labels_only=labels_only)
        return l

    def __build_full_list(self, catalog, label_list, prefixes=[], labels_only=False):
        for q in catalog.questions.all():
            if q.reference:
                prefix = q.label.rsplit('_' + q.reference.label, maxsplit=1)[0]
                self.__build_full_list(
                    q.reference,
                    label_list,
                    prefixes + [prefix],
                    labels_only=labels_only,
                )
            else:
                full_label = "_".join(prefixes + [q.label])
                label_list.append(
                    (full_label, q) if not labels_only else full_label
                )

    class Meta:
        order_with_respect_to = 'checklist'
        unique_together = ('checklist', 'label')


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
    question_text = models.CharField(max_length=300, blank=True)
    comment = models.CharField(max_length=300, blank=True)
    answer_type = models.CharField(max_length=2, choices=ANSWER_TYPES, default=ALTERNATIVES, blank=True)
    catalog = models.ForeignKey(Catalog, on_delete=models.CASCADE, related_name="questions")
    reference = models.ForeignKey(Catalog, on_delete=models.CASCADE, related_name="references", blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.label

    def get_choices(self, empty=False):
        if self.answer_type in (self.ALTERNATIVES, self.MULTINOM):
            l = [ (o.name, o.name) for o in self.answer_options.all() ]
            return [("n.n.", "-- choose --")] + l if empty else l
        else:
            raise ValueError("No choices for this answer type.")

    def has_negatives(self):
        return self.answer_options.filter(negativ=True).count() != 0

    def save(self, *args, **kwargs):
        super(Question, self).save(*args, **kwargs)
        # flag all answers as revision needed, since the question changed
        self.answers.update(revision_needed=True)

    class Meta:
        order_with_respect_to = 'catalog'


class Site(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

    @staticmethod
    @transaction.atomic
    def import_from_file(path):
        with open(path, "r") as f:
            for l in f.readlines():
                sn = l.strip().lower()
                Site.objects.get_or_create(name=sn)


class SiteEvaluation(models.Model):
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name="evaluations")
    tester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="evaluations")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="evaluations")
    note = models.CharField(max_length=300, blank=True)
    finished = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return "Evaluation of {} by {}".format(str(self.site), str(self.tester))

    @transaction.atomic
    def populate_answers(self):
        for catalog in self.checklist.get_sequence():
            self.__populate_with_catalog(catalog)

    def __populate_with_catalog(self, catalog, prefixes=[]):
        for q in catalog.questions.all():
            if q.reference:
                prefix = q.label.rsplit('_' + q.reference.label, maxsplit=1)[0]
                self.__populate_with_catalog(q.reference, prefixes + [prefix])
            else:
                full_label = "_".join(prefixes + [q.label])
                if not self.answers.filter(full_label=full_label).exists():
                    ac = self.answers.create(
                        full_label=full_label,
                        question=q,
                        parent=self.__get_parent(full_label),
                    )

    def __get_parent(self, label):
        while label != "":
            cand_label = label.rsplit("_", maxsplit=1)[0]
            try:
                parent = self.answers.get(full_label=cand_label)
                return parent
            except AnswerChoice.DoesNotExist as e:
                if label == cand_label:
                    label = ""
                else:
                    label = cand_label
        return None


    def answers_ordered_by_label(self, flat=False, add_unanswered=False):
        """Returns a list of AnswerChoice/AnswerForm tuples."""
        l = list()
        for cat in self.checklist.get_sequence():
            catlist = list()
            for full_label, q in cat.expand():
                try:
                    ac = self.answers.get(
                        full_label=full_label,
                    )
                    catlist.append(ac)
                except AnswerChoice.DoesNotExist:
                    if add_unanswered:
                        ac = AnswerChoice(
                            evaluation=self,
                            full_label=full_label,
                            question=q,
                            parent = self.__get_parent(full_label),
                        )
                        catlist.append(ac)
                    else:
                        pass
            if flat:
                l.extend(catlist)
            else:
                l.append((cat.label, catlist))
        return l


    def get_forms(self, data=None):
        """Returns a list of AnswerChoice/AnswerForm tuples."""
        forms = list()
        for cat, cl in self.answers_ordered_by_label(add_unanswered=True):
            catforms = list()
            for ac in cl:
                catforms.append((
                    ac,
                    AnswerForm(
                        data,
                        instance=ac,
                        prefix=ac.full_label,
                    )
                ))
            forms.append((cat, catforms))
        return forms


    def count_discussions(self):
        return self.answers.filter(discussion_needed=True).count()

    def count_revisions(self):
        return self.answers.filter(revision_needed=True).count()

    class Meta:
        unique_together = ("checklist", "tester", "site")
        permissions = (
            ('can_review', 'Can review site evaluations'),
        )


class SiteEvaluationForm(forms.ModelForm):

    class Meta:
        model = SiteEvaluation
        fields = ['note', 'finished']
        widgets = {
                'note': forms.Textarea(attrs={'rows': '5'}),
        }
        labels = {
            'note': '',
        }


class AnswerOption(models.Model):
    name = models.CharField(max_length=200)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answer_options")
    negativ = models.BooleanField(default=False)
    history = HistoricalRecords()

    class Meta:
        order_with_respect_to = 'question'


class SortedAnswerChoiceManager(models.Manager):
    def ordered_by_label(self, checklist, *args, **kwargs):
        # get full label order reference
        ref_list = checklist.list_expanded_labels()
        # query
        qs = super(SortedAnswerChoiceManager, self).get_queryset().filter(evaluation__checklist=checklist).filter(*args, **kwargs)
        return sorted(qs, key=lambda ac: ref_list.index(ac.full_label))

class AnswerChoice(models.Model):
    evaluation = models.ForeignKey(SiteEvaluation, on_delete=models.CASCADE, related_name="answers")
    full_label = models.SlugField(max_length=100, db_index=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
            related_name="children", blank=True, null=True)
    value = models.CharField(max_length=200, default="", blank=True)
    note = models.CharField(max_length=300, blank=True)
    discussion_needed = models.BooleanField(default=False)
    revision_needed = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()
    objects = SortedAnswerChoiceManager()

    def get_full_label(self):
        return self.full_label

    def get_parent_label(self):
        return self.parent.get_full_label() if self.parent else ""

    def is_outdated(self):
        """Checks if the question changed since this answer has been given."""
        if self.last_updated is None:
            return False
        return self.last_updated < self.question.history.latest('history_date').history_date

    def get_question_as_answered(self):
        return self.question.history.as_of(self.last_updated).pk

    def __str__(self):
        return self.get_full_label()

    class Meta:
        unique_together = ('evaluation', 'full_label')
        ordering = ['id']


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
                        label='',
                )
            elif ans.question.answer_type == Question.MULTINOM:
                self.fields['value'] = forms.MultipleChoiceField(
                        choices=ans.question.get_choices(),
                        label='',
                        widget=forms.CheckboxSelectMultiple,
                        required=False, # allows saving of unfinished evals
                )

        # add information about negative selections for JS-based collapsing
        if ans and ans.question.answer_type == Question.ALTERNATIVES:
            self.fields['negatives'] = forms.CharField(
                    initial=json.dumps([o.name for o in ans.question.answer_options.filter(negativ=True)]),
                    disabled=True,
                    widget=forms.HiddenInput,
            )
            self.fields['negatives'].has_changed = lambda x, y: False


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
                'note': forms.Textarea(attrs={'rows': '5'}),
        }
        labels = {
            'value': '',
            'note': 'Notes',
        }

