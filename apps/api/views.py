from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.customers.models import Customer
from apps.loans.models import Loan
from services.limit_calculator import calculate_approved_limit
from services.eligibility import evaluate_loan
from services.emi_calculator import calculate_emi

from .serializers import (
    RegisterSerializer,
    EligibilitySerializer,
    LoanCreateSerializer
)


# POST /register
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        approved_limit = calculate_approved_limit(data["monthly_income"])

        customer = Customer.objects.create(
            customer_id=Customer.objects.count() + 1,
            first_name=data["first_name"],
            last_name=data["last_name"],
            age=data["age"],
            monthly_salary=data["monthly_income"],
            phone_number=data["phone_number"],
            approved_limit=approved_limit,
            current_debt=0
        )

        return Response({
            "customer_id": customer.customer_id,
            "name": f"{customer.first_name} {customer.last_name}",
            "age": customer.age,
            "monthly_income": customer.monthly_salary,
            "approved_limit": customer.approved_limit,
            "phone_number": customer.phone_number
        }, status=status.HTTP_201_CREATED)


# POST /check-eligibility
class CheckEligibilityView(APIView):
    def post(self, request):
        serializer = EligibilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            customer = Customer.objects.get(customer_id=data["customer_id"])
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)

        result = evaluate_loan(
            customer,
            data["loan_amount"],
            data["interest_rate"],
            data["tenure"]
        )

        return Response({
            "customer_id": customer.customer_id,
            "approval": result["approval"],
            "interest_rate": data["interest_rate"],
            "corrected_interest_rate": result.get("corrected_interest_rate", data["interest_rate"]),
            "tenure": data["tenure"],
            "monthly_installment": result.get("monthly_installment", 0)
        })


# POST /create-loan
class CreateLoanView(APIView):
    def post(self, request):
        serializer = LoanCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            customer = Customer.objects.get(customer_id=data["customer_id"])
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)

        result = evaluate_loan(customer, data["loan_amount"], data["interest_rate"], data["tenure"])

        if not result["approval"]:
            return Response({
                "loan_id": None,
                "customer_id": customer.customer_id,
                "loan_approved": False,
                "message": result["message"],
                "monthly_installment": 0
            }, status=400)

        # create loan
        loan = Loan.objects.create(
            loan_id=Loan.objects.count() + 1000,
            customer=customer,
            loan_amount=data["loan_amount"],
            tenure=data["tenure"],
            interest_rate=result["corrected_interest_rate"],
            monthly_installment=result["monthly_installment"],
            emis_paid_on_time=0,
            start_date="2026-01-01",
            end_date="2026-12-31"
        )

        return Response({
            "loan_id": loan.loan_id,
            "customer_id": customer.customer_id,
            "loan_approved": True,
            "message": "Loan approved",
            "monthly_installment": loan.monthly_installment
        }, status=201)


# GET /view-loan/<loan_id>
class ViewLoan(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(loan_id=loan_id)
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found"}, status=404)

        customer = loan.customer

        return Response({
            "loan_id": loan.loan_id,
            "customer": {
                "id": customer.customer_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone_number": customer.phone_number,
                "age": customer.age
            },
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_installment,
            "tenure": loan.tenure
        })


# GET /view-loans/<customer_id>
class ViewLoansByCustomer(APIView):
    def get(self, request, customer_id):
        loans = Loan.objects.filter(customer__customer_id=customer_id)

        data = []
        for loan in loans:
            repayments_left = loan.tenure - loan.emis_paid_on_time
            data.append({
                "loan_id": loan.loan_id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_installment,
                "repayments_left": repayments_left
            })

        return Response(data)
