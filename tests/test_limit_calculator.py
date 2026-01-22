from django.test import SimpleTestCase
from services.limit_calculator import calculate_approved_limit

class TestLimitCalculator(SimpleTestCase):

    def test_limit_rounding(self):
        limit = calculate_approved_limit(33333)
        self.assertEqual(limit, 1200000)  # 36*33333=1199988 → rounds to 1200000
