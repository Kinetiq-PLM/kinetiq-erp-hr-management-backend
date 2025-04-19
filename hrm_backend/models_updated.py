# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AdminNotifications(models.Model):
    notifications_id = models.CharField(primary_key=True, max_length=255)
    module = models.CharField()
    to_user_id = models.CharField()
    message = models.CharField()
    notifications_status = models.CharField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'admin.notifications'


class AttendanceTracking(models.Model):
    attendance_id = models.CharField(primary_key=True, max_length=255)
    employee = models.ForeignKey('Employees', models.DO_NOTHING, blank=True, null=True)
    date = models.ForeignKey('CalendarDates', models.DO_NOTHING, db_column='date', blank=True, null=True)
    time_in = models.DateTimeField(blank=True, null=True)
    time_out = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    late_hours = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    undertime_hours = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    is_holiday = models.BooleanField(blank=True, null=True)
    holiday_type = models.CharField(max_length=20, blank=True, null=True)
    work_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    calendar_date = models.ForeignKey('CalendarDates', models.DO_NOTHING, related_name='attendancetracking_calendar_date_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'attendance_tracking'


class AuditLog(models.Model):
    log_id = models.CharField(primary_key=True, max_length=255)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    action = models.TextField()
    timestamp = models.DateTimeField()
    ip_address = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'audit_log'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class CalendarDates(models.Model):
    date = models.DateField(primary_key=True)
    is_workday = models.BooleanField()
    is_holiday = models.BooleanField()
    is_special = models.BooleanField()
    holiday_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'calendar_dates'


class Candidates(models.Model):
    candidate_id = models.CharField(primary_key=True, max_length=255)
    job = models.ForeignKey('JobPosting', models.DO_NOTHING, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(unique=True, max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    resume_path = models.TextField(blank=True, null=True)
    application_status = models.CharField(max_length=50, blank=True, null=True)
    documents = models.JSONField(blank=True, null=True)
    interview_details = models.JSONField(blank=True, null=True)
    offer_details = models.JSONField(blank=True, null=True)
    contract_details = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    is_archived = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'candidates'


class DepartmentSuperiors(models.Model):
    dept_superior_id = models.CharField(primary_key=True, max_length=255)
    dept = models.ForeignKey('Departments', models.DO_NOTHING, blank=True, null=True)
    position = models.ForeignKey('Positions', models.DO_NOTHING, blank=True, null=True)
    hierarchy_level = models.IntegerField(blank=True, null=True)
    is_archived = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'department_superiors'


class Departments(models.Model):
    dept_id = models.CharField(primary_key=True, max_length=255)
    dept_name = models.CharField(unique=True, max_length=100, blank=True, null=True)
    is_archived = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'departments'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoCeleryBeatClockedschedule(models.Model):
    clocked_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_celery_beat_clockedschedule'


class DjangoCeleryBeatCrontabschedule(models.Model):
    minute = models.CharField(max_length=240)
    hour = models.CharField(max_length=96)
    day_of_week = models.CharField(max_length=64)
    day_of_month = models.CharField(max_length=124)
    month_of_year = models.CharField(max_length=64)
    timezone = models.CharField(max_length=63)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_crontabschedule'


class DjangoCeleryBeatIntervalschedule(models.Model):
    every = models.IntegerField()
    period = models.CharField(max_length=24)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_intervalschedule'


class DjangoCeleryBeatPeriodictask(models.Model):
    name = models.CharField(unique=True, max_length=200)
    task = models.CharField(max_length=200)
    args = models.TextField()
    kwargs = models.TextField()
    queue = models.CharField(max_length=200, blank=True, null=True)
    exchange = models.CharField(max_length=200, blank=True, null=True)
    routing_key = models.CharField(max_length=200, blank=True, null=True)
    expires = models.DateTimeField(blank=True, null=True)
    enabled = models.BooleanField()
    last_run_at = models.DateTimeField(blank=True, null=True)
    total_run_count = models.IntegerField()
    date_changed = models.DateTimeField()
    description = models.TextField()
    crontab = models.ForeignKey(DjangoCeleryBeatCrontabschedule, models.DO_NOTHING, blank=True, null=True)
    interval = models.ForeignKey(DjangoCeleryBeatIntervalschedule, models.DO_NOTHING, blank=True, null=True)
    solar = models.ForeignKey('DjangoCeleryBeatSolarschedule', models.DO_NOTHING, blank=True, null=True)
    one_off = models.BooleanField()
    start_time = models.DateTimeField(blank=True, null=True)
    priority = models.IntegerField(blank=True, null=True)
    headers = models.TextField()
    clocked = models.ForeignKey(DjangoCeleryBeatClockedschedule, models.DO_NOTHING, blank=True, null=True)
    expire_seconds = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_periodictask'


class DjangoCeleryBeatPeriodictasks(models.Model):
    ident = models.SmallIntegerField(primary_key=True)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_celery_beat_periodictasks'


class DjangoCeleryBeatSolarschedule(models.Model):
    event = models.CharField(max_length=24)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        managed = False
        db_table = 'django_celery_beat_solarschedule'
        unique_together = (('event', 'latitude', 'longitude'),)


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class EmployeeLeaveBalances(models.Model):
    balance_id = models.CharField(primary_key=True, max_length=255)
    employee = models.ForeignKey('Employees', models.DO_NOTHING, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    sick_leave_remaining = models.IntegerField(blank=True, null=True)
    vacation_leave_remaining = models.IntegerField(blank=True, null=True)
    maternity_leave_remaining = models.IntegerField(blank=True, null=True)
    paternity_leave_remaining = models.IntegerField(blank=True, null=True)
    solo_parent_leave_remaining = models.IntegerField(blank=True, null=True)
    unpaid_leave_taken = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee_leave_balances'
        unique_together = (('employee', 'year'),)


class EmployeePerformance(models.Model):
    performance_id = models.CharField(primary_key=True, max_length=255)
    employee = models.ForeignKey('Employees', models.DO_NOTHING, blank=True, null=True)
    immediate_superior = models.ForeignKey('Employees', models.DO_NOTHING, related_name='employeeperformance_immediate_superior_set', blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    bonus_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    bonus_payment_month = models.IntegerField(blank=True, null=True)
    review_date = models.DateField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee_performance'


class EmployeeSalary(models.Model):
    salary_id = models.CharField(primary_key=True, max_length=255)
    employee = models.ForeignKey('Employees', models.DO_NOTHING, blank=True, null=True)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    daily_rate = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    effective_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee_salary'


class Employees(models.Model):
    employee_id = models.CharField(primary_key=True, max_length=255)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    dept = models.ForeignKey(Departments, models.DO_NOTHING, blank=True, null=True)
    position = models.ForeignKey('Positions', models.DO_NOTHING, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    employment_type = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    reports_to = models.ForeignKey('self', models.DO_NOTHING, db_column='reports_to', blank=True, null=True)
    is_supervisor = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    is_archived = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employees'


class Equipment(models.Model):
    equipment_id = models.CharField(primary_key=True, max_length=255)
    equipment_name = models.CharField(max_length=255)
    description = models.TextField()
    availability_status = models.CharField(max_length=50)
    last_maintenance_date = models.DateField()
    equipment_cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'equipment'


class ExternalProjectTaskList(models.Model):
    task_id = models.CharField(primary_key=True, max_length=255)
    task_deadline = models.DateField()

    class Meta:
        managed = False
        db_table = 'external_project_task_list'


class FeatureGoodsTrackingDepartmentdata(models.Model):
    dept_id = models.CharField(primary_key=True, max_length=255)
    dept_name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'feature_goods_tracking_departmentdata'


class FeatureGoodsTrackingProductdocuitemdata(models.Model):
    productdocu_id = models.CharField(primary_key=True, max_length=255)
    manuf_date = models.DateField()
    expiry_date = models.DateField()
    product_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'feature_goods_tracking_productdocuitemdata'


class FeatureInternalTransferExternalmoduleproductorderdata(models.Model):
    external_id = models.CharField(primary_key=True, max_length=255)
    rework_quantity = models.IntegerField()
    reason_rework = models.CharField(max_length=255)
    production_order_detail_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'feature_internal_transfer_externalmoduleproductorderdata'


class GeneralLedgerAccounts(models.Model):
    gl_account_id = models.CharField(primary_key=True, max_length=255)
    account_name = models.CharField(max_length=255)
    account_code = models.CharField(max_length=255)
    account_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'general_ledger_accounts'


class JobPosting(models.Model):
    job_id = models.CharField(primary_key=True, max_length=255)
    dept = models.ForeignKey(Departments, models.DO_NOTHING, blank=True, null=True)
    position = models.ForeignKey('Positions', models.DO_NOTHING, blank=True, null=True)
    position_title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    employment_type = models.CharField(max_length=20, blank=True, null=True)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    duration_days = models.SmallIntegerField(blank=True, null=True)
    finance_approval_id = models.CharField(max_length=255, blank=True, null=True)
    finance_approval_status = models.CharField(max_length=20, blank=True, null=True)
    posting_status = models.CharField(max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    is_archived = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'job_posting'


class JournalEntries(models.Model):
    description = models.CharField(max_length=255)
    currency_id = models.CharField(max_length=255)
    invoice_id = models.CharField(max_length=255, blank=True, null=True)
    journal_date = models.DateField()
    journal_id = models.CharField(primary_key=True, max_length=255)
    total_credit = models.DecimalField(max_digits=15, decimal_places=2)
    total_debit = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'journal_entries'


class JournalEntryLines(models.Model):
    entry_line_id = models.CharField(primary_key=True, max_length=255)
    gl_account_id = models.CharField(max_length=255, blank=True, null=True)
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2)
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    journal = models.ForeignKey(JournalEntries, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'journal_entry_lines'


class Labor(models.Model):
    labor_id = models.CharField(primary_key=True, max_length=255)
    production_order_id = models.CharField(max_length=255)
    employee_id = models.CharField(max_length=255)
    date_worked = models.DateTimeField()
    days_worked = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'labor'


class LeaveRequests(models.Model):
    leave_id = models.CharField(primary_key=True, max_length=255)
    employee = models.ForeignKey(Employees, models.DO_NOTHING, blank=True, null=True)
    dept = models.ForeignKey(Departments, models.DO_NOTHING, blank=True, null=True)
    immediate_superior = models.ForeignKey(Employees, models.DO_NOTHING, related_name='leaverequests_immediate_superior_set', blank=True, null=True)
    management_approval_id = models.CharField(max_length=255, blank=True, null=True)
    leave_type = models.CharField(max_length=20, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    total_days = models.IntegerField(blank=True, null=True)
    is_paid = models.BooleanField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    is_archived = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'leave_requests'


class Payroll(models.Model):
    payroll_id = models.CharField(primary_key=True, max_length=255)
    employee = models.ForeignKey(Employees, models.DO_NOTHING, blank=True, null=True)
    pay_period_start = models.DateField(blank=True, null=True)
    pay_period_end = models.DateField(blank=True, null=True)
    employment_type = models.CharField(max_length=20)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    overtime_pay = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    holiday_pay = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    bonus_pay = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    thirteenth_month_pay = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    gross_pay = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    sss_contribution = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    philhealth_contribution = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    pagibig_contribution = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    tax = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    late_deduction = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    absent_deduction = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    undertime_deduction = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payroll'


class PoliciesPolicydocument(models.Model):
    document = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField()
    policy_id = models.CharField(primary_key=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'policies_policydocument'


class Positions(models.Model):
    position_id = models.CharField(primary_key=True, max_length=255)
    position_title = models.CharField(max_length=100, blank=True, null=True)
    salary_grade = models.CharField(max_length=20, blank=True, null=True)
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    employment_type = models.CharField(max_length=20, blank=True, null=True)
    typical_duration_days = models.SmallIntegerField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    is_archived = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'positions'


class ProductionOrdersDetails(models.Model):
    production_order_id = models.CharField(primary_key=True, max_length=255)
    actual_quantity = models.IntegerField()
    cost_of_production = models.DecimalField(max_digits=10, decimal_places=2)
    miscellaneous_costs = models.DecimalField(max_digits=10, decimal_places=2)
    rework_required = models.BooleanField()
    rework_notes = models.TextField()

    class Meta:
        managed = False
        db_table = 'production_orders_details'


class ProductionOrdersHeader(models.Model):
    production_order_id = models.CharField(primary_key=True, max_length=255)
    task_id = models.CharField(max_length=255)
    bom_id = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=50)
    target_quantity = models.IntegerField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'production_orders_header'


class ProjectEquipment(models.Model):
    project_equipment_id = models.CharField(primary_key=True, max_length=255)
    equipment_id = models.CharField(max_length=255)
    product_id = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'project_equipment'


class PurchaseOrderShipment(models.Model):
    shipment_id = models.CharField(primary_key=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'purchase_order_shipment'


class ResignationResignation(models.Model):
    resignation_id = models.CharField(primary_key=True, max_length=255)
    employee_id = models.CharField(max_length=255)
    submission_date = models.DateTimeField()
    notice_period_days = models.IntegerField()
    hr_approver_id = models.CharField(max_length=255, blank=True, null=True)
    approval_status = models.CharField(max_length=20)
    clearance_status = models.CharField(max_length=20)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'resignation_resignation'


class Resignations(models.Model):
    resignation_id = models.CharField(primary_key=True, max_length=255)
    employee = models.ForeignKey(Employees, models.DO_NOTHING)
    submission_date = models.DateTimeField(blank=True, null=True)
    notice_period_days = models.IntegerField(blank=True, null=True)
    hr_approver = models.ForeignKey(Employees, models.DO_NOTHING, related_name='resignations_hr_approver_set', blank=True, null=True)
    approval_status = models.CharField(max_length=20, blank=True, null=True)
    clearance_status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'resignations'


class ReworkCost(models.Model):
    production_order_id = models.CharField(primary_key=True, max_length=255)
    additional_cost = models.DecimalField(max_digits=10, decimal_places=2)
    additional_misc = models.DecimalField(max_digits=10, decimal_places=2)
    total_rework_cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'rework_cost'


class RolesPermission(models.Model):
    role_id = models.CharField(primary_key=True, max_length=255)
    role_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    permissions = models.TextField(blank=True, null=True)
    access_level = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'roles_permission'


class Users(models.Model):
    user_id = models.CharField(primary_key=True, max_length=255)
    employee_id = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    status = models.CharField(max_length=10)
    type = models.CharField(max_length=10)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    role = models.ForeignKey(RolesPermission, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class VReworkGlAccountId(models.Model):
    gl_account_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'v_rework_gl_account_id'


class WorkforceAllocation(models.Model):
    allocation_id = models.CharField(primary_key=True, max_length=255)
    request_id = models.CharField(unique=True, max_length=255, blank=True, null=True)
    requesting_dept = models.ForeignKey(Departments, models.DO_NOTHING, blank=True, null=True)
    required_skills = models.TextField(blank=True, null=True)
    task_description = models.TextField(blank=True, null=True)
    employee = models.ForeignKey(Employees, models.DO_NOTHING, blank=True, null=True)
    current_dept = models.ForeignKey(Departments, models.DO_NOTHING, related_name='workforceallocation_current_dept_set', blank=True, null=True)
    hr_approver = models.ForeignKey(Employees, models.DO_NOTHING, related_name='workforceallocation_hr_approver_set', blank=True, null=True)
    approval_status = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    is_archived = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'workforce_allocation'
