/**
 * EquityMetrics Experience - JavaScript Controller
 * Handles scrolling, form submission, preview calculations, and live dashboard updates
 */

// Import calculation functions from calculator.js (reuse existing logic)
// These functions are defined in calculator.js and included via script tag

/**
 * Scroll to form section
 */
function scrollToForm() {
    document.getElementById('input-form').scrollIntoView({
        behavior: 'smooth'
    });
}

/**
 * Update preview calculations in the burgundy panel
 */
function updatePreview() {
    const loanAmount = parseFloat(document.getElementById('form_loan_amount').value);
    const annualRate = parseFloat(document.getElementById('form_annual_rate').value) / 100;
    const loanYears = parseInt(document.getElementById('form_loan_years').value);
    const fixedPeriod = parseInt(document.getElementById('form_fixed_period').value);
    const floatingRate = parseFloat(document.getElementById('form_floating_rate').value) / 100;

    const rawInputs = [loanAmount, annualRate * 100, loanYears, fixedPeriod, floatingRate * 100];
    if (rawInputs.some(v => isNaN(v) || v < 0)) {
        document.getElementById('preview_remaining').textContent = 'All numbers must be positive';
        return;
    }

    if (!loanAmount || !loanYears) {
        document.getElementById('preview_remaining').textContent = '—';
        return;
    }

    const monthlyRate = annualRate / 12;
    const totalMonths = loanYears * 12;
    const fixedMonths = fixedPeriod * 12;

    let balance = loanAmount;
    for (let month = 1; month <= fixedMonths; month++) {
        balance -= Math.abs(ppmt(monthlyRate, month, totalMonths, -loanAmount));
    }

    document.getElementById('preview_remaining').textContent = formatCurrency(balance);
}

/**
 * Handle form submission - Navigate to /dashboard with values
 */
function handleFormSubmit(e) {
    e.preventDefault();

    // Get form values
    const formData = {
        loan_amount: document.getElementById('form_loan_amount').value,
        annual_rate: document.getElementById('form_annual_rate').value,
        loan_years: document.getElementById('form_loan_years').value,
        fixed_period: document.getElementById('form_fixed_period').value,
        floating_rate: document.getElementById('form_floating_rate').value
    };

    // Store in sessionStorage to transfer to dashboard page
    sessionStorage.setItem('loanFormData', JSON.stringify(formData));

    // Navigate to dashboard page
    window.location.href = '/dashboard';
}

/**
 * Initialize the experience
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add form submit listener
    document.getElementById('loan-form').addEventListener('submit', handleFormSubmit);

    // Add input listeners for preview updates
    const formInputs = [
        'form_loan_amount',
        'form_annual_rate',
        'form_loan_years',
        'form_fixed_period',
        'form_floating_rate'
    ];

    formInputs.forEach(id => {
        document.getElementById(id).addEventListener('input', updatePreview);
    });

    // Initialize preview with default values
    updatePreview();
});
