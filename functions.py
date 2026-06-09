"""
PPMT Function - Principal Payment Calculator
Calculates the principal portion of a loan payment for a specific period.
"""

def ppmt(rate, per, nper, pv):
    """
    Calculate the principal portion of a payment for a specific period.

    Args
        rate: Interest rate per period (e.g., annual rate / 12 for monthly)
        per: The specific payment period to calculate (1-indexed, e.g., 1 for first period)
        nper: Total number of payment periods
        pv: Present value (initial loan amount, should be negative for borrowing)

    Returns:
        float: Principal portion of the payment for the specified period

    """

    # Validate inputs
    if per < 1 or per > nper:
        raise ValueError(f"Period (per={per}) must be between 1 and {nper}")

    # Handle edge case: if rate is 0, there's no interest
    if rate == 0:
        # With no interest, each payment is just principal divided equally
        return -pv / nper

    # STEP 1: Calculate the fixed payment amount (PMT)
    # Formula: PMT = PV × [rate × (1 + rate)^nper] / [(1 + rate)^nper - 1]
    rate_factor = (1 + rate) ** nper
    pmt = pv * (rate * rate_factor) / (rate_factor - 1)

    # STEP 2: Calculate the remaining balance at the START of period 'per'
    # This represents how much principal is still owed before this payment
    # Formula: Balance = PV × (1 + rate)^(per-1) - PMT × [((1 + rate)^(per-1) - 1) / rate]
    if per == 1:
        # At the start of period 1, the balance is just the original loan amount
        balance_at_start = pv
    else:
        # For later periods, calculate using the future value formula
        periods_elapsed = per - 1
        growth_factor = (1 + rate) ** periods_elapsed

        # Original loan + interest
        loan_with_interest = pv * growth_factor

        # Sum of all previous payments with their accumulated interest
        payments_with_interest = pmt * ((growth_factor - 1) / rate)

        balance_at_start = loan_with_interest - payments_with_interest

    # STEP 3: Calculate the interest portion of this period's payment
    # Interest is charged on the outstanding balance
    interest_payment = balance_at_start * rate

    # STEP 4: Calculate the principal portion
    # Whatever isn't interest goes toward paying down the principal
    principal_payment = pmt - interest_payment

    return principal_payment


def ipmt(rate, per, nper, pv):
    """
    Calculate the interest portion of a payment for a specific period.

    Args:
        rate: Interest rate per period (e.g., annual rate / 12 for monthly)
        per: The specific payment period to calculate (1-indexed, e.g., 1 for first period)
        nper: Total number of payment periods
        pv: Present value (initial loan amount, should be negative for borrowing)

    Returns:
        float: Interest portion of the payment for the specified period
    """

    # Validate inputs
    if per < 1 or per > nper:
        raise ValueError(f"Period (per={per}) must be between 1 and {nper}")

    # Handle edge case: if rate is 0, there's no interest
    if rate == 0:
        # With no interest rate, there's no interest payment
        return 0

    # STEP 1: Calculate the fixed payment amount (PMT)
    # We need this to calculate the balance at the start of the period
    # Formula: PMT = PV × [rate × (1 + rate)^nper] / [(1 + rate)^nper - 1]
    rate_factor = (1 + rate) ** nper
    pmt = pv * (rate * rate_factor) / (rate_factor - 1)

    # STEP 2: Calculate the remaining balance at the START of period 'per'
    # This represents how much principal is still owed before this payment
    # Formula: Balance = PV × (1 + rate)^(per-1) - PMT × [((1 + rate)^(per-1) - 1) / rate]
    if per == 1:
        # At the start of period 1, the balance is just the original loan amount
        balance_at_start = pv
    else:
        # For later periods, calculate using the future value formula
        periods_elapsed = per - 1
        growth_factor = (1 + rate) ** periods_elapsed

        # Original loan grown with interest
        loan_with_interest = pv * growth_factor

        # Sum of all previous payments with their accumulated interest
        payments_with_interest = pmt * ((growth_factor - 1) / rate)

        balance_at_start = loan_with_interest - payments_with_interest

    # STEP 3: Calculate the interest portion of this period's payment
    # Interest is simply the outstanding balance multiplied by the interest rate
    interest_payment = balance_at_start * rate

    return interest_payment



# Example usage and demonstration
if __name__ == "__main__":
    print("PPMT Function Demonstration")
    print("=" * 60)

    # Example: $10,000 loan at 5% annual interest, paid monthly over 2 years
    loan_amount = 8500000  # Negative because it's money borrowed
    annual_rate = 0.03
    monthly_rate = annual_rate / 12
    years = 30
    total_payments = years*12

    print(f"\nLoan Details:")
    print(f"  Loan Amount: ${abs(loan_amount):,.2f}")
    print(f"  Annual Interest Rate: {annual_rate * 100}%")
    print(f"  Monthly Interest Rate: {monthly_rate * 100:.4f}%")
    print(f"  Loan Term: {years} years ({total_payments} months)")

    # Calculate a few periods showing both principal and interest
    print(f"\n{'Period':<8} {'Principal':<14} {'Interest':<14} {'Total Payment':<14}")
    print("-" * 65)
    principalsum = []
    interestsum = []
    totalsum = []

    for period in [12, 24, 36, 48, 60, 72, 84]:
        psum = 0
        isum = 0
        tsum = 0
        for i in range (12):
            principal = ppmt(monthly_rate, period, total_payments, loan_amount)
            interest = ipmt(monthly_rate, period, total_payments, loan_amount)
            total = principal + interest
            psum += principal
            isum += interest
            tsum += total

        principalsum.append(f"${abs(psum):,.2f}")
        interestsum.append(f"${abs(isum):,.2f}")
        if period == 12:
            totalsum.append(f"${abs(tsum):,.2f}")
            #print(f"{period:<8} ${abs(principal):<13,.2f} ${abs(interest):<13,.2f} ${abs(total):<13,.2f}")
    print("principal payment: ", principalsum)
    print("interest payment: ", interestsum)
    print("total payment: ", totalsum)

    #confirming principal payment finishes at starting sum
    checkp = 0
    checki = 0
    for period in range(1,total_payments+1):
        checkp += ppmt(monthly_rate, period, total_payments, loan_amount)
        checki += ipmt(monthly_rate, period, total_payments, loan_amount)
    
    print ("check: ", checkp, checki)
