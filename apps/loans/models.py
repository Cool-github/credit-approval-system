from django.db import models
from apps.customers.models import Customer

class Loan(models.Model):
    loan_id = models.IntegerField(unique=True, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="loans")

    loan_amount = models.FloatField()
    tenure = models.PositiveIntegerField()  # months
    interest_rate = models.FloatField()
    monthly_installment = models.FloatField()

    emis_paid_on_time = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Loan {self.loan_id} - Customer {self.customer.customer_id}"
