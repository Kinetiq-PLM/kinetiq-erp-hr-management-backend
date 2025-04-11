(function($) {
    $(document).ready(function() {
        function toggleFields() {
            var employeeId = $("#id_employee").val();
            if (!employeeId) return;

            $.ajax({
                url: "/admin/get_employment_type/",
                data: { employee_id: employeeId },
                success: function(response) {
                    if (response.employment_type === "Regular") {
                        $("#id_contract_start_date").closest(".form-row").hide();
                        $("#id_contract_end_date").closest(".form-row").hide();
                        $("#id_daily_rate").closest(".form-row").hide();
                        $("#id_base_salary").closest(".form-row").show();
                    } else {
                        $("#id_contract_start_date").closest(".form-row").show();
                        $("#id_contract_end_date").closest(".form-row").show();
                        $("#id_daily_rate").closest(".form-row").show();
                        $("#id_base_salary").closest(".form-row").hide();
                    }
                }
            });
        }

        $("#id_employee").change(toggleFields);

        toggleFields();
    });
})(django.jQuery);
