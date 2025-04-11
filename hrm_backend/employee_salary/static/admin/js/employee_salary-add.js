(function() {
    const $ = django.jQuery;

    $(document).ready(function () {
        console.log("Employee Salary Add JS Loaded!");

        $("#id_employee").on("change", toggleFields);
        setTimeout(toggleFields, 500);
    });

    function toggleFields() {
        const employeeId = $("#id_employee").val();

        if (!employeeId) return;

        $.ajax({
            url: `/admin/employee_salary/employeesalary/get_employment_type/`,
            data: {
                employee_id: employeeId
            },
            success: function (response) {
                console.log("Employment Type:", response.employment_type);

                const isRegular = response.employment_type === "Regular";

                if (isRegular) {
                    $("#id_contract_start_date").closest(".form-row").hide();
                    $("#id_contract_end_date").closest(".form-row").hide();
                    $("#id_daily_rate").closest(".form-row").hide();
                } else {
                    $("#id_base_salary").closest(".form-row").hide();
                }
            },
            error: function () {
                console.error("Failed to fetch employment type.");
            }
        });
    }
})();
