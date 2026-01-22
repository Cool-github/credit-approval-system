import math

def calculate_approved_limit(monthly_salary: int) -> int:
    """
    approved_limit = 36 * monthly_salary rounded to nearest lakh
    """
    raw_limit = 36 * monthly_salary
    rounded = int(round(raw_limit / 100000)) * 100000
    return rounded
