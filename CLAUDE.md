# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask web application for calculating loan payments with fixed and floating interest rate periods. The application provides three different interfaces for analyzing loan amortization schedules, focusing on the transition between fixed-rate and floating-rate periods.

## Running the Application

```bash
python app.py
```

The server runs on http://localhost:5000 by default.

## Architecture

### Core Calculation Logic

The application implements custom financial functions (`ppmt` and `ipmt`) in both Python and JavaScript:

- **functions.py**: Python implementation of principal payment (ppmt) and interest payment (ipmt) calculators
- **static/calculator.js**: JavaScript port of the same functions for client-side calculations

Both implementations use identical formulas:
- Fixed payment calculation: `PMT = PV × [rate × (1 + rate)^nper] / [(1 + rate)^nper - 1]`
- Balance tracking with compound interest over periods
- Separation of principal vs interest portions of each payment

### Two-Phase Loan Calculation

The key business logic in `calculate_yearly_payments()` (app.py:6-80) handles loans that transition from fixed to floating rates:

1. **Phase 1 (Fixed Rate)**: Calculates payments using the fixed rate for the initial period
2. **Phase 2 (Floating Rate)**: Treats remaining balance as a new loan with the floating rate

Critical detail: When transitioning to floating rate, the remaining principal becomes the new loan amount (`remaining_balance_at_switch`), and payments are recalculated based on the remaining years with the new rate.

### Application Routes

- `/` - Simple form-based calculator (index.html)
- `/calculate` - POST endpoint for form submission, returns results.html
- `/dashboard` - Live dashboard with real-time JavaScript calculations (dashboard.html)
- `/experience` - Multi-page scrolling experience with elegant design (experience.html)

The `/dashboard` route provides the most interactive experience, using client-side JavaScript for instant recalculation without server round-trips.

### Template Structure

- **index.html**: Traditional form-submit interface
- **results.html**: Server-rendered results page showing payment schedules
- **dashboard.html**: Real-time calculator with sticky input panel and live-updating results
- **experience.html**: Marketing-style multi-section scrolling page (uses custom fonts: Playfair Display, Montserrat, Lora)

### Data Flow

1. User inputs: loan_amount, annual_rate, loan_years, fixed_period, floating_rate
2. Rates are converted from percentages to decimals (divide by 100)
3. Calculations iterate month-by-month, then aggregate to yearly summaries
4. Each year returns: principal, interest, total payment, remaining balance, rate_type

The dashboard uses sessionStorage to pass form data from the experience page to preserve user inputs across page transitions.

## Key Implementation Details

### Month-by-Month Calculation

Although the UI displays yearly data, calculations happen at monthly granularity:
- Annual rate divided by 12 for monthly rate
- Years multiplied by 12 for total months
- Monthly payments summed to produce yearly aggregates

### Rate Type Tracking

Each payment period is tagged with `rate_type: 'fixed'` or `rate_type: 'floating'` to distinguish which rate was used. The fixed period year is highlighted in the payment schedule table.

### Input Validation

- Fixed period cannot exceed total loan term
- All amounts must be positive
- Rates must be non-negative (zero rate is handled as a special case)
