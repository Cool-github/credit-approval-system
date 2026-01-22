from django.test import TestCase
from apps.customers.models import Customer
from apps.loans.models import Loan


class BaseTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            customer_id=999,
            first_name="Test",
            last_name="User",
            age=30,
            phone_number="9999999999",
            monthly_salary=50000,
            approved_limit=1800000,
            current_debt=0
        )
