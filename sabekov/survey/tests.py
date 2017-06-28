from django.test import TestCase
from django.contrib.auth.models import User

from .models import *
from .util import importer


class IRRTestCase(TestCase):
    def setUp(self):
        cl = Checklist.objects.create(name="some_checklist")
        self.cat = cl.catalogs.create(
            label="CAT",
            is_top_level=True,
        )
        self.q = self.cat.questions.create(
            label="FOO",
            question_text="Foo?",
            answer_type=Question.INPUT,
        )
        t1 = User.objects.create(username='tester1')
        t2 = User.objects.create(username='tester2')
        t3 = User.objects.create(username='tester3')
        self.s = Site.objects.create(name="example.com")
        self.e1 = SiteEvaluation.objects.create(
            checklist=cl,
            site=self.s,
            tester=t1,
        )
        self.e2 = SiteEvaluation.objects.create(
            checklist=cl,
            site=self.s,
            tester=t2,
        )
        self.e3 = SiteEvaluation.objects.create(
            checklist=cl,
            site=self.s,
            tester=t3,
        )

    def test_differing5050(self):
        self.e1.answers.create(question=self.q, value="1")
        self.e2.answers.create(question=self.q, value="2")
        irr = self.s.calc_inter_rater_relyability(self.e1.checklist)
        self.assertEqual(irr, 0.5)


    def test_identical(self):
        self.e1.answers.create(question=self.q, value="A")
        self.e2.answers.create(question=self.q, value="A")
        irr = self.s.calc_inter_rater_relyability(self.e1.checklist)
        self.assertEqual(irr, 1.0)


    def test_differing_twothird(self):
        self.e1.answers.create(question=self.q, value="A")
        self.e2.answers.create(question=self.q, value="B")
        self.e3.answers.create(question=self.q, value="B")
        irr = self.s.calc_inter_rater_relyability(self.e1.checklist)
        self.assertEqual(irr, 2/3)


    def test_multiple_questions(self):
        q2 = self.cat.questions.create(
            label="BAR",
            question_text="Bar?",
            answer_type=Question.INPUT,
        )
        self.e1.answers.create(question=self.q, value="A")
        self.e2.answers.create(question=self.q, value="B")
        self.e3.answers.create(question=self.q, value="B")
        self.e1.answers.create(question=q2, full_label="BAR", value="B")
        self.e2.answers.create(question=q2, full_label="BAR", value="B")
        self.e3.answers.create(question=q2, full_label="BAR", value="B")
        irr = self.s.calc_inter_rater_relyability(self.e1.checklist)
        self.assertEqual(irr, ((2/3)+1)/2)


class SiteSynonymImportTestCase(TestCase):
    SYNS = """example.de: example.de example.com example.net
        uhh.de: uhh.de uni-hamburg.de"""

    def setUp(self):
        import tempfile
        tmpf = tempfile.NamedTemporaryFile(mode="w", delete=False)
        self.path = tmpf.name
        with tmpf:
            tmpf.write(self.SYNS)

    def test_import(self):
        importer.import_site_synonyms(self.path)
        site_ex = Site.objects.get(name="example.de")
        site_uhh = Site.objects.get(name="uhh.de")
        self.assertEquals(Site.objects.count(), 2)
        self.assertEquals(site_ex.synonyms.count(), 3)
        self.assertEquals(site_uhh.synonyms.count(), 2)

    def test_import_existing_sites(self):
        site_uhh = Site.objects.create(name="uhh.de")
        site_ex = Site.objects.create(name="example.net")
        importer.import_site_synonyms(self.path)
        self.assertEquals(Site.objects.count(), 2)
        self.assertEquals(site_ex.synonyms.count(), 3)
        self.assertEquals(site_uhh.synonyms.count(), 2)
