from django.core.management.base import BaseCommand
from celery import chain
from apps.ingestion.tasks import ingest_customers, ingest_loans


class Command(BaseCommand):
    help = "Trigger background ingestion of Excel data"

    def handle(self, *args, **kwargs):
        customer_file = "/app/data/customer_data.xlsx"
        loan_file = "/app/data/loan_data.xlsx"

        chain(
            ingest_customers.s(customer_file),
            ingest_loans.s(loan_file)
        ).delay()

        self.stdout.write(self.style.SUCCESS("Chained ingestion tasks triggered"))
