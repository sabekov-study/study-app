from django.db import models
from django.db.models import Case, When
from django.contrib.auth.models import User
from django.db import transaction
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Button, Field, Div
from crispy_forms.bootstrap import InlineCheckboxes, FormActions

from simple_history.models import HistoricalRecords

from datetime import date
import json



class QuestionDiff(object):
    """Descriptor for changes in questions."""

    def __init__(self, question, jdata):
        self.question = question
        self.jdata = jdata
        self.label = question.label
        self.text = self.__diff(question.question_text, jdata.get('question'))
        self.comment = self.__diff(question.comment, jdata.get('comment'))
        self.type = self.__diff(question.answer_type, Question.get_type(jdata))
        self.ref = self.__diff_ref(question.reference, jdata.get('reference'))
        ans_options = jdata.get("answers") or []
        if type(ans_options) is not list:
            # bug in json converter tool
            ans_options = [ans_options]
        self.options = self.__diff(
            list(question.answer_options.values_list('name', 'negativ')),
            [ AnswerOption.parseJson(a) for a in ans_options],
        )
        self.generate_control_form()


    def __diff(self, o, n):
        return (o, n) if (o or n) and o != n else None

    def __diff_ref(self, o, n):
        if o:
            return self.__diff(o.label, n)
        else:
            return self.__diff(o, n)

    def has_changed(self):
        return any([self.text, self.comment, self.type, self.ref, self.options])

    def generate_control_form(self, data=None):
        from .forms import UpdateControlForm
        self.form = UpdateControlForm(
            data,
            prefix=self.label,
            initial = {
                'flag_dirty': any([self.text, self.type, self.options]),
            },
        )


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

    def list_changes(self, jdata):
        """List changes compared to json import."""
        new = list()
        modified = list()
        deleted = list()
        for cn in jdata.get("subcategories"):
            cat = None
            try:
                cat = self.catalogs.get(label=cn)
            except Catalog.DoesNotExist:
                pass

            ql = jdata.get("subcategories").get(cn)
            label_l = [qd.get('label') for qd in ql]

            if cat:
                new.extend([l for l in label_l if l not in cat.questions.values_list('label', flat=True)])
                deleted.extend(cat.questions.exclude(label__in=label_l))
                existing_qs = cat.questions.filter(label__in=label_l)
                for qd in ql:
                    if qd.get('label') in new:
                        continue
                    q = existing_qs.get(label=qd.get('label'))
                    qdiff = QuestionDiff(q, qd)
                    if qdiff.has_changed():
                        modified.append(qdiff)
            else:
                new.extend(label_l) # entirely new catalog

        return (new, modified, deleted)


    @transaction.atomic
    def update(self, jdata, flag_dirty=[]):
        """Update checklist from given json representation."""
        top_cats = jdata.get("steps")
        for cn in jdata.get("subcategories"):
            self.catalogs.update_or_create(
                label=cn,
                defaults={'is_top_level': cn in top_cats},
            )
        # delete obsolete cats
        self.catalogs.exclude(label__in=jdata.get('subcategories')).delete()
        # update catalog order (only relevant for top-level cats)
        cat_order = Case(*[When(label=label, then=pos) for pos, label in enumerate(top_cats)], default=len(top_cats))
        new_pk_order = self.catalogs.order_by(cat_order).values_list('pk', flat=True)
        self.set_catalog_order(new_pk_order)

        # add, update or delete questions per category
        for cn in jdata.get("subcategories"):
            cat = self.catalogs.get(label=cn)
            q_pks = list()
            for qd in jdata.get("subcategories").get(cn):
                type_mapping = {
                    "selection": Question.ALTERNATIVES,
                    "multiselection":  Question.MULTINOM,
                    "input":  Question.INPUT,
                }
                q, created = cat.questions.update_or_create(
                    label=qd.get("label"),
                    defaults={
                        'question_text': qd.get("question") or "",
                        'comment': qd.get("comment") or "",
                        'reference': self.catalogs.get(label=qd.get("reference")) if qd.get("reference") else None,
                        'answer_type': Question.get_type(qd),
                    }
                )
                q_pks.append(q.pk)

                # update answer choices
                ans_pks = list()
                ans_options = qd.get("answers") or []
                if type(ans_options) is not list:
                    # bug in json converter tool
                    ans_options = [ans_options]
                for ans in ans_options:
                    name, negative = AnswerOption.parseJson(ans)
                    ao, created = q.answer_options.update_or_create(
                        name=name,
                        defaults={'negativ': negative},
                    )
                    ans_pks.append(ao.pk)
                # delete obsolete options
                q.answer_options.exclude(pk__in=ans_pks).delete()
                # update order
                q.set_answeroption_order(ans_pks)
                # flag answers dirty for revision if wanted
                if q.label in flag_dirty:
                    q.answers.update(dirty=True)
            # delete obsolete questions
            cat.questions.exclude(pk__in=q_pks).delete()
            # update order
            cat.set_question_order(q_pks)


    @staticmethod
    @transaction.atomic
    def import_from_json(path):
        import json
        with open(path, "r") as f:
            obj = json.load(f)
            cl = Checklist.objects.get_or_create(
                name=obj.get("name", "imported"),
                defaults={
                    'version': obj.get("version"),
                    'is_active': True,
                },
            )
            cl.update(obj)
            return cl


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
    comment = models.CharField(max_length=1000, blank=True)
    answer_type = models.CharField(max_length=2, choices=ANSWER_TYPES, default=ALTERNATIVES, blank=True)
    catalog = models.ForeignKey(Catalog, on_delete=models.CASCADE, related_name="questions")
    reference = models.ForeignKey(Catalog, on_delete=models.CASCADE, related_name="references", blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.label

    def get_choices(self, empty=False):
        if self.answer_type in (self.ALTERNATIVES, self.MULTINOM):
            l = [ (o.name, o.name) for o in self.answer_options.all() ]
            return [(AnswerChoice.NN, "-- choose --")] + l if empty else l
        else:
            raise ValueError("No choices for this answer type.")

    def has_negatives(self):
        return self.answer_options.filter(negativ=True).count() != 0

    def save(self, *args, **kwargs):
        super(Question, self).save(*args, **kwargs)
        if kwargs.get('flag_dirty', False):
            # flag all answers as dirty, since the question changed
            self.answers.update(dirty=True)

    @staticmethod
    def get_type(jdata):
        type_mapping = {
            "selection": Question.ALTERNATIVES,
            "multiselection":  Question.MULTINOM,
            "input":  Question.INPUT,
        }
        return type_mapping.get(jdata.get('answer_type'), '')

    class Meta:
        order_with_respect_to = 'catalog'


class Listing(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ListingIssue(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="issues", unique_for_date='pub_date')
    pub_date = models.DateField(default=date.today)

    def __str__(self):
        return "{} on {}".format(str(self.listing), self.pub_date)

    class Meta:
        ordering = ['pub_date']


class ListingEntry(models.Model):
    issue = models.ForeignKey(ListingIssue, on_delete=models.CASCADE, related_name="entries")
    site = models.ForeignKey('SiteSynonym', on_delete=models.CASCADE, related_name="listing_entries")
    rank = models.PositiveIntegerField()

    class Meta:
        unique_together = ("issue", "site")


class Site(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

    def calc_inter_rater_relyability(self, checklist):
        """IRR is calculated as the occurance of the most common answer divided
        by the total number of answers for each label."""
        from itertools import groupby
        from collections import Counter
        acs = AnswerChoice.objects.filter(
            evaluation__site=self,
            evaluation__checklist=checklist,
        ).only('full_label', 'value')
        irr_sum = 0.0
        ctr = 0
        for fl, fli in groupby(acs, key=lambda x: x.full_label):
            c = Counter([a.value for a in fli])
            irr = c.most_common(1)[0][1] / sum(c.values())
            irr_sum += irr
            ctr += 1
        return irr_sum / ctr


    class Meta:
        ordering = ['name']


class SiteSynonym(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="synonyms")
    name = models.CharField(max_length=200, unique=True)
    listing_issues = models.ManyToManyField(ListingIssue, through=ListingEntry, related_name="sites")

    def __str__(self):
        return "Synonym {} for {}".format(self.name, str(self.site))


class SiteEvaluation(models.Model):
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name="evaluations")
    tester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="evaluations")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="evaluations")
    note = models.CharField(max_length=1000, blank=True)
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
                            parent=self.__get_parent(full_label), # Fixme: This does not work if parent ACs are not saved yet.
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

    def count_dirties(self):
        return self.answers.filter(dirty=True).count()

    def estimate_progress(self):
        """Estimate the evaluation progress. Returns a values between 0 and 100."""
        total_qs = self.answers.exclude(parent__value=AnswerChoice.NN)
        return int(round(total_qs.exclude(value__in=["", AnswerChoice.NN]).count() /
                total_qs.count(), 2) * 100)



    @transaction.atomic
    def repair_parent_references(self, force=False):
        if not force and self.answers.exclude(parent=None).exists():
            # some answers have parent set, so its fine
            return
        for ac in self.answers.all():
            ac.parent = self.__get_parent(ac.full_label)
            ac.save()


    @staticmethod
    def repair_all_parent_references():
        for se in SiteEvaluation.objects.all():
            se.repair_parent_references()


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

    @staticmethod
    def parseJson(ans):
        negative = (ans.startswith("_") and ans.endswith("_"))
        name = ans if not negative else ans[1:-1]
        return (name, negative)


class SortedAnswerChoiceManager(models.Manager):
    def ordered_by_label(self, checklist, *args, **kwargs):
        # get full label order reference
        ref_list = checklist.list_expanded_labels()
        # query
        qs = super(SortedAnswerChoiceManager, self).get_queryset().filter(evaluation__checklist=checklist).filter(*args, **kwargs)
        return sorted(qs, key=lambda ac: ref_list.index(ac.full_label) if ac.full_label in ref_list else len(ref_list))

class AnswerChoice(models.Model):
    NN = 'n.n.'
    evaluation = models.ForeignKey(SiteEvaluation, on_delete=models.CASCADE, related_name="answers")
    full_label = models.SlugField(max_length=100, db_index=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
            related_name="children", blank=True, null=True)
    value = models.CharField(max_length=200, default="", blank=True)
    note = models.CharField(max_length=300, blank=True)
    discussion_needed = models.BooleanField(default=False)
    revision_needed = models.BooleanField(default=False)
    dirty = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    history = HistoricalRecords(
        excluded_fields=[
            'dirty',
        ],
    )
    objects = SortedAnswerChoiceManager()

    def get_full_label(self):
        return self.full_label

    def get_parent_label(self):
        return self.parent.get_full_label() if self.parent else ""

    def is_outdated(self):
        """Checks if the question changed since this answer has been given."""
        if self.last_updated is None:
            return False
        return self.last_updated < self.question.history.latest('history_date').history_date \
            and self.revision_needed

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
        initial = kwargs.get('initial', {})
        if ans and ans.question.answer_type == Question.MULTINOM:
            initial['value'] = json.loads(ans.value) if ans.value != "" else []
        elif ans and ans.question.answer_type == Question.ALTERNATIVES:
            initial['value'] = ans.value or AnswerChoice.NN
        kwargs['initial'] = initial

        super(AnswerForm, self).__init__(*args, **kwargs)

        # adjust value field type to question type
        if ans:
            if ans.question.answer_type == Question.ALTERNATIVES:
                choices = ans.question.get_choices(empty=True)
                self.fields['value'] = forms.ChoiceField(
                        choices=choices,
                        widget=forms.Select if len(choices) > 3 else forms.RadioSelect,
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
        fields = ['value', 'note', 'discussion_needed', 'revision_needed', 'dirty']
        widgets = {
                'note': forms.Textarea(attrs={'rows': '5'}),
        }
        labels = {
            'value': '',
            'note': 'Notes',
        }

