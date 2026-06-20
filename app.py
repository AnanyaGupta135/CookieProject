from flask import Flask, render_template, request, redirect, url_for, jsonify
from functions import ppmt, ipmt
import database

app = Flask(__name__)
database.init_db()

def calculate_yearly_payments(loan_amount, annual_rate, years, fixed_period, floating_rate):
    """
    Calculate yearly payment breakdown for a loan with fixed and floating rate periods.

    Args:
        loan_amount: Initial loan amount
        annual_rate: Fixed annual interest rate (for fixed period)
        years: Total loan term in years
        fixed_period: Number of years at fixed rate
        floating_rate: Floating annual interest rate (after fixed period)

    Returns a list of dictionaries with yearly payment details.
    """
    yearly_data = []
    cumulative_principal = 0

    # Phase 1: Fixed rate period (years 1 to fixed_period)
    if fixed_period > 0:
        fixed_monthly_rate = annual_rate / 12
        fixed_total_months = years * 12

        for year in range(1, fixed_period + 1):
            yearly_principal = 0
            yearly_interest = 0

            # Sum up 12 months for this year using fixed rate
            for month in range((year-1)*12 + 1, year*12 + 1):
                yearly_principal += abs(ppmt(fixed_monthly_rate, month, fixed_total_months, -loan_amount))
                yearly_interest += abs(ipmt(fixed_monthly_rate, month, fixed_total_months, -loan_amount))

            cumulative_principal += yearly_principal
            remaining_balance = loan_amount - cumulative_principal

            yearly_data.append({
                'year': year,
                'principal': yearly_principal,
                'interest': yearly_interest,
                'total': yearly_principal + yearly_interest,
                'remaining_balance': max(0, remaining_balance),
                'rate_type': 'fixed'
            })

    # Phase 2: Floating rate period (years fixed_period+1 to end)
    if fixed_period < years:
        # Remaining balance becomes the new "loan" for floating period
        remaining_balance_at_switch = loan_amount - cumulative_principal
        floating_years = years - fixed_period
        floating_monthly_rate = floating_rate / 12
        floating_total_months = floating_years * 12

        for year in range(fixed_period + 1, years + 1):
            yearly_principal = 0
            yearly_interest = 0

            # Calculate month number within the floating period
            floating_year_index = year - fixed_period

            # Sum up 12 months for this year using floating rate
            for month in range((floating_year_index-1)*12 + 1, floating_year_index*12 + 1):
                yearly_principal += abs(ppmt(floating_monthly_rate, month, floating_total_months, -remaining_balance_at_switch))
                yearly_interest += abs(ipmt(floating_monthly_rate, month, floating_total_months, -remaining_balance_at_switch))

            cumulative_principal += yearly_principal
            remaining_balance = loan_amount - cumulative_principal

            yearly_data.append({
                'year': year,
                'principal': yearly_principal,
                'interest': yearly_interest,
                'total': yearly_principal + yearly_interest,
                'remaining_balance': max(0, remaining_balance),
                'rate_type': 'floating'
            })

    return yearly_data


@app.route('/')
def index():
    properties = database.list_properties()
    return render_template('landing.html', properties=properties)


@app.route('/property/new', methods=['GET', 'POST'])
def property_new():
    if request.method == 'POST':
        try:
            loan_amount = float(request.form['loan_amount'])
            annual_rate = float(request.form['annual_rate'])
            loan_years = int(request.form['loan_years'])
            fixed_period = int(request.form['fixed_period'])
            floating_rate = float(request.form['floating_rate'])

            if fixed_period > loan_years:
                raise ValueError("Fixed period cannot exceed loan term.")
            if loan_amount <= 0 or loan_years <= 0:
                raise ValueError("Loan amount and term must be positive.")
            if annual_rate < 0 or floating_rate < 0:
                raise ValueError("Rates must be non-negative.")

            prop = database.create_property(
                name=request.form['name'],
                loan_amount=loan_amount,
                annual_rate=annual_rate,
                loan_years=loan_years,
                fixed_period=fixed_period,
                floating_rate=floating_rate,
            )
            return redirect(url_for('property_view', id=prop['id']))
        except ValueError as e:
            return render_template('property_new.html', error=str(e), form=request.form)
    return render_template('property_new.html')


@app.route('/property/<int:id>')
def property_view(id):
    prop = database.get_property(id)
    if prop is None:
        return "Property not found", 404
    return render_template('dashboard.html', property=prop)


@app.route('/property/<int:id>/save', methods=['POST'])
def property_save(id):
    data = request.get_json(force=True)
    prop = database.update_property(
        id,
        name=data.get('name'),
        loan_amount=data.get('loan_amount'),
        annual_rate=data.get('annual_rate'),
        loan_years=data.get('loan_years'),
        fixed_period=data.get('fixed_period'),
        floating_rate=data.get('floating_rate'),
    )
    if prop is None:
        return jsonify({'error': 'Property not found'}), 404
    return jsonify(prop)


@app.route('/property/<int:id>/delete', methods=['POST'])
def property_delete(id):
    database.delete_property(id)
    return redirect(url_for('index'))


@app.route('/calculate', methods=['POST'])
def calculate():
    """Process form data and display results."""
    try:
        # Get form data
        loan_amount = float(request.form['loan_amount'])
        annual_rate = float(request.form['annual_rate']) / 100  # Convert percentage to decimal
        loan_years = int(request.form['loan_years'])
        fixed_period = int(request.form['fixed_period'])
        floating_rate = float(request.form['floating_rate']) / 100  # Convert percentage to decimal

        # Validation
        if fixed_period > loan_years:
            return "Error: Fixed period cannot exceed loan term", 400
        if loan_amount <= 0 or annual_rate < 0 or loan_years <= 0 or floating_rate < 0:
            return "Error: Please enter valid positive numbers", 400

        # Calculate yearly payments
        yearly_payments = calculate_yearly_payments(loan_amount, annual_rate, loan_years, fixed_period, floating_rate)

        # Get data at fixed period end
        fixed_end_data = yearly_payments[fixed_period - 1] if fixed_period > 0 else yearly_payments[0]
        remaining_balance = fixed_end_data['remaining_balance']
        years_left = loan_years - fixed_period

        # Get payments after fixed period
        payments_after_fixed = yearly_payments[fixed_period:] if fixed_period < loan_years else []

        return render_template('results.html',
                             loan_amount=loan_amount,
                             annual_rate=annual_rate * 100,  # Convert back to percentage for display
                             floating_rate=floating_rate * 100,  # Convert back to percentage for display
                             loan_years=loan_years,
                             fixed_period=fixed_period,
                             yearly_payments=yearly_payments,
                             remaining_balance=remaining_balance,
                             years_left=years_left,
                             payments_after_fixed=payments_after_fixed)

    except ValueError:
        return "Error: Invalid input. Please enter numeric values.", 400
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route('/dashboard')
def dashboard():
    """Render the live dashboard with real-time calculations."""
    return render_template('dashboard.html')


@app.route('/experience')
def experience():
    """Render the multi-page scrolling experience with elegant design."""
    return render_template('experience.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
