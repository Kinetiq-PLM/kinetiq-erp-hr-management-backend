(function () {
    const $ = django.jQuery;

    function toggleFields() {
        const employeeId = $("#id_employee").val()?.trim();

        if (!employeeId) {
            $("#id_base_salary").closest(".form-row").hide();
            $("#id_contract_start_date").closest(".form-row").hide();
            $("#id_contract_end_date").closest(".form-row").hide();
            $("#id_daily_rate").closest(".form-row").hide();
            return;
        }

        $.ajax({
            url: "/admin/employee_salary/employeesalary/get_employment_type/",
            data: { employee_id: employeeId },
            success: function (response) {
                console.log("Employment Type:", response.employment_type);

                const isRegular = response.employment_type === "Regular";

                $("#id_base_salary").closest(".form-row").toggle(isRegular);
                $("#id_contract_start_date").closest(".form-row").toggle(!isRegular);
                $("#id_contract_end_date").closest(".form-row").toggle(!isRegular);
                $("#id_daily_rate").closest(".form-row").toggle(!isRegular);
            },
            error: function () {
                console.error("Failed to fetch employment type.");
            }
        });
    }

    $(document).ready(function () {
        console.log("Employee Salary Add JS Loaded!");

        $("#id_employee").on("change", toggleFields);

    });
})();
