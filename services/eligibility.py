from apps.loans.models import Loan
from .credit_score import calculate_credit_score
from .emi_calculator import calculate_emi


def evaluate_loan(customer, loan_amount, interest_rate, tenure):
    # sum of current EMIs
    current_emis = Loan.objects.filter(customer=customer).values_list("monthly_installment", flat=True)
    total_current_emi = sum(current_emis)

    if total_current_emi > 0.5 * customer.monthly_salary:
        return {
            "approval": False,
            "message": "Current EMIs exceed 50% of monthly salary"
        }

    credit_score = calculate_credit_score(customer)

    if credit_score == 0 or credit_score < 10:
        return {"approval": False, "message": "Low credit score"}

    corrected_interest = interest_rate

    if credit_score <= 30:
        corrected_interest = max(interest_rate, 16.0)
    elif credit_score <= 50:
        corrected_interest = max(interest_rate, 12.0)

    approval = True

    emi = calculate_emi(loan_amount, corrected_interest, tenure)

    return {
        "approval": approval,
        "credit_score": credit_score,
        "interest_rate": interest_rate,
        "corrected_interest_rate": corrected_interest,
        "tenure": tenure,
        "monthly_installment": emi
    }
