document.addEventListener("DOMContentLoaded", function () {
    const empField = document.querySelector("#id_employee");
    const contractStartField = document.querySelector("#id_contract_start_date").closest(".form-row");
    const contractEndField = document.querySelector("#id_contract_end_date").closest(".form-row");
    const dailyRateField = document.querySelector("#id_daily_rate").closest(".form-row");

    function updateFields() {
        const selectedOption = empField.options[empField.selectedIndex].text;
        if (selectedOption.includes("(Regular)")) {
            contractStartField.style.display = "none";
            contractEndField.style.display = "none";
            dailyRateField.style.display = "none";
        } else {
            contractStartField.style.display = "";
            contractEndField.style.display = "";
            dailyRateField.style.display = "";
        }
    }

    empField.addEventListener("change", updateFields);
    updateFields();  // Run on page load
});
