from tests.base import BaseTestCase
from services.eligibility import evaluate_loan

class TestEligibility(BaseTestCase):

    def test_approval_basic_case(self):
        result = evaluate_loan(self.customer, 100000, 10, 12)
        self.assertTrue(result["approval"])
        self.assertIn("monthly_installment", result)
