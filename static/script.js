document.addEventListener("DOMContentLoaded", function() {
    const slider = document.getElementById("expense-deposit-toggle");
    const sliderLabel = document.getElementById("slider-label");

    slider.addEventListener("change", function() {
        if (this.checked) {
            sliderLabel.textContent = "Deposit";
        } else {
            sliderLabel.textContent = "Expense";
        }
    });
});
