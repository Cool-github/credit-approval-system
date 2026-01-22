from django.test import SimpleTestCase
from services.emi_calculator import calculate_emi

class TestEmiCalculator(SimpleTestCase):

    def test_zero_interest(self):
        emi = calculate_emi(120000, 0, 12)
        self.assertEqual(emi, 10000.00)

    def test_positive_interest(self):
        emi = calculate_emi(100000, 12, 12)
        self.assertTrue(emi > 8000)
