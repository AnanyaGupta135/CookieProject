/**
 * Loan Payment Calculator - JavaScript Implementation
 * Converts Python ppmt/ipmt functions to JavaScript for client-side calculations
 */

/**
 * Calculate the principal portion of a payment for a specific period
 * @param {number} rate - Interest rate per period
 * @param {number} per - The specific payment period (1-indexed)
 * @param {number} nper - Total number of payment periods
 * @param {number} pv - Present value (loan amount, negative for borrowing)
 * @returns {number} Principal portion of the payment
 */
function ppmt(rate, per, nper, pv) {
    if (per < 1 || per > nper) {
        throw new Error(`Period (per=${per}) must be between 1 and ${nper}`);
    }

    if (rate === 0) {
        return -pv / nper;
    }

    const rateFactor = Math.pow(1 + rate, nper);
    const pmt = pv * (rate * rateFactor) / (rateFactor - 1);

    let balanceAtStart;
    if (per === 1) {
        balanceAtStart = pv;
    } else {
        const periodsElapsed = per - 1;
        const growthFactor = Math.pow(1 + rate, periodsElapsed);
        const loanWithInterest = pv * growthFactor;
        const paymentsWithInterest = pmt * ((growthFactor - 1) / rate);
        balanceAtStart = loanWithInterest - paymentsWithInterest;
    }

    const interestPayment = balanceAtStart * rate;
    const principalPayment = pmt - interestPayment;

    return principalPayment;
}

/**
 * Calculate the interest portion of a payment for a specific period
 * @param {number} rate - Interest rate per period
 * @param {number} per - The specific payment period (1-indexed)
 * @param {number} nper - Total number of payment periods
 * @param {number} pv - Present value (loan amount, negative for borrowing)
 * @returns {number} Interest portion of the payment
 */
function ipmt(rate, per, nper, pv) {
    if (per < 1 || per > nper) {
        throw new Error(`Period (per=${per}) must be between 1 and ${nper}`);
    }

    if (rate === 0) {
        return 0;
    }

    const rateFactor = Math.pow(1 + rate, nper);
    const pmt = pv * (rate * rateFactor) / (rateFactor - 1);

    let balanceAtStart;
    if (per === 1) {
        balanceAtStart = pv;
    } else {
        const periodsElapsed = per - 1;
        const growthFactor = Math.pow(1 + rate, periodsElapsed);
        const loanWithInterest = pv * growthFactor;
        const paymentsWithInterest = pmt * ((growthFactor - 1) / rate);
        balanceAtStart = loanWithInterest - paymentsWithInterest;
    }

    const interestPayment = balanceAtStart * rate;
    return interestPayment;
}

/**
 * Calculate yearly payment breakdown for a loan with fixed and floating rate periods
 * @param {number} loanAmount - Initial loan amount
 * @param {number} annualRate - Fixed annual interest rate (as decimal, e.g., 0.05 for 5%)
 * @param {number} years - Total loan term in years
 * @param {number} fixedPeriod - Number of years at fixed rate
 * @param {number} floatingRate - Floating annual interest rate (as decimal)
 * @returns {Array} Array of yearly payment objects
 */
function calculateYearlyPayments(loanAmount, annualRate, years, fixedPeriod, floatingRate) {
    const yearlyData = [];
    let cumulativePrincipal = 0;

    // Phase 1: Fixed rate period
    if (fixedPeriod > 0) {
        const fixedMonthlyRate = annualRate / 12;
        const fixedTotalMonths = years * 12;

        for (let year = 1; year <= fixedPeriod; year++) {
            let yearlyPrincipal = 0;
            let yearlyInterest = 0;

            // Sum up 12 months for this year using fixed rate
            for (let month = (year - 1) * 12 + 1; month <= year * 12; month++) {
                yearlyPrincipal += Math.abs(ppmt(fixedMonthlyRate, month, fixedTotalMonths, -loanAmount));
                yearlyInterest += Math.abs(ipmt(fixedMonthlyRate, month, fixedTotalMonths, -loanAmount));
            }

            cumulativePrincipal += yearlyPrincipal;
            const remainingBalance = Math.max(0, loanAmount - cumulativePrincipal);

            yearlyData.push({
                year: year,
                principal: yearlyPrincipal,
                interest: yearlyInterest,
                total: yearlyPrincipal + yearlyInterest,
                remainingBalance: remainingBalance,
                rateType: 'fixed'
            });
        }
    }

    // Phase 2: Floating rate period
    if (fixedPeriod < years) {
        const remainingBalanceAtSwitch = loanAmount - cumulativePrincipal;
        const floatingYears = years - fixedPeriod;
        const floatingMonthlyRate = floatingRate / 12;
        const floatingTotalMonths = floatingYears * 12;

        for (let year = fixedPeriod + 1; year <= years; year++) {
            let yearlyPrincipal = 0;
            let yearlyInterest = 0;

            const floatingYearIndex = year - fixedPeriod;

            // Sum up 12 months for this year using floating rate
            for (let month = (floatingYearIndex - 1) * 12 + 1; month <= floatingYearIndex * 12; month++) {
                yearlyPrincipal += Math.abs(ppmt(floatingMonthlyRate, month, floatingTotalMonths, -remainingBalanceAtSwitch));
                yearlyInterest += Math.abs(ipmt(floatingMonthlyRate, month, floatingTotalMonths, -remainingBalanceAtSwitch));
            }

            cumulativePrincipal += yearlyPrincipal;
            const remainingBalance = Math.max(0, loanAmount - cumulativePrincipal);

            yearlyData.push({
                year: year,
                principal: yearlyPrincipal,
                interest: yearlyInterest,
                total: yearlyPrincipal + yearlyInterest,
                remainingBalance: remainingBalance,
                rateType: 'floating'
            });
        }
    }

    return yearlyData;
}

/**
 * Format number as currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

/**
 * Update the results display with new calculations
 */
function updateResults() {
    // Get input values
    const loanAmount = parseFloat(document.getElementById('loan_amount').value);
    const annualRate = parseFloat(document.getElementById('annual_rate').value) / 100;
    const loanYears = parseInt(document.getElementById('loan_years').value);
    const fixedPeriod = parseInt(document.getElementById('fixed_period').value);
    const floatingRate = parseFloat(document.getElementById('floating_rate').value) / 100;

    // Validation
    if (!loanAmount || isNaN(annualRate) || !loanYears || isNaN(fixedPeriod) || isNaN(floatingRate)) {
        return;
    }

    if (fixedPeriod > loanYears) {
        alert('Fixed period cannot exceed loan term');
        return;
    }

    // Calculate yearly payments
    const yearlyPayments = calculateYearlyPayments(loanAmount, annualRate, loanYears, fixedPeriod, floatingRate);

    // Update summary section
    document.getElementById('display_loan_amount').textContent = formatCurrency(loanAmount);
    document.getElementById('display_loan_years').textContent = `${loanYears} years`;
    document.getElementById('display_fixed_rate').textContent = `${(annualRate * 100).toFixed(2)}%`;
    document.getElementById('display_floating_rate').textContent = `${(floatingRate * 100).toFixed(2)}%`;
    document.getElementById('display_fixed_period').textContent = `${fixedPeriod} years`;

    // Update key metrics
    const fixedEndData = yearlyPayments[fixedPeriod - 1];
    const remainingBalance = fixedEndData ? fixedEndData.remainingBalance : 0;
    const yearsLeft = loanYears - fixedPeriod;
    const principalPaid = loanAmount - remainingBalance;

    document.getElementById('remaining_balance').textContent = formatCurrency(remainingBalance);
    document.getElementById('years_left').textContent = `${yearsLeft} year${yearsLeft !== 1 ? 's' : ''}`;
    document.getElementById('principal_paid').textContent = formatCurrency(principalPaid);
    document.getElementById('fixed_period_text').textContent = fixedPeriod;

    // Update full payment schedule table
    const tableBody = document.getElementById('payment_table_body');
    tableBody.innerHTML = '';

    yearlyPayments.forEach(payment => {
        const row = document.createElement('tr');
        if (payment.year === fixedPeriod) {
            row.classList.add('highlight-row');
        }

        row.innerHTML = `
            <td>${payment.year}</td>
            <td class="currency">${formatCurrency(payment.principal)}</td>
            <td class="currency">${formatCurrency(payment.interest)}</td>
            <td class="currency">${formatCurrency(payment.total)}</td>
            <td class="currency">${formatCurrency(payment.remainingBalance)}</td>
        `;
        tableBody.appendChild(row);
    });

}

// Debounce function to avoid excessive updates while typing
let debounceTimer;
function debounceUpdate() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(updateResults, 300);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Check if values were passed from the experience form
    const storedData = sessionStorage.getItem('loanFormData');

    if (storedData) {
        // Use values from experience form
        const formData = JSON.parse(storedData);
        document.getElementById('loan_amount').value = formData.loan_amount;
        document.getElementById('annual_rate').value = formData.annual_rate;
        document.getElementById('loan_years').value = formData.loan_years;
        document.getElementById('fixed_period').value = formData.fixed_period;
        document.getElementById('floating_rate').value = formData.floating_rate;

        // Clear the stored data
        sessionStorage.removeItem('loanFormData');
    } else {
        // Set default values
        document.getElementById('loan_amount').value = '100000';
        document.getElementById('annual_rate').value = '5';
        document.getElementById('loan_years').value = '30';
        document.getElementById('fixed_period').value = '5';
        document.getElementById('floating_rate').value = '6';
    }

    // Add event listeners to all inputs
    const inputs = document.querySelectorAll('input[type="number"]');
    inputs.forEach(input => {
        input.addEventListener('input', debounceUpdate);
    });

    // Calculate initial results
    updateResults();
});
