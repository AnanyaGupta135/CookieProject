# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask web application for real estate loan analysis. It allows realtors and investors to save properties, model loan amortization schedules across fixed and floating rate periods, explore remaining balances at any point in time, and run DSCR (Debt Service Coverage Ratio) checks.

## Running the Application

```bash
python app.py
```

The server runs on http://localhost:5001 by default.

## Deployment

Deployed on Render. Pushing to the `main` branch on GitHub triggers an automatic redeploy. Configuration is in `render.yaml`. The start command is `gunicorn app:app`.

> **Note**: Render's free tier uses an ephemeral filesystem. The SQLite database (`properties.db`) will be lost on redeploy unless a Render Persistent Disk is attached and `DB_PATH` is set to a path on that disk.

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

### SQLite Persistence (database.py)

Properties are persisted in a SQLite database. `database.init_db()` is called at app startup.

- **DB_PATH**: read from the `DB_PATH` environment variable, defaulting to `properties.db` in the project root
- **Functions**: `init_db()`, `list_properties()`, `get_property(id)`, `create_property(...)`, `update_property(id, ...)`, `delete_property(id)`
- `create_property` returns the new row by calling `get_property` **after** the `with` block exits so the INSERT is committed before the second connection reads it

### Application Routes

- `/` — Portfolio landing page listing all saved properties (landing.html)
- `/property/new` — GET renders new property form; POST validates and creates, redirects to dashboard
- `/property/<id>` — Renders dashboard.html with the saved property's values pre-loaded
- `/property/<id>/save` — POST JSON body; updates the property and returns updated record as JSON
- `/property/<id>/delete` — POST; deletes and redirects to `/`
- `/calculate` — POST endpoint for form submission, returns results.html
- `/dashboard` — Standalone live dashboard (no saved property)
- `/experience` — Marketing-style scrolling page

### Template Structure

- **landing.html**: Portfolio view — lists saved properties as cards with name, loan amount, rates, term; "Add Property" button; delete (×) per card; empty state
- **property_new.html**: Two-panel form for creating a property; validation error banner re-populates fields on failure
- **dashboard.html**: Real-time calculator (see Dashboard section below)
- **results.html**: Server-rendered results page showing payment schedules
- **experience.html**: Marketing-style multi-section scrolling page (fonts: Playfair Display, Montserrat, Lora; palette: burgundy #5B161B, gold #A68B67, cream #F9F8F4)
- **index.html**: Legacy simple form-submit interface (still accessible at `/calculate`)

### Visual Style

The portfolio-facing pages (landing, property_new) use the same design language as experience.html:
- **Fonts**: Playfair Display (headings), Montserrat (labels/buttons), Lora (body)
- **Palette**: `--burgundy: #5B161B`, `--gold: #A68B67`, `--cream: #F9F8F4`
- Buttons: burgundy fill, cream text, uppercase Montserrat, no border-radius

The dashboard retains its own minimal system-font style.

### Data Flow

1. User inputs: loan_amount, annual_rate, loan_years, fixed_period, floating_rate
2. Rates are converted from percentages to decimals (divide by 100)
3. Calculations iterate month-by-month, then aggregate to yearly summaries
4. Each year returns: principal, interest, total payment, remaining balance, rate_type

## Dashboard Detail (dashboard.html + calculator.js)

### Input Pre-population Priority

On page load, `calculator.js` populates inputs in this order:
1. `window.PROPERTY` global (injected by the server when viewing a saved property)
2. `sessionStorage['loanFormData']` (set by the experience page form)
3. Hardcoded defaults

### Property Mode (when `property` is passed from server)

- The server injects `var PROPERTY = <json>;` before `calculator.js` loads
- Header shows the property name and a "Save Changes" button
- Clicking "Save Changes" POSTs current input values as JSON to `/property/<id>/save`
- A "Saved ✓" toast appears briefly on success
- "← Back to Portfolio" link appears in the header

### Dashboard Sections

1. **Summary** — echoes the five input values as formatted displays
2. **Key Metrics Post Loan Term** — remaining principal, years left, principal paid at end of fixed period
3. **Remaining Balance Explorer** — slider (year 0 → loan term) + number input; shows remaining balance and total principal paid at the selected year. Year 0 = full loan amount / $0 paid. Driven by `lastYearlyPayments` (module-level cache updated on every `updateResults()` call).
4. **DSCR Calculator** — standalone interest-only DSCR check:
   - Formula: `DSCR = Annual Rental Income ÷ (Loan Amount × Stressed Rate)`
   - Inputs: rental income, stressed rate (%), required DSCR threshold
   - Loan amount is read from the main input panel automatically
   - Displays calculated DSCR, required DSCR, annual debt service
   - Green verdict banner (✓) if calculated ≥ required; burgundy (✗) with shortfall if not
5. **Complete Yearly Payment Schedule** — full amortization table; fixed-period end year highlighted

## Key Implementation Details

### Month-by-Month Calculation

Although the UI displays yearly data, calculations happen at monthly granularity:
- Annual rate divided by 12 for monthly rate
- Years multiplied by 12 for total months
- Monthly payments summed to produce yearly aggregates

### Rate Type Tracking

Each payment period is tagged with `rate_type: 'fixed'` or `rate_type: 'floating'`. The fixed period end year is highlighted in the payment schedule table.

### Input Validation

- Fixed period cannot exceed total loan term
- All amounts must be positive
- Rates must be non-negative (zero rate is handled as a special case in ppmt/ipmt)
- `property_new.html` uses `step="any"` on loan amount to allow any positive number (not just multiples of 1000)
