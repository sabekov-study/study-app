from django.test import TestCase
from django.contrib.auth.models import User

from .models import *


class IRRTestCase(TestCase):
    def setUp(self):
        cl = Checklist.objects.create(name="some_checklist")
        cat = cl.catalogs.create(
            label="CAT",
            is_top_level=True,
        )
        self.q = cat.questions.create(
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
