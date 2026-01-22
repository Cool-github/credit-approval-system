import math

def calculate_emi(principal: float, annual_interest_rate: float, tenure_months: int) -> float:
    r = annual_interest_rate / (12 * 100)
    n = tenure_months

    if r == 0:
        return round(principal / n, 2)

    emi = principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
    return round(emi, 2)
