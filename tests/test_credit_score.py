from tests.base import BaseTestCase
from services.credit_score import calculate_credit_score

class TestCreditScore(BaseTestCase):

    def test_no_loans_neutral_score(self):
        score = calculate_credit_score(self.customer)
        self.assertEqual(score, 50)
