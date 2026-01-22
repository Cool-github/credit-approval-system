import pandas as pd
from celery import shared_task
from django.db import transaction

from apps.customers.models import Customer
from apps.loans.models import Loan
from .mappings import CUSTOMER_COLUMN_MAPPING, LOAN_COLUMN_MAPPING


@shared_task
def ingest_customers(file_path):
    df = pd.read_excel(file_path)
    df = df.rename(columns=CUSTOMER_COLUMN_MAPPING)

    customers = []
    for _, row in df.iterrows():
        customers.append(
            Customer(
                customer_id=int(row["customer_id"]),
                first_name=row["first_name"],
                last_name=row["last_name"],
                age=int(row["age"]),
                phone_number=str(row["phone_number"]),
                monthly_salary=int(row["monthly_salary"]),
                approved_limit=int(row["approved_limit"]),
                current_debt=0,
            )
        )

    with transaction.atomic():
        Customer.objects.bulk_create(customers, ignore_conflicts=True)

    return f"{len(customers)} customers ingested"


@shared_task
def ingest_loans(_, file_path):
    df = pd.read_excel(file_path)
    df = df.rename(columns=LOAN_COLUMN_MAPPING)

    loans = []
    for _, row in df.iterrows():
        customer = Customer.objects.get(customer_id=int(row["customer_id"]))

        loans.append(
            Loan(
                loan_id=int(row["loan_id"]),
                customer=customer,
                loan_amount=float(row["loan_amount"]),
                tenure=int(row["tenure"]),
                interest_rate=float(row["interest_rate"]),
                monthly_installment=float(row["monthly_installment"]),
                emis_paid_on_time=int(row["emis_paid_on_time"]),
                start_date=row["start_date"],
                end_date=row["end_date"],
            )
        )

    with transaction.atomic():
        Loan.objects.bulk_create(loans, ignore_conflicts=True)

    return f"{len(loans)} loans ingested"
