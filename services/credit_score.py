from datetime import date
from apps.loans.models import Loan
from apps.customers.models import Customer


def calculate_credit_score(customer: Customer) -> int:
    loans = Loan.objects.filter(customer=customer)

    if not loans.exists():
        return 50  # neutral score for no history

    total_loans = loans.count()
    total_volume = sum(l.loan_amount for l in loans)
    total_emis_paid = sum(l.emis_paid_on_time for l in loans)

    current_year = date.today().year
    current_year_loans = loans.filter(start_date__year=current_year).count()

    # current total debt check
    if total_volume > customer.approved_limit:
        return 0

    # Build score
    score = 0

    # Payment discipline (max 40)
    score += min(40, total_emis_paid)

    # Loan count factor (max 20)
    score += min(20, total_loans * 2)

    # Current year activity (max 20)
    score += min(20, current_year_loans * 5)

    # Loan volume factor (max 20)
    volume_ratio = total_volume / customer.approved_limit
    score += int((1 - volume_ratio) * 20)

    return max(0, min(100, score))
