from rest_framework.test import APITestCase
from apps.customers.models import Customer

class TestEligibilityAPI(APITestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            customer_id=1,
            first_name="A",
            last_name="B",
            age=30,
            phone_number="7777777777",
            monthly_salary=50000,
            approved_limit=1800000,
            current_debt=0
        )

    def test_check_eligibility(self):
        response = self.client.post("/check-eligibility", {
            "customer_id": 1,
            "loan_amount": 200000,
            "interest_rate": 10,
            "tenure": 12
        }, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("approval", response.data)
