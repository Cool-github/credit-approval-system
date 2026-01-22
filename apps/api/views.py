from datetime import date

from dateutil.relativedelta import relativedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.customers.models import Customer
from apps.loans.models import Loan

from services.limit_calculator import calculate_approved_limit
from services.eligibility import evaluate_loan
from drf_spectacular.utils import extend_schema, OpenApiExample

from .serializers import (
    RegisterSerializer,
    EligibilitySerializer,
    LoanCreateSerializer
)

@extend_schema(
    request=RegisterSerializer,
    examples=[
        OpenApiExample(
            "Register Example",
            value={
                "first_name": "John",
                "last_name": "Doe",
                "age": 28,
                "monthly_income": 50000,
                "phone_number": "9999999999"
            },
            request_only=True
        )
    ]
)

# POST /register
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        approved_limit = calculate_approved_limit(data["monthly_income"])

        # Safe customer_id generation (no collision with ingested data)
        last_customer = Customer.objects.order_by("-customer_id").first()
        new_customer_id = last_customer.customer_id + 1 if last_customer else 1

        customer = Customer.objects.create(
            customer_id=new_customer_id,
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

@extend_schema(
    request=EligibilitySerializer,
    examples=[
        OpenApiExample(
            "Eligibility Example",
            value={
                "customer_id": 1,
                "loan_amount": 500000,
                "interest_rate": 10,
                "tenure": 24
            },
            request_only=True
        )
    ]
)

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
            "corrected_interest_rate": result.get(
                "corrected_interest_rate",
                data["interest_rate"]
            ),
            "tenure": data["tenure"],
            "monthly_installment": result.get("monthly_installment", 0)
        })

@extend_schema(
    request=LoanCreateSerializer,
    examples=[
        OpenApiExample(
            "Create Loan Example",
            value={
                "customer_id": 1,
                "loan_amount": 500000,
                "interest_rate": 10,
                "tenure": 24
            },
            request_only=True
        )
    ]
)

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

        result = evaluate_loan(
            customer,
            data["loan_amount"],
            data["interest_rate"],
            data["tenure"]
        )

        if not result["approval"]:
            return Response({
                "loan_id": None,
                "customer_id": customer.customer_id,
                "loan_approved": False,
                "message": result["message"],
                "monthly_installment": 0
            }, status=400)

        # Safe loan_id generation (no collision with ingested data)
        last_loan = Loan.objects.order_by("-loan_id").first()
        new_loan_id = last_loan.loan_id + 1 if last_loan else 1000

        # Real start and end dates based on tenure
        start_date = date.today()
        end_date = start_date + relativedelta(months=data["tenure"])

        loan = Loan.objects.create(
            loan_id=new_loan_id,
            customer=customer,
            loan_amount=data["loan_amount"],
            tenure=data["tenure"],
            interest_rate=result["corrected_interest_rate"],
            monthly_installment=result["monthly_installment"],
            emis_paid_on_time=0,
            start_date=start_date,
            end_date=end_date
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
