--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: accounting; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA accounting;


ALTER SCHEMA accounting OWNER TO postgres;

--
-- Name: admin; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA admin;


ALTER SCHEMA admin OWNER TO postgres;

--
-- Name: distribution; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA distribution;


ALTER SCHEMA distribution OWNER TO postgres;

--
-- Name: finance; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA finance;


ALTER SCHEMA finance OWNER TO postgres;

--
-- Name: human_resources; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA human_resources;


ALTER SCHEMA human_resources OWNER TO postgres;

--
-- Name: inventory; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA inventory;


ALTER SCHEMA inventory OWNER TO postgres;

--
-- Name: management; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA management;


ALTER SCHEMA management OWNER TO postgres;

--
-- Name: mrp; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA mrp;


ALTER SCHEMA mrp OWNER TO postgres;

--
-- Name: operations; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA operations;


ALTER SCHEMA operations OWNER TO postgres;

--
-- Name: production; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA production;


ALTER SCHEMA production OWNER TO postgres;

--
-- Name: project_management; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA project_management;


ALTER SCHEMA project_management OWNER TO postgres;

--
-- Name: purchasing; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA purchasing;


ALTER SCHEMA purchasing OWNER TO postgres;

--
-- Name: sales; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA sales;


ALTER SCHEMA sales OWNER TO postgres;

--
-- Name: services; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA services;


ALTER SCHEMA services OWNER TO postgres;

--
-- Name: solution_customizing; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA solution_customizing;


ALTER SCHEMA solution_customizing OWNER TO postgres;

--
-- Name: calculate_performance_bonus(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.calculate_performance_bonus() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.performance_id := 'HR-PERF-' || to_char(CURRENT_DATE, 'YYYY') || '-' || substr(md5(random()::text), 1, 6);

    SELECT 
        CASE 
            WHEN es.base_salary IS NOT NULL THEN 
                (es.base_salary * 12 * 
                    CASE 
                        WHEN NEW.rating = 5 THEN 0.10  
                        WHEN NEW.rating = 4 THEN 0.075   
                        WHEN NEW.rating = 3 THEN 0.05   
                        WHEN NEW.rating = 2 THEN 0.025   
                        ELSE 0.00
                    END)
            WHEN es.daily_rate IS NOT NULL THEN
                (es.daily_rate * 260 * 
                    CASE 
                        WHEN NEW.rating = 5 THEN 0.10  
                        WHEN NEW.rating = 4 THEN 0.075   
                        WHEN NEW.rating = 3 THEN 0.05   
                        WHEN NEW.rating = 2 THEN 0.025   
                        ELSE 0.00
                    END)
            ELSE 0
        END 
    INTO NEW.bonus_amount
    FROM human_resources.employee_salary es
    WHERE es.employee_id = NEW.employee_id
    ORDER BY es.effective_date DESC
    LIMIT 1;

    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.calculate_performance_bonus() OWNER TO postgres;

--
-- Name: calculate_tax(numeric); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.calculate_tax(gross_pay numeric) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
BEGIN
 RETURN CASE
        WHEN gross_pay <= 20833 THEN 0
        WHEN gross_pay <= 33333 THEN (gross_pay - 20833) * 0.20
        WHEN gross_pay <= 66667 THEN 2500 + (gross_pay - 33333) * 0.25
        WHEN gross_pay <= 166667 THEN 10833 + (gross_pay - 66667) * 0.30
        WHEN gross_pay <= 666667 THEN 40833.33 + (gross_pay - 166667) * 0.32
        ELSE 200833.33 + (gross_pay - 666667) * 0.35
    END;
END;
$$;


ALTER FUNCTION human_resources.calculate_tax(gross_pay numeric) OWNER TO postgres;

--
-- Name: calculate_work_hours(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.calculate_work_hours() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
 NEW.work_hours := 
        CASE WHEN NEW.time_out IS NULL THEN NULL
        ELSE EXTRACT(EPOCH FROM (NEW.time_out - NEW.time_in))/3600 END;
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.calculate_work_hours() OWNER TO postgres;

--
-- Name: check_assignment_overlap(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.check_assignment_overlap() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM human_resources.workforce_allocation
        WHERE employee_id = NEW.employee_id
        AND status = 'Active'
        AND (
            (start_date BETWEEN NEW.start_date AND NEW.end_date) OR
            (end_date BETWEEN NEW.start_date AND NEW.end_date) OR
            (NEW.start_date BETWEEN start_date AND end_date)
        )
    ) THEN
        RAISE EXCEPTION 'Employee already has an active assignment during this period';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.check_assignment_overlap() OWNER TO postgres;

--
-- Name: deduct_leave_balances(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.deduct_leave_balances() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Only deduct when status changes to fully approved
    IF NEW.status = 'Approved by Management' AND OLD.status != 'Approved by Management' THEN
        UPDATE human_resources.employee_leave_balances
        SET
            sick_leave_remaining = CASE 
                WHEN NEW.leave_type = 'Sick' THEN sick_leave_remaining - NEW.total_days 
                ELSE sick_leave_remaining END,
            vacation_leave_remaining = CASE 
                WHEN NEW.leave_type = 'Vacation' THEN vacation_leave_remaining - NEW.total_days 
                ELSE vacation_leave_remaining END,
			maternity_leave_remaining = CASE 
                WHEN NEW.leave_type = 'Maternity' THEN maternity_leave_remaining - NEW.total_days 
                ELSE maternity_leave_remaining END,
            paternity_leave_remaining = CASE 
                WHEN NEW.leave_type = 'Paternity' THEN paternity_leave_remaining - NEW.total_days 
                ELSE paternity_leave_remaining END,
            solo_parent_leave_remaining = CASE 
                WHEN NEW.leave_type = 'Solo Parent' THEN solo_parent_leave_remaining - NEW.total_days 
                ELSE solo_parent_leave_remaining END,
            unpaid_leave_taken = CASE 
                WHEN NEW.leave_type = 'Unpaid' THEN unpaid_leave_taken + NEW.total_days 
                ELSE unpaid_leave_taken END,
            updated_at = CURRENT_TIMESTAMP
        WHERE employee_id = NEW.employee_id
        AND year = EXTRACT(YEAR FROM NEW.start_date);
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.deduct_leave_balances() OWNER TO postgres;

--
-- Name: detect_attendance_status(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.detect_attendance_status() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Don't override statuses that were manually set by app
    IF NEW.status IS DISTINCT FROM 'Clocked Out' THEN
        IF NEW.time_in IS NULL THEN
            NEW.status := 'Absent';
        ELSIF NEW.time_in > '[expected_start_time]' THEN 
            NEW.status := 'Late';
        ELSE
            NEW.status := 'Present';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.detect_attendance_status() OWNER TO postgres;

--
-- Name: generate_allocation_id(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.generate_allocation_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
 NEW.allocation_id := 'ALLOC-' || to_char(CURRENT_DATE, 'YYYYMM') || '-' || 
                        lpad(floor(random() * 10000)::text, 4, '0');
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.generate_allocation_id() OWNER TO postgres;

--
-- Name: generate_attendance_id(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.generate_attendance_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
 unique_code TEXT;
    module_prefix TEXT := 'ATT'; 
    module_name TEXT := 'HR';          
BEGIN
    unique_code := substr(md5(random()::text), 1, 6);
    NEW.attendance_id := module_name || '-' || module_prefix || '-' || 
                        to_char(CURRENT_DATE, 'YYYYMMDD') || '-' || unique_code;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.generate_attendance_id() OWNER TO postgres;

--
-- Name: generate_bi_monthly_payroll(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.generate_bi_monthly_payroll() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_daily_rate DECIMAL(12,2);
    v_hourly_rate DECIMAL(12,2);
    v_attendance RECORD;
    v_holidays INT;
    v_work_days INT;
    v_actual_work_days INT;
    v_performance_bonus DECIMAL(12,2);
BEGIN
    SELECT 
        CASE WHEN es.base_salary IS NOT NULL THEN es.base_salary/2
             ELSE es.daily_rate * 15 END,
        CASE WHEN es.base_salary IS NOT NULL THEN es.base_salary/(22*8)
             ELSE es.daily_rate/8 END
    INTO v_daily_rate, v_hourly_rate
    FROM human_resources.employee_salary es
    WHERE es.employee_id = NEW.employee_id
    ORDER BY es.effective_date DESC LIMIT 1;
    
    SELECT 
        COUNT(*) FILTER (WHERE is_holiday = TRUE AND is_special = FALSE),
        COUNT(*) FILTER (WHERE is_workday = TRUE)
    INTO v_holidays, v_work_days
    FROM human_resources.calendar_dates
    WHERE date BETWEEN NEW.pay_period_start AND NEW.pay_period_end;
    
    SELECT 
        COUNT(*) FILTER (WHERE status = 'Absent') AS absent_days,
        COUNT(*) FILTER (WHERE status = 'Late') AS late_days,
        SUM(late_hours) AS total_late_hours,
        SUM(undertime_hours) AS total_undertime_hours,
        COUNT(*) FILTER (WHERE is_holiday = TRUE AND time_in IS NOT NULL) AS worked_holidays
    INTO v_attendance
    FROM human_resources.attendance_tracking
    WHERE employee_id = NEW.employee_id 
    AND date BETWEEN NEW.pay_period_start AND NEW.pay_period_end;
    
    SELECT bonus_amount INTO v_performance_bonus
    FROM human_resources.employee_performance
    WHERE employee_id = NEW.employee_id
    AND EXTRACT(YEAR FROM review_date) = EXTRACT(YEAR FROM NEW.pay_period_end)
    ORDER BY review_date DESC LIMIT 1;
    
    NEW.base_salary := v_daily_rate * (v_work_days - v_attendance.absent_days);
    NEW.overtime_pay := NEW.overtime_hours * v_hourly_rate * 1.5;
    NEW.holiday_pay := (v_holidays * v_daily_rate) + (v_attendance.worked_holidays * v_daily_rate * 1.3);
    NEW.bonus_pay := COALESCE(v_performance_bonus, 0);
    
    IF NEW.employment_type = 'Regular' AND EXTRACT(MONTH FROM NEW.pay_period_end) = 12 THEN
        NEW.thirteenth_month_pay := v_daily_rate * 15; -- Half month pay
    END IF;
    
    NEW.sss_contribution := NEW.base_salary * 0.05;
    NEW.philhealth_contribution := NEW.base_salary * 0.045;
    NEW.pagibig_contribution := NEW.base_salary * 0.02;
    NEW.late_deduction := v_attendance.total_late_hours * v_hourly_rate;
    NEW.absent_deduction := v_attendance.absent_days * v_daily_rate;
    NEW.undertime_deduction := v_attendance.total_undertime_hours * v_hourly_rate;
    
    NEW.tax := human_resources.calculate_tax(NEW.gross_pay);
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.generate_bi_monthly_payroll() OWNER TO postgres;

--
-- Name: generate_department_id(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.generate_department_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    unique_code TEXT;
    module_prefix TEXT := 'DEPT'; 
    module_name TEXT := 'HR';          
BEGIN
    unique_code := substr(md5(random()::text), 1, 6);
    NEW.dept_id := module_name || '-' || module_prefix || '-' || to_char(CURRENT_DATE, 'YYYY') || '-' || unique_code;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.generate_department_id() OWNER TO postgres;

--
-- Name: generate_dept_superior_id(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.generate_dept_superior_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.dept_superior_id IS NULL THEN
        NEW.dept_superior_id := 'DEPT-SUP-2025-' || 
                                  substring(translate(gen_random_uuid()::TEXT, '-', ''), 1, 6);
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.generate_dept_superior_id() OWNER TO postgres;

--
-- Name: generate_employee_id(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.generate_employee_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
 unique_code TEXT;
    module_prefix TEXT := 'EMP'; 
    module_name TEXT := 'HR';          
BEGIN
    unique_code := substr(md5(random()::text), 1, 6);
    NEW.employee_id := module_name || '-' || module_prefix || '-' || to_char(CURRENT_DATE, 'YYYY') || '-' || unique_code;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.generate_employee_id() OWNER TO postgres;

--
-- Name: generate_final_payroll(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.generate_final_payroll() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_base_salary DECIMAL(12,2);
    v_final_payroll_id VARCHAR(255);
    v_employment_type VARCHAR(50);
BEGIN
    -- Generate payroll ID
    v_final_payroll_id := 'FPAY-' || NEW.employee_id || '-' || to_char(NEW.last_working_date, 'YYYYMMDD');

    -- Get current salary data
    SELECT 
        es.base_salary,
        es.employment_type
    INTO 
        v_base_salary,
        v_employment_type
    FROM human_resources.employee_salary es
    WHERE es.employee_id = NEW.employee_id
    ORDER BY es.effective_date DESC
    LIMIT 1;

    -- Insert final payroll record
    INSERT INTO human_resources.payroll (
        payroll_id,
        employee_id,
        pay_period_start,
        pay_period_end,
        employment_type,
        base_salary,
        bonus_pay,
        status,
        is_final_settlement
    ) VALUES (
        v_final_payroll_id,
        NEW.employee_id,
        DATE_TRUNC('month', NEW.last_working_date),
        NEW.last_working_date,
        v_employment_type,
        v_base_salary,
        0,
        'Pending',
        TRUE
    );

    RETURN NULL;  -- After trigger, no need to modify NEW
END;
$$;


ALTER FUNCTION human_resources.generate_final_payroll() OWNER TO postgres;

--
-- Name: generate_job_id(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.generate_job_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.job_id := 'JOB-' || to_char(CURRENT_DATE, 'YYYYMM') || '-' || 
                 lpad(floor(random() * 10000)::text, 4, '0');
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.generate_job_id() OWNER TO postgres;

--
-- Name: generate_leave_balance_id(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.generate_leave_balance_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.balance_id IS NULL THEN
        NEW.balance_id := 'LEAVE-BAL-' || NEW.employee_id || '-' || NEW.year;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.generate_leave_balance_id() OWNER TO postgres;

--
-- Name: generate_position_id(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.generate_position_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.position_id IS NULL THEN
        NEW.position_id := 
            CASE NEW.employment_type
                WHEN 'Regular' THEN 'REG-' || to_char(CURRENT_DATE, 'YYMM') || '-' || substr(md5(random()::text), 1, 4)
                WHEN 'Contractual' THEN 'CTR-' || to_char(CURRENT_DATE, 'YYMM') || '-' || substr(md5(random()::text), 1, 4)
                WHEN 'Seasonal' THEN 'SEA-' || to_char(CURRENT_DATE, 'YYMM') || '-' || substr(md5(random()::text), 1, 4)
            END;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.generate_position_id() OWNER TO postgres;

--
-- Name: generate_request_id(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.generate_request_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.request_id := 'REQ-2025-' || lpad(floor(random() * 1000000)::text, 6, '0');
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.generate_request_id() OWNER TO postgres;

--
-- Name: handle_leave_approval(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.handle_leave_approval() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    
    IF NEW.management_approval_id IS NOT NULL AND 
       (OLD.management_approval_id IS NULL OR OLD.management_approval_id != NEW.management_approval_id) THEN
        
        IF NOT EXISTS (
            SELECT 1 FROM management.approvals 
            WHERE approval_id = NEW.management_approval_id
        ) THEN
            RAISE EXCEPTION 'Invalid management approval reference: %', NEW.management_approval_id;
        END IF;
        
        SELECT 
            CASE WHEN status = 'Approved' THEN 'Approved by Management'
                 ELSE 'Rejected by Management' END
        INTO NEW.status
        FROM management.approvals
        WHERE approval_id = NEW.management_approval_id;
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.handle_leave_approval() OWNER TO postgres;

--
-- Name: process_leave_request(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.process_leave_request() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.leave_id := 'LV-' || to_char(CURRENT_DATE, 'YYYYMM') || '-' || substr(md5(random()::text), 1, 6);
    
    IF NOT EXISTS (
        SELECT 1 FROM human_resources.employees 
        WHERE employee_id = NEW.employee_id AND employment_type = 'Regular'
    ) THEN
        RAISE EXCEPTION 'Only regular employees can request leave';
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.process_leave_request() OWNER TO postgres;

--
-- Name: process_resignation(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.process_resignation() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Generate resignation ID
    NEW.resignation_id := 'RES-' || to_char(CURRENT_DATE, 'YYYYMM') || '-' || substr(md5(random()::text), 1, 6);
    
    -- Set default notice period based on employment type
    SELECT 
        CASE employment_type
            WHEN 'Regular' THEN 30
            WHEN 'Contractual' THEN 15
            WHEN 'Seasonal' THEN 7
        END
    INTO NEW.notice_period_days
    FROM human_resources.employees
    WHERE employee_id = NEW.employee_id;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.process_resignation() OWNER TO postgres;

--
-- Name: set_compensation_values(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.set_compensation_values() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.position_id IS NOT NULL THEN
        IF NEW.employment_type = 'Regular' THEN
            SELECT min_salary INTO NEW.base_salary 
            FROM human_resources.positions 
            WHERE position_id = NEW.position_id;
        ELSIF NEW.employment_type IN ('Contractual', 'Seasonal') THEN
            SELECT min_salary/22 INTO NEW.daily_rate -- Convert monthly to daily rate
            FROM human_resources.positions
            WHERE position_id = NEW.position_id;
            
            IF NEW.duration_days IS NULL THEN
                SELECT typical_duration_days INTO NEW.duration_days
                FROM human_resources.positions
                WHERE position_id = NEW.position_id;
            END IF;
        END IF;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.set_compensation_values() OWNER TO postgres;

--
-- Name: set_position_defaults(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.set_position_defaults() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN

    IF NEW.employment_type = 'Contractual' AND NEW.typical_duration_days IS NULL THEN
        NEW.typical_duration_days := 90; -- Default 3 months
    ELSIF NEW.employment_type = 'Seasonal' AND NEW.typical_duration_days IS NULL THEN
        NEW.typical_duration_days := 14; -- Default 2 weeks
    END IF;
    
    IF NEW.is_active IS NULL THEN
        NEW.is_active := TRUE;
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.set_position_defaults() OWNER TO postgres;

--
-- Name: set_supervisor_flag(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.set_supervisor_flag() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.is_supervisor := EXISTS (
        SELECT 1 FROM human_resources.department_superiors ds
        WHERE ds.dept_id = NEW.dept_id AND ds.position_id = NEW.position_id
    );
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.set_supervisor_flag() OWNER TO postgres;

--
-- Name: track_allocation_status(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.track_allocation_status() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.status = 'Submitted' AND OLD.status != 'Submitted' THEN
        NEW.submitted_at = CURRENT_TIMESTAMP;
    ELSIF NEW.approval_status = 'Approved' AND OLD.approval_status != 'Approved' THEN
        NEW.approved_at = CURRENT_TIMESTAMP;
    END IF;
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.track_allocation_status() OWNER TO postgres;

--
-- Name: update_employee_timestamp(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.update_employee_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.update_employee_timestamp() OWNER TO postgres;

--
-- Name: update_job_timestamps(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.update_job_timestamps() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    
    IF NEW.finance_approval_id IS NOT NULL AND 
       (OLD.finance_approval_id IS DISTINCT FROM NEW.finance_approval_id) THEN
        IF NOT EXISTS (
            SELECT 1 FROM finance.budget_submission 
            WHERE submission_id = NEW.finance_approval_id
        ) THEN
            RAISE EXCEPTION 'Invalid finance approval reference: %', NEW.finance_approval_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.update_job_timestamps() OWNER TO postgres;

--
-- Name: update_payroll_status(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.update_payroll_status() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;

    IF NEW.status = 'Processing' AND OLD.status != 'Processing' THEN
        NEW.status := 'Completed';
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.update_payroll_status() OWNER TO postgres;

--
-- Name: update_position_timestamp(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.update_position_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.update_position_timestamp() OWNER TO postgres;

--
-- Name: validate_finance_approval(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.validate_finance_approval() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.posting_status = 'Open' AND 
       (NEW.finance_approval_status != 'Approved' OR NEW.finance_approval_id IS NULL) THEN
        RAISE EXCEPTION 'Cannot open job posting without finance approval';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.validate_finance_approval() OWNER TO postgres;

--
-- Name: validate_leave_request(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.validate_leave_request() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    current_balance RECORD;
    fiscal_year INT := EXTRACT(YEAR FROM CURRENT_DATE);
BEGIN
    SELECT * INTO current_balance
    FROM human_resources.employee_leave_balances
    WHERE employee_id = NEW.employee_id AND year = fiscal_year;
    
    IF NOT FOUND THEN
        INSERT INTO human_resources.employee_leave_balances (employee_id)
        VALUES (NEW.employee_id)
        RETURNING * INTO current_balance;
    END IF;
    
    CASE NEW.leave_type
        WHEN 'Sick' THEN
            IF NEW.total_days > current_balance.sick_leave_remaining THEN
                RAISE EXCEPTION 'Insufficient sick leave balance. Remaining: % days', current_balance.sick_leave_remaining;
            END IF;
        WHEN 'Vacation' THEN
            IF NEW.total_days > current_balance.vacation_leave_remaining THEN
                RAISE EXCEPTION 'Insufficient vacation leave balance. Remaining: % days', current_balance.vacation_leave_remaining;
            END IF;
        WHEN 'Maternity' THEN
            IF NEW.total_days > 105 THEN
                RAISE EXCEPTION 'Maternity leave cannot exceed 105 days';
            END IF;
            IF NEW.total_days > current_balance.maternity_leave_remaining THEN
                RAISE EXCEPTION 'Insufficient maternity leave balance. Remaining: % days', current_balance.maternity_leave_remaining;
            END IF;
        WHEN 'Paternity' THEN
            IF NEW.total_days > 7 THEN
                RAISE EXCEPTION 'Paternity leave cannot exceed 7 days';
            END IF;
            IF NEW.total_days > current_balance.paternity_leave_remaining THEN
                RAISE EXCEPTION 'Insufficient paternity leave balance. Remaining: % days', current_balance.paternity_leave_remaining;
            END IF;
        WHEN 'Solo Parent' THEN
            IF NEW.total_days > 7 THEN
                RAISE EXCEPTION 'Solo parent leave cannot exceed 7 days per year';
            END IF;
            IF NEW.total_days > current_balance.solo_parent_leave_remaining THEN
                RAISE EXCEPTION 'Insufficient solo parent leave balance. Remaining: % days', current_balance.solo_parent_leave_remaining;
            END IF;
        ELSE
            NULL;
    END CASE;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.validate_leave_request() OWNER TO postgres;

--
-- Name: validate_salary(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.validate_salary() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
 emp_type TEXT;
BEGIN
    SELECT employment_type INTO emp_type 
    FROM human_resources.employees 
    WHERE employee_id = NEW.employee_id;
    
    NEW.salary_id := 'SAL-' || to_char(CURRENT_DATE, 'YYYYMM') || '-' || substr(md5(random()::text), 1, 6);
    
    IF emp_type = 'Regular' THEN
        IF NEW.base_salary IS NULL OR NEW.base_salary <= 0 THEN
            RAISE EXCEPTION 'Regular employees must have a positive base salary';
        END IF;

IF emp_type = 'Regular' AND (
    NEW.base_salary < (SELECT min_salary FROM human_resources.positions p 
                      JOIN human_resources.employees e ON p.position_id = e.position_id 
                      WHERE e.employee_id = NEW.employee_id)
    OR 
    NEW.base_salary > (SELECT max_salary FROM human_resources.positions p 
                      JOIN human_resources.employees e ON p.position_id = e.position_id 
                      WHERE e.employee_id = NEW.employee_id)
) THEN 
    RAISE EXCEPTION 'Base salary must be within position’s min/max range';
END IF;

        IF NEW.daily_rate IS NOT NULL OR NEW.contract_start_date IS NOT NULL OR NEW.contract_end_date IS NOT NULL THEN
            RAISE EXCEPTION 'Regular employees should not have daily rates or contract dates';
        END IF;
    ELSIF emp_type IN ('Contractual', 'Seasonal') THEN
        IF NEW.daily_rate IS NULL OR NEW.daily_rate <= 0 THEN
            RAISE EXCEPTION 'Contractual/Seasonal employees must have a positive daily rate';
        END IF;
        IF NEW.contract_start_date IS NULL OR NEW.contract_end_date IS NULL OR NEW.contract_end_date <= NEW.contract_start_date THEN
            RAISE EXCEPTION 'Contractual/Seasonal employees require valid contract dates';
        END IF;
        IF NEW.base_salary IS NOT NULL THEN
            RAISE EXCEPTION 'Contractual/Seasonal employees should not have a base salary';
        END IF;
    END IF;
    
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.validate_salary() OWNER TO postgres;

--
-- Name: validate_superior(); Type: FUNCTION; Schema: human_resources; Owner: postgres
--

CREATE FUNCTION human_resources.validate_superior() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.reports_to IS NOT NULL THEN
        -- Check if the superior exists and is in the same department
        IF NOT EXISTS (
            SELECT 1 FROM human_resources.employees sup
            WHERE sup.employee_id = NEW.reports_to
            AND sup.dept_id = NEW.dept_id
            AND sup.is_supervisor = TRUE  -- Ensure they're marked as supervisor
        ) THEN
            RAISE EXCEPTION 'Invalid superior: Must be a supervisor in the same department';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION human_resources.validate_superior() OWNER TO postgres;

--
-- Name: calculate_payroll_values(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.calculate_payroll_values() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_hourly_rate DECIMAL(12,2);
    v_daily_rate DECIMAL(12,2);
    v_attendance RECORD;
    v_work_days INT;
    v_actual_days INT;
BEGIN
    -- Get basic salary information
    IF NEW.employment_type = 'Regular' THEN
        v_hourly_rate := NEW.base_salary / (22 * 8); -- 22 working days/month, 8 hours/day
        v_daily_rate := NEW.base_salary / 11; -- Semi-monthly pay period has ~11 work days
    ELSE
        -- For contractual/seasonal, get daily rate from employee_salary
        SELECT daily_rate INTO v_daily_rate
        FROM human_resources.employee_salary
        WHERE employee_id = NEW.employee_id
        ORDER BY effective_date DESC LIMIT 1;
        
        v_hourly_rate := v_daily_rate / 8;
        NEW.base_salary := v_daily_rate * (
            SELECT COUNT(DISTINCT date) 
            FROM human_resources.attendance_tracking 
            WHERE employee_id = NEW.employee_id 
            AND date BETWEEN NEW.pay_period_start AND NEW.pay_period_end
            AND status != 'Absent'
        );
    END IF;

    -- Calculate overtime pay
    NEW.overtime_pay := NEW.overtime_hours * v_hourly_rate * 1.5;

    -- Get attendance data for deductions
    SELECT 
        COUNT(DISTINCT date) FILTER (WHERE status = 'Absent') AS absent_days,
        SUM(late_hours) AS total_late_hours,
        SUM(undertime_hours) AS total_undertime_hours,
        COUNT(DISTINCT date) FILTER (WHERE is_holiday = TRUE AND status = 'Present') AS worked_holidays
    INTO v_attendance
    FROM human_resources.attendance_tracking
    WHERE employee_id = NEW.employee_id
    AND date BETWEEN NEW.pay_period_start AND NEW.pay_period_end;

    -- Calculate work days in period
    SELECT COUNT(*) INTO v_work_days
    FROM human_resources.calendar_dates
    WHERE date BETWEEN NEW.pay_period_start AND NEW.pay_period_end
    AND is_workday = TRUE AND is_holiday = FALSE;

    -- Calculate deductions
    NEW.late_deduction := COALESCE(v_attendance.total_late_hours, 0) * v_hourly_rate;
    NEW.absent_deduction := COALESCE(v_attendance.absent_days, 0) * v_daily_rate;
    NEW.undertime_deduction := COALESCE(v_attendance.total_undertime_hours, 0) * v_hourly_rate;
    
    -- Calculate holiday pay if applicable
    NEW.holiday_pay := COALESCE(v_attendance.worked_holidays, 0) * v_daily_rate * 1.3;

    -- Government contributions (Philippines example)
    NEW.sss_contribution := LEAST(NEW.base_salary * 0.05, 1350.00);
    NEW.philhealth_contribution := NEW.base_salary * 0.045;
    NEW.pagibig_contribution := LEAST(NEW.base_salary * 0.02, 100.00);

    -- Tax calculation
    NEW.tax := human_resources.calculate_tax(
        NEW.base_salary + NEW.overtime_pay + NEW.holiday_pay
    );

    -- Finalize status
    NEW.status := 'Completed';
    NEW.updated_at := CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.calculate_payroll_values() OWNER TO postgres;

--
-- Name: calculate_performance_bonus(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.calculate_performance_bonus() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Your bonus calculation logic here
    -- Example only:
    IF NEW.rating = 5 THEN
        NEW.bonus_amount := NEW.bonus_amount + 1000;
    END IF;

    -- REMOVE THIS ↓
    -- NEW.updated_at := CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.calculate_performance_bonus() OWNER TO postgres;

--
-- Name: check_assignment_overlap(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.check_assignment_overlap() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM human_resources.workforce_allocation
        WHERE employee_id = NEW.employee_id
        AND status = 'Active'
        AND (
            (start_date BETWEEN NEW.start_date AND NEW.end_date) OR
            (end_date BETWEEN NEW.start_date AND NEW.end_date) OR
            (NEW.start_date BETWEEN start_date AND end_date)
        )
    )THEN
        RAISE EXCEPTION 'Employee already has an active assignment during this period';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_assignment_overlap() OWNER TO postgres;

--
-- Name: update_leave_balances(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_leave_balances() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.status = 'Approved by Management' AND OLD.status != 'Approved by Management' THEN
        UPDATE human_resources.employee_leave_balances
        SET 
            sick_leave_remaining = CASE 
                WHEN NEW.leave_type = 'Sick' THEN GREATEST(0, sick_leave_remaining - NEW.total_days)
                ELSE sick_leave_remaining END,
            vacation_leave_remaining = CASE 
                WHEN NEW.leave_type = 'Vacation' THEN GREATEST(0, vacation_leave_remaining - NEW.total_days)
                ELSE vacation_leave_remaining END,
            unpaid_leave_taken = CASE
                WHEN NEW.is_paid = FALSE THEN unpaid_leave_taken + NEW.total_days
                ELSE unpaid_leave_taken END
        WHERE employee_id = NEW.employee_id AND year = EXTRACT(YEAR FROM NEW.start_date);
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_leave_balances() OWNER TO postgres;

--
-- Name: update_timestamp(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_timestamp() OWNER TO postgres;

--
-- Name: validate_salary(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.validate_salary() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Ensure the "updated_at" field exists in the table
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.validate_salary() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: attendance_tracking; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.attendance_tracking (
    attendance_id character varying(255) NOT NULL,
    employee_id character varying(255),
    date date,
    time_in timestamp without time zone,
    time_out timestamp without time zone,
    status character varying(20),
    late_hours numeric(4,2) DEFAULT 0,
    undertime_hours numeric(4,2) DEFAULT 0,
    is_holiday boolean DEFAULT false,
    holiday_type character varying(20),
    work_hours numeric(5,2) GENERATED ALWAYS AS (
CASE
    WHEN (time_out IS NULL) THEN (0)::numeric
    ELSE ((EXTRACT(epoch FROM (time_out - time_in)) / (3600)::numeric) - late_hours)
END) STORED,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    is_archived boolean DEFAULT false,
    CONSTRAINT chk_holiday_type CHECK (((holiday_type)::text = ANY ((ARRAY[NULL::character varying, 'Regular'::character varying, 'Special'::character varying])::text[]))),
    CONSTRAINT chk_status CHECK (((status)::text = ANY ((ARRAY['Present'::character varying, 'Absent'::character varying, 'Late'::character varying, 'Half-Day'::character varying])::text[])))
);


ALTER TABLE human_resources.attendance_tracking OWNER TO postgres;

--
-- Name: auth_group; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE human_resources.auth_group OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: human_resources; Owner: postgres
--

ALTER TABLE human_resources.auth_group ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME human_resources.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_group_permissions; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE human_resources.auth_group_permissions OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: human_resources; Owner: postgres
--

ALTER TABLE human_resources.auth_group_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME human_resources.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_permission; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE human_resources.auth_permission OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: human_resources; Owner: postgres
--

ALTER TABLE human_resources.auth_permission ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME human_resources.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_user; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE human_resources.auth_user OWNER TO postgres;

--
-- Name: auth_user_groups; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.auth_user_groups (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE human_resources.auth_user_groups OWNER TO postgres;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: human_resources; Owner: postgres
--

ALTER TABLE human_resources.auth_user_groups ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME human_resources.auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: human_resources; Owner: postgres
--

ALTER TABLE human_resources.auth_user ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME human_resources.auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.auth_user_user_permissions (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE human_resources.auth_user_user_permissions OWNER TO postgres;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: human_resources; Owner: postgres
--

ALTER TABLE human_resources.auth_user_user_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME human_resources.auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: calendar_dates; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.calendar_dates (
    date date NOT NULL,
    is_workday boolean NOT NULL,
    is_holiday boolean DEFAULT false NOT NULL,
    is_special boolean DEFAULT false NOT NULL,
    holiday_name character varying(100),
    holiday_type character varying(50)
);


ALTER TABLE human_resources.calendar_dates OWNER TO postgres;

--
-- Name: candidates; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.candidates (
    candidate_id character varying(255) NOT NULL,
    job_id character varying(255),
    first_name character varying(50),
    last_name character varying(50),
    email character varying(100),
    phone character varying(20),
    resume_path text,
    application_status character varying(50) DEFAULT 'Applied'::character varying,
    documents jsonb,
    interview_details jsonb,
    offer_details jsonb,
    contract_details jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_application_status CHECK (((application_status)::text = ANY ((ARRAY['Applied'::character varying, 'Document Screening'::character varying, 'Interview Scheduled'::character varying, 'Interview Completed'::character varying, 'Offer Extended'::character varying, 'Contract Signed'::character varying, 'Hired'::character varying, 'Rejected'::character varying])::text[])))
);


ALTER TABLE human_resources.candidates OWNER TO postgres;

--
-- Name: department_superiors; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.department_superiors (
    dept_id character varying(255) NOT NULL,
    position_id character varying(255) NOT NULL,
    hierarchy_level integer,
    is_archived boolean DEFAULT false,
    dept_superior_id character varying(255) NOT NULL,
    change_reason character varying(255),
    CONSTRAINT chk_hierarchy_level CHECK ((hierarchy_level > 0))
);


ALTER TABLE human_resources.department_superiors OWNER TO postgres;

--
-- Name: department_superiors_historicaldepartment_superior; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.department_superiors_historicaldepartment_superior (
    dept_superior_id character varying NOT NULL,
    hierarchy_level integer NOT NULL,
    is_archived boolean NOT NULL,
    change_reason character varying(255),
    history_id integer NOT NULL,
    history_date timestamp with time zone NOT NULL,
    history_change_reason character varying(100),
    history_type character varying(1) NOT NULL,
    dept_id character varying(20),
    history_user_id integer,
    position_id character varying(255),
    CONSTRAINT department_superiors_historicaldepartment_hierarchy_level_check CHECK ((hierarchy_level >= 0))
);


ALTER TABLE human_resources.department_superiors_historicaldepartment_superior OWNER TO postgres;

--
-- Name: department_superiors_historicaldepartment_superi_history_id_seq; Type: SEQUENCE; Schema: human_resources; Owner: postgres
--

ALTER TABLE human_resources.department_superiors_historicaldepartment_superior ALTER COLUMN history_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME human_resources.department_superiors_historicaldepartment_superi_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: departments; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.departments (
    dept_id character varying(255) NOT NULL,
    dept_name character varying(100),
    is_archived boolean DEFAULT false,
    created_by_id integer,
    updated_by_id integer,
    change_reason character varying(255)
);


ALTER TABLE human_resources.departments OWNER TO postgres;

--
-- Name: employees; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.employees (
    employee_id character varying(255) NOT NULL,
    user_id character varying(255),
    dept_id character varying(255),
    position_id character varying(255),
    first_name character varying(50),
    last_name character varying(50),
    phone character varying(20),
    employment_type character varying(20),
    status character varying(20) DEFAULT 'Active'::character varying,
    reports_to character varying(255),
    is_supervisor boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    is_archived boolean DEFAULT false,
    change_reason character varying(255),
    CONSTRAINT chk_employment_type CHECK (((employment_type)::text = ANY ((ARRAY['Regular'::character varying, 'Contractual'::character varying, 'Seasonal'::character varying])::text[]))),
    CONSTRAINT chk_status CHECK (((status)::text = ANY ((ARRAY['Active'::character varying, 'Inactive'::character varying, 'Resigned'::character varying, 'On Notice'::character varying])::text[])))
);


ALTER TABLE human_resources.employees OWNER TO postgres;

--
-- Name: positions; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.positions (
    position_id character varying(255) NOT NULL,
    position_title character varying(100),
    salary_grade character varying(20),
    min_salary numeric(10,2),
    max_salary numeric(10,2),
    employment_type character varying(20),
    typical_duration_days smallint,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    employee_id character varying(50),
    is_archived boolean DEFAULT false,
    change_reason character varying(255),
    CONSTRAINT chk_duration_days CHECK (((((employment_type)::text = 'Contractual'::text) AND ((typical_duration_days >= 30) AND (typical_duration_days <= 180))) OR (((employment_type)::text = 'Seasonal'::text) AND ((typical_duration_days >= 1) AND (typical_duration_days <= 29))) OR (((employment_type)::text = 'Regular'::text) AND (typical_duration_days IS NULL)))),
    CONSTRAINT chk_employment_types CHECK (((employment_type)::text = ANY ((ARRAY['Regular'::character varying, 'Contractual'::character varying, 'Seasonal'::character varying])::text[]))),
    CONSTRAINT chk_salary_ranges CHECK (((((employment_type)::text = 'Regular'::text) AND (min_salary >= (0)::numeric) AND (max_salary >= min_salary)) OR (((employment_type)::text = ANY ((ARRAY['Contractual'::character varying, 'Seasonal'::character varying])::text[])) AND ((min_salary >= (500)::numeric) AND (min_salary <= (10000)::numeric)) AND (max_salary >= min_salary))))
);


ALTER TABLE human_resources.positions OWNER TO postgres;

--
-- Name: department_superiors_view; Type: VIEW; Schema: human_resources; Owner: postgres
--

CREATE VIEW human_resources.department_superiors_view AS
 SELECT ds.dept_id,
    d.dept_name,
    ds.position_id,
    p.position_title,
    ds.hierarchy_level,
    e.employee_id,
    concat(e.first_name, ' ', e.last_name) AS superior_name,
    e.phone,
    e.status AS employee_status
   FROM (((human_resources.department_superiors ds
     JOIN human_resources.departments d ON (((ds.dept_id)::text = (d.dept_id)::text)))
     JOIN human_resources.positions p ON (((ds.position_id)::text = (p.position_id)::text)))
     LEFT JOIN human_resources.employees e ON ((((ds.position_id)::text = (e.position_id)::text) AND ((ds.dept_id)::text = (e.dept_id)::text))))
  ORDER BY ds.dept_id, ds.hierarchy_level;


ALTER VIEW human_resources.department_superiors_view OWNER TO postgres;

--
-- Name: departments_department; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.departments_department (
    dept_id character varying(20) NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE human_resources.departments_department OWNER TO postgres;

--
-- Name: departments_historicaldepartment; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.departments_historicaldepartment (
    dept_id character varying(20) NOT NULL,
    dept_name character varying(100) NOT NULL,
    is_archived boolean NOT NULL,
    history_id integer NOT NULL,
    history_date timestamp with time zone NOT NULL,
    history_change_reason character varying(100),
    history_type character varying(1) NOT NULL,
    history_user_id integer,
    change_reason character varying(255)
);


ALTER TABLE human_resources.departments_historicaldepartment OWNER TO postgres;

--
-- Name: departments_historicaldepartment_history_id_seq; Type: SEQUENCE; Schema: human_resources; Owner: postgres
--

ALTER TABLE human_resources.departments_historicaldepartment ALTER COLUMN history_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME human_resources.departments_historicaldepartment_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dept_superior_seq; Type: SEQUENCE; Schema: human_resources; Owner: postgres
--

CREATE SEQUENCE human_resources.dept_superior_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE human_resources.dept_superior_seq OWNER TO postgres;

--
-- Name: django_admin_log; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE human_resources.django_admin_log OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: human_resources; Owner: postgres
--

ALTER TABLE human_resources.django_admin_log ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME human_resources.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_content_type; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE human_resources.django_content_type OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: human_resources; Owner: postgres
--

ALTER TABLE human_resources.django_content_type ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME human_resources.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_migrations; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE human_resources.django_migrations OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: human_resources; Owner: postgres
--

ALTER TABLE human_resources.django_migrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME human_resources.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_session; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE human_resources.django_session OWNER TO postgres;

--
-- Name: employee_leave_balances; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.employee_leave_balances (
    balance_id character varying(255) NOT NULL,
    employee_id character varying(255),
    year integer DEFAULT EXTRACT(year FROM CURRENT_DATE),
    sick_leave_remaining integer DEFAULT 15,
    vacation_leave_remaining integer DEFAULT 15,
    maternity_leave_remaining integer DEFAULT 105,
    paternity_leave_remaining integer DEFAULT 7,
    solo_parent_leave_remaining integer DEFAULT 7,
    unpaid_leave_taken integer DEFAULT 0,
    CONSTRAINT chk_positive_balances CHECK (((sick_leave_remaining >= 0) AND (vacation_leave_remaining >= 0) AND (maternity_leave_remaining >= 0) AND (paternity_leave_remaining >= 0) AND (solo_parent_leave_remaining >= 0) AND (unpaid_leave_taken >= 0)))
);


ALTER TABLE human_resources.employee_leave_balances OWNER TO postgres;

--
-- Name: employee_performance; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.employee_performance (
    performance_id character varying(255) NOT NULL,
    employee_id character varying(255),
    immediate_superior_id character varying(255),
    rating integer,
    bonus_amount numeric(12,2),
    bonus_payment_month integer,
    review_date date,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    is_archived boolean DEFAULT false,
    CONSTRAINT chk_bonus_payment_month CHECK (((bonus_payment_month >= 1) AND (bonus_payment_month <= 12))),
    CONSTRAINT chk_rating CHECK (((rating >= 1) AND (rating <= 5)))
);


ALTER TABLE human_resources.employee_performance OWNER TO postgres;

--
-- Name: employee_salary; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.employee_salary (
    salary_id character varying(255) NOT NULL,
    employee_id character varying(255),
    base_salary numeric(12,2),
    daily_rate numeric(12,2),
    effective_date date,
    updated_at timestamp without time zone,
    contract_end_date date,
    contract_start_date date
);


ALTER TABLE human_resources.employee_salary OWNER TO postgres;

--
-- Name: employees_historicalemployee; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.employees_historicalemployee (
    employee_id character varying(255) NOT NULL,
    user_id character varying(255),
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    phone character varying(20) NOT NULL,
    employment_type character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    reports_to character varying(255),
    is_supervisor boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    is_archived boolean NOT NULL,
    change_reason character varying(255),
    history_id integer NOT NULL,
    history_date timestamp with time zone NOT NULL,
    history_change_reason character varying(100),
    history_type character varying(1) NOT NULL,
    dept_id character varying(20),
    history_user_id integer,
    position_id character varying(255)
);


ALTER TABLE human_resources.employees_historicalemployee OWNER TO postgres;

--
-- Name: employees_historicalemployee_history_id_seq; Type: SEQUENCE; Schema: human_resources; Owner: postgres
--

ALTER TABLE human_resources.employees_historicalemployee ALTER COLUMN history_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME human_resources.employees_historicalemployee_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: human_resources.department_superiors; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources."human_resources.department_superiors" (
    id bigint NOT NULL,
    dept_id character varying(255) NOT NULL,
    superior_job_title character varying(100) NOT NULL,
    hierarchy_level integer NOT NULL,
    CONSTRAINT "human_resources.department_superiors_hierarchy_level_check" CHECK ((hierarchy_level >= 0))
);


ALTER TABLE human_resources."human_resources.department_superiors" OWNER TO postgres;

--
-- Name: human_resources.department_superiors_id_seq; Type: SEQUENCE; Schema: human_resources; Owner: postgres
--

ALTER TABLE human_resources."human_resources.department_superiors" ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME human_resources."human_resources.department_superiors_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: human_resources.employees; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources."human_resources.employees" (
    employee_id character varying(255) NOT NULL,
    dept_id character varying(255) NOT NULL,
    position_id character varying(255) NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    phone character varying(20) NOT NULL,
    employment_type character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    reports_to character varying(255),
    is_supervisor boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE human_resources."human_resources.employees" OWNER TO postgres;

--
-- Name: human_resources.positions; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources."human_resources.positions" (
    position_id character varying(255) NOT NULL,
    position_title character varying(100) NOT NULL,
    salary_grade character varying(20) NOT NULL,
    min_salary numeric(10,2) NOT NULL,
    max_salary numeric(10,2) NOT NULL,
    employment_type character varying(20) NOT NULL,
    typical_duration_days smallint NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE human_resources."human_resources.positions" OWNER TO postgres;

--
-- Name: job_posting; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.job_posting (
    job_id character varying(255) NOT NULL,
    dept_id character varying(255),
    position_id character varying(255),
    position_title character varying(100),
    description text,
    requirements text,
    employment_type character varying(20),
    base_salary numeric(10,2),
    daily_rate numeric(10,2),
    duration_days smallint,
    finance_approval_id character varying(255),
    finance_approval_status character varying(20) DEFAULT 'Pending'::character varying,
    posting_status character varying(20) DEFAULT 'Draft'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_compensation_fields CHECK (((((employment_type)::text = 'Regular'::text) AND (base_salary IS NOT NULL) AND (daily_rate IS NULL)) OR (((employment_type)::text = ANY ((ARRAY['Contractual'::character varying, 'Seasonal'::character varying])::text[])) AND (daily_rate IS NOT NULL) AND (base_salary IS NULL)))),
    CONSTRAINT chk_duration_days CHECK (((((employment_type)::text = 'Contractual'::text) AND ((duration_days >= 30) AND (duration_days <= 180))) OR (((employment_type)::text = 'Seasonal'::text) AND ((duration_days >= 1) AND (duration_days <= 29))) OR (((employment_type)::text = 'Regular'::text) AND (duration_days IS NULL)))),
    CONSTRAINT chk_employment_type CHECK (((employment_type)::text = ANY ((ARRAY['Regular'::character varying, 'Contractual'::character varying, 'Seasonal'::character varying])::text[]))),
    CONSTRAINT chk_finance_approval_status CHECK (((finance_approval_status)::text = ANY ((ARRAY['Pending'::character varying, 'Approved'::character varying, 'Rejected'::character varying])::text[]))),
    CONSTRAINT chk_posting_status CHECK (((posting_status)::text = ANY ((ARRAY['Draft'::character varying, 'Pending Finance Approval'::character varying, 'Open'::character varying, 'Closed'::character varying, 'Filled'::character varying])::text[])))
);


ALTER TABLE human_resources.job_posting OWNER TO postgres;

--
-- Name: leave_requests; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.leave_requests (
    leave_id character varying(255) NOT NULL,
    employee_id character varying(255),
    dept_id character varying(255),
    immediate_superior_id character varying(255),
    management_approval_id character varying(255),
    leave_type character varying(20),
    start_date date,
    end_date date,
    total_days integer,
    is_paid boolean,
    status character varying(50) DEFAULT 'Pending'::character varying,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_leave_types CHECK (((leave_type)::text = ANY ((ARRAY['Sick'::character varying, 'Vacation'::character varying, 'Personal'::character varying, 'Maternity'::character varying, 'Paternity'::character varying, 'Solo Parent'::character varying, 'Unpaid'::character varying])::text[]))),
    CONSTRAINT chk_status_values CHECK (((status)::text = ANY ((ARRAY['Pending'::character varying, 'Approved by Superior'::character varying, 'Rejected by Superior'::character varying, 'Approved by Management'::character varying, 'Rejected by Management'::character varying, 'Recorded in HRIS'::character varying])::text[]))),
    CONSTRAINT chk_valid_dates CHECK ((end_date >= start_date))
);


ALTER TABLE human_resources.leave_requests OWNER TO postgres;

--
-- Name: payroll; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.payroll (
    payroll_id character varying(255) NOT NULL,
    employee_id character varying(255),
    pay_period_start date,
    pay_period_end date,
    employment_type character varying(20) NOT NULL,
    base_salary numeric(12,2),
    overtime_hours numeric(5,2) DEFAULT 0,
    overtime_pay numeric(12,2) DEFAULT 0,
    holiday_pay numeric(12,2) DEFAULT 0,
    bonus_pay numeric(12,2) DEFAULT 0,
    thirteenth_month_pay numeric(12,2) DEFAULT 0,
    gross_pay numeric(12,2) GENERATED ALWAYS AS (((((base_salary + overtime_pay) + holiday_pay) + bonus_pay) + thirteenth_month_pay)) STORED,
    sss_contribution numeric(12,2) DEFAULT 0,
    philhealth_contribution numeric(12,2) DEFAULT 0,
    pagibig_contribution numeric(12,2) DEFAULT 0,
    tax numeric(12,2) DEFAULT 0,
    late_deduction numeric(12,2) DEFAULT 0,
    absent_deduction numeric(12,2) DEFAULT 0,
    undertime_deduction numeric(12,2) DEFAULT 0,
    total_deductions numeric(12,2) GENERATED ALWAYS AS (((((((sss_contribution + philhealth_contribution) + pagibig_contribution) + tax) + late_deduction) + absent_deduction) + undertime_deduction)) STORED,
    net_pay numeric(12,2) GENERATED ALWAYS AS ((((((base_salary + overtime_pay) + holiday_pay) + bonus_pay) + thirteenth_month_pay) - ((((((sss_contribution + philhealth_contribution) + pagibig_contribution) + tax) + late_deduction) + absent_deduction) + undertime_deduction))) STORED,
    status character varying(20) DEFAULT 'Draft'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_pay_period CHECK ((pay_period_end > pay_period_start)),
    CONSTRAINT chk_regular_employee_benefits CHECK ((((employment_type)::text = 'Regular'::text) OR (thirteenth_month_pay = (0)::numeric))),
    CONSTRAINT chk_status CHECK (((status)::text = ANY ((ARRAY['Draft'::character varying, 'Processing'::character varying, 'Completed'::character varying, 'Cancelled'::character varying])::text[])))
);


ALTER TABLE human_resources.payroll OWNER TO postgres;

--
-- Name: positions_historicalposition; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.positions_historicalposition (
    position_id character varying(255) NOT NULL,
    position_title character varying(100) NOT NULL,
    salary_grade character varying(20),
    min_salary numeric(10,2) NOT NULL,
    max_salary numeric(10,2) NOT NULL,
    employment_type character varying(20) NOT NULL,
    typical_duration_days smallint,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    is_archived boolean NOT NULL,
    change_reason character varying(255),
    history_id integer NOT NULL,
    history_date timestamp with time zone NOT NULL,
    history_change_reason character varying(100),
    history_type character varying(1) NOT NULL,
    history_user_id integer,
    CONSTRAINT positions_historicalposition_typical_duration_days_check CHECK ((typical_duration_days >= 0))
);


ALTER TABLE human_resources.positions_historicalposition OWNER TO postgres;

--
-- Name: positions_historicalposition_history_id_seq; Type: SEQUENCE; Schema: human_resources; Owner: postgres
--

ALTER TABLE human_resources.positions_historicalposition ALTER COLUMN history_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME human_resources.positions_historicalposition_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: resignations; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.resignations (
    resignation_id character varying(255) NOT NULL,
    employee_id character varying(255) NOT NULL,
    submission_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    notice_period_days integer,
    hr_approver_id character varying(255),
    approval_status character varying(20) DEFAULT 'Pending'::character varying,
    clearance_status character varying(20) DEFAULT 'Pending'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE human_resources.resignations OWNER TO postgres;

--
-- Name: workforce_allocation; Type: TABLE; Schema: human_resources; Owner: postgres
--

CREATE TABLE human_resources.workforce_allocation (
    allocation_id character varying(255) NOT NULL,
    request_id character varying(255),
    requesting_dept_id character varying(255),
    required_skills text,
    task_description text,
    employee_id character varying(255),
    current_dept_id character varying(255),
    hr_approver_id character varying(255),
    approval_status character varying(20) DEFAULT 'Pending'::character varying,
    status character varying(20) DEFAULT 'Draft'::character varying,
    start_date date,
    end_date date,
    rejection_reason text,
    submitted_at timestamp without time zone,
    approved_at timestamp without time zone,
    is_archived boolean DEFAULT false,
    CONSTRAINT chk_approval_status CHECK (((approval_status)::text = ANY ((ARRAY['Pending'::character varying, 'Approved'::character varying, 'Rejected'::character varying, 'Under Review'::character varying])::text[]))),
    CONSTRAINT chk_status CHECK (((status)::text = ANY ((ARRAY['Draft'::character varying, 'Submitted'::character varying, 'Active'::character varying, 'Completed'::character varying, 'Canceled'::character varying])::text[]))),
    CONSTRAINT employee_assignment_logic CHECK (((((approval_status)::text = 'Approved'::text) AND (employee_id IS NOT NULL)) OR ((approval_status)::text <> 'Approved'::text))),
    CONSTRAINT valid_allocation_period CHECK ((end_date >= start_date))
);


ALTER TABLE human_resources.workforce_allocation OWNER TO postgres;

--
-- Name: attendance_tracking; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attendance_tracking (
    attendance_id character varying(255) NOT NULL,
    employee_id character varying(255) NOT NULL,
    time_in timestamp with time zone,
    time_out timestamp with time zone,
    work_hours numeric(5,2),
    status character varying(20) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.attendance_tracking OWNER TO postgres;

--
-- Name: employee_performance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employee_performance (
    performance_id character varying(255) NOT NULL,
    rating integer NOT NULL,
    bonus_percentage numeric(5,2) NOT NULL,
    bonus_amount numeric(10,2),
    review_date date NOT NULL,
    comments text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    employee_id character varying(255) NOT NULL,
    immediate_superior_id character varying(255)
);


ALTER TABLE public.employee_performance OWNER TO postgres;

--
-- Name: employee_salary; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employee_salary (
    salary_id character varying(255) NOT NULL,
    employee_id character varying(255) NOT NULL,
    base_salary numeric(10,2) NOT NULL,
    daily_rate numeric(10,2) NOT NULL,
    contract_start_date date,
    contract_end_date date,
    effective_date date NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.employee_salary OWNER TO postgres;

--
-- Name: workforce_allocation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workforce_allocation (
    allocation_id character varying(255) NOT NULL,
    request_id character varying(255) NOT NULL,
    requesting_dept_id character varying(255) NOT NULL,
    required_skills text NOT NULL,
    task_description text NOT NULL,
    employee_id character varying(255),
    current_dept_id character varying(255) NOT NULL,
    hr_approver_id character varying(255),
    approval_status character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    start_date date,
    end_date date,
    rejection_reason text,
    created_at timestamp with time zone NOT NULL,
    submitted_at timestamp with time zone,
    approved_at timestamp with time zone,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.workforce_allocation OWNER TO postgres;

--
-- Data for Name: attendance_tracking; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.attendance_tracking (attendance_id, employee_id, date, time_in, time_out, status, late_hours, undertime_hours, is_holiday, holiday_type, created_at, updated_at, is_archived) FROM stdin;
ATT-20231106-bb6f41	HR-EMP-2025-bb6f41	2023-11-06	2023-11-06 08:58:00	2023-11-06 17:02:00	Present	0.00	0.00	f	\N	2025-04-08 09:40:34.119108	2025-04-08 09:40:34.119108	f
ATT-20231107-bb6f41	HR-EMP-2025-bb6f41	2023-11-07	2023-11-07 09:15:00	2023-11-07 17:00:00	Late	0.25	0.00	f	\N	2025-04-08 09:40:34.119108	2025-04-08 09:40:34.119108	f
ATT-20231109-bb6f41	HR-EMP-2025-bb6f41	2023-11-09	2023-11-09 08:50:00	2023-11-09 17:05:00	Present	0.00	0.00	f	\N	2025-04-08 09:40:34.119108	2025-04-08 09:40:34.119108	f
ATT-20231106-e4973e	HR-EMP-2025-e4973e	2023-11-06	2023-11-06 09:20:00	2023-11-06 17:20:00	Late	0.33	0.00	f	\N	2025-04-08 09:40:34.119108	2025-04-08 09:40:34.119108	f
ATT-20231107-e4973e	HR-EMP-2025-e4973e	2023-11-07	2023-11-07 08:50:00	2023-11-07 17:00:00	Present	0.00	0.00	f	\N	2025-04-08 09:40:34.119108	2025-04-08 09:40:34.119108	f
ATT-20231108-e4973e	HR-EMP-2025-e4973e	2023-11-08	\N	\N	Absent	0.00	8.00	f	\N	2025-04-08 09:40:34.119108	2025-04-08 09:40:34.119108	f
ATT-20231109-e4973e	HR-EMP-2025-e4973e	2023-11-09	2023-11-09 08:55:00	2023-11-09 17:10:00	Present	0.00	0.00	f	\N	2025-04-08 09:40:34.119108	2025-04-08 09:40:34.119108	f
ATT-20231110-e4973e	HR-EMP-2025-e4973e	2023-11-10	2023-11-10 09:30:00	2023-11-10 17:25:00	Late	0.50	0.00	f	\N	2025-04-08 09:40:34.119108	2025-04-08 09:40:34.119108	f
ATT-20231106-6bcb48	HR-EMP-2025-6bcb48	2023-11-06	2023-11-06 08:40:00	2023-11-06 16:50:00	Present	0.00	0.17	f	\N	2025-04-08 09:40:34.119108	2025-04-08 09:40:34.119108	f
ATT-20231108-6bcb48	HR-EMP-2025-6bcb48	2023-11-08	2023-11-08 08:50:00	2023-11-08 16:55:00	Present	0.00	0.08	f	\N	2025-04-08 09:40:34.119108	2025-04-08 09:40:34.119108	f
ATT-20231109-6bcb48	HR-EMP-2025-6bcb48	2023-11-09	\N	\N	Absent	0.00	8.00	f	\N	2025-04-08 09:40:34.119108	2025-04-08 09:40:34.119108	f
ATT-20231110-6bcb48	HR-EMP-2025-6bcb48	2023-11-10	2023-11-10 08:55:00	2023-11-10 17:00:00	Present	0.00	0.00	f	\N	2025-04-08 09:40:34.119108	2025-04-08 09:40:34.119108	f
ATT-20231113-000a28	HR-EMP-2025-000a28	2023-11-13	2023-11-13 09:05:00	2023-11-13 17:05:00	Late	0.08	0.00	f	\N	2025-04-08 09:40:34.119108	2025-04-08 09:40:34.119108	f
ATT-20231114-000a28	HR-EMP-2025-000a28	2023-11-14	2023-11-14 08:50:00	2023-11-14 17:00:00	Present	0.00	0.00	f	\N	2025-04-08 09:40:34.119108	2025-04-08 09:40:34.119108	f
ATT-20231115-000a28	HR-EMP-2025-000a28	2023-11-15	2023-11-15 08:55:00	2023-11-15 17:10:00	Present	0.00	0.00	t	Special	2025-04-08 09:40:34.119108	2025-04-08 09:40:34.119108	f
ATT-20231117-000a28	HR-EMP-2025-000a28	2023-11-17	2023-11-17 08:50:00	2023-11-17 17:05:00	Present	0.00	0.00	f	\N	2025-04-08 09:40:34.119108	2025-04-08 09:40:34.119108	f
	HR-EMP-2025-000a28	2025-04-11	2025-04-11 06:15:30.842143	\N	Present	0.00	0.00	f	\N	2025-04-11 06:15:30.842302	2025-04-11 06:15:30.842903	f
ATT-20231108-bb6f41	HR-EMP-2025-bb6f41	2023-11-08	2023-11-08 08:55:00	2023-11-08 16:30:00	Absent	0.00	0.50	f	\N	2025-04-08 09:40:34.119108	2025-04-11 17:59:50.848795	f
ATT-20231110-bb6f41	HR-EMP-2025-bb6f41	2023-11-10	2023-11-10 08:45:00	2023-11-10 15:00:00	Absent	0.00	2.00	f	\N	2025-04-08 09:40:34.119108	2025-04-11 17:59:50.848795	f
ATT-20231107-6bcb48	HR-EMP-2025-6bcb48	2023-11-07	2023-11-07 08:45:00	2023-11-07 12:00:00	Absent	0.00	4.00	f	\N	2025-04-08 09:40:34.119108	2025-04-11 17:59:50.848795	f
ATT-20231116-000a28	HR-EMP-2025-000a28	2023-11-16	2023-11-16 08:45:00	2023-11-16 16:00:00	Absent	0.00	1.00	f	\N	2025-04-08 09:40:34.119108	2025-04-11 17:59:50.848795	f
\.


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add user	4	add_user
14	Can change user	4	change_user
15	Can delete user	4	delete_user
16	Can view user	4	view_user
17	Can add content type	5	add_contenttype
18	Can change content type	5	change_contenttype
19	Can delete content type	5	delete_contenttype
20	Can view content type	5	view_contenttype
21	Can add session	6	add_session
22	Can change session	6	change_session
23	Can delete session	6	delete_session
24	Can view session	6	view_session
25	Can add department	7	add_department
26	Can change department	7	change_department
27	Can delete department	7	delete_department
28	Can view department	7	view_department
29	Can add position	8	add_position
30	Can change position	8	change_position
31	Can delete position	8	delete_position
32	Can view position	8	view_position
33	Can add employee	9	add_employee
34	Can change employee	9	change_employee
35	Can delete employee	9	delete_employee
36	Can view employee	9	view_employee
37	Can add department superior	10	add_departmentsuperior
38	Can change department superior	10	change_departmentsuperior
39	Can delete department superior	10	delete_departmentsuperior
40	Can view department superior	10	view_departmentsuperior
41	Can add attendance	11	add_attendance
42	Can change attendance	11	change_attendance
43	Can delete attendance	11	delete_attendance
44	Can view attendance	11	view_attendance
45	Can add employee performance	13	add_employeeperformance
46	Can change employee performance	13	change_employeeperformance
47	Can delete employee performance	13	delete_employeeperformance
48	Can view employee performance	13	view_employeeperformance
49	Can add employee salary	12	add_employeesalary
50	Can change employee salary	12	change_employeesalary
51	Can delete employee salary	12	delete_employeesalary
52	Can view employee salary	12	view_employeesalary
53	Can add workforce allocation	14	add_workforceallocation
54	Can change workforce allocation	14	change_workforceallocation
55	Can delete workforce allocation	14	delete_workforceallocation
56	Can view workforce allocation	14	view_workforceallocation
57	Can add department	15	add_department
58	Can change department	15	change_department
59	Can delete department	15	delete_department
60	Can view department	15	view_department
61	Can add position	16	add_position
62	Can change position	16	change_position
63	Can delete position	16	delete_position
64	Can view position	16	view_position
65	Can add employee	17	add_employee
66	Can change employee	17	change_employee
67	Can delete employee	17	delete_employee
68	Can view employee	17	view_employee
69	Can add attendance_ tracking	18	add_attendance_tracking
70	Can change attendance_ tracking	18	change_attendance_tracking
71	Can delete attendance_ tracking	18	delete_attendance_tracking
72	Can view attendance_ tracking	18	view_attendance_tracking
73	Can add employee_ performance	19	add_employee_performance
74	Can change employee_ performance	19	change_employee_performance
75	Can delete employee_ performance	19	delete_employee_performance
76	Can view employee_ performance	19	view_employee_performance
77	Can add workforce_ allocation	20	add_workforce_allocation
78	Can change workforce_ allocation	20	change_workforce_allocation
79	Can delete workforce_ allocation	20	delete_workforce_allocation
80	Can view workforce_ allocation	20	view_workforce_allocation
81	Can add Calendar Dates	21	add_calendar_date
82	Can change Calendar Dates	21	change_calendar_date
83	Can delete Calendar Dates	21	delete_calendar_date
84	Can view Calendar Dates	21	view_calendar_date
85	Can add Department Superiors	22	add_department_superior
86	Can change Department Superiors	22	change_department_superior
87	Can delete Department Superiors	22	delete_department_superior
88	Can view Department Superiors	22	view_department_superior
89	Can add Employee Salary	23	add_employee_salary
90	Can change Employee Salary	23	change_employee_salary
91	Can delete Employee Salary	23	delete_employee_salary
92	Can view Employee Salary	23	view_employee_salary
93	Can add historical department	24	add_historicaldepartment
94	Can change historical department	24	change_historicaldepartment
95	Can delete historical department	24	delete_historicaldepartment
96	Can view historical department	24	view_historicaldepartment
97	Can add historical Department Superiors	25	add_historicaldepartment_superior
98	Can change historical Department Superiors	25	change_historicaldepartment_superior
99	Can delete historical Department Superiors	25	delete_historicaldepartment_superior
100	Can view historical Department Superiors	25	view_historicaldepartment_superior
101	Can add historical position	26	add_historicalposition
102	Can change historical position	26	change_historicalposition
103	Can delete historical position	26	delete_historicalposition
104	Can view historical position	26	view_historicalposition
105	Can add historical employee	27	add_historicalemployee
106	Can change historical employee	27	change_historicalemployee
107	Can delete historical employee	27	delete_historicalemployee
108	Can view historical employee	27	view_historicalemployee
\.


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
1	pbkdf2_sha256$870000$SiSuA4Zlh4uj6287A6Pjay$he4WrjYrazUiCsXRM9QpXqCaOrgfJanogRdlKv54D7I=	2025-04-04 08:08:35.944355+08	t	admin				t	t	2025-04-04 08:08:19.075303+08
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: calendar_dates; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.calendar_dates (date, is_workday, is_holiday, is_special, holiday_name, holiday_type) FROM stdin;
2023-11-06	t	f	f	\N	\N
2023-11-07	t	f	f	\N	\N
2023-11-08	t	f	f	\N	\N
2023-11-09	t	f	f	\N	\N
2023-11-10	t	f	f	\N	\N
2023-11-13	t	f	f	\N	\N
2023-11-14	t	f	f	\N	\N
2023-11-15	f	t	t	Special Holiday	\N
2023-11-16	t	f	f	\N	\N
2023-11-17	t	f	f	\N	\N
2023-11-20	t	f	f	\N	\N
2023-11-21	t	f	f	\N	\N
2023-11-22	t	f	f	\N	\N
2023-11-23	t	t	f	Thanksgiving Day	\N
2023-11-24	t	f	f	\N	\N
2023-11-25	f	f	f	\N	\N
2023-11-26	f	f	f	\N	\N
2023-11-27	t	f	f	\N	\N
2023-11-28	t	f	f	\N	\N
2023-11-29	t	f	f	\N	\N
2023-11-30	t	f	f	\N	\N
2025-04-09	t	f	f	\N	\N
2025-04-11	t	f	f	\N	\N
\.


--
-- Data for Name: candidates; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.candidates (candidate_id, job_id, first_name, last_name, email, phone, resume_path, application_status, documents, interview_details, offer_details, contract_details, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: department_superiors; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.department_superiors (dept_id, position_id, hierarchy_level, is_archived, dept_superior_id, change_reason) FROM stdin;
HR-DEPT-2025-345995	REG-2504-eb03	1	t	DEPT-SUP-2025-f67f52	\N
HR-DEPT-2025-0fac18	REG-2504-5eef	1	f	DEPT-SUP-2025-0b38e4	\N
HR-DEPT-2025-cca1d0	REG-2504-fb38	1	f	DEPT-SUP-2025-72f18b	\N
HR-DEPT-2025-3bb2ca	REG-2504-8ab5	4	f	DEPT-SUP-2025-9fd37c	\N
HR-DEPT-2025-26b8a4	REG-2504-9b2a	1	f	DEPT-SUP-2025-716d98	\N
HR-DEPT-2025-de1518	REG-2504-6363	2	f	DEPT-SUP-2025-418f26	\N
HR-DEPT-2025-185182	REG-2504-d999	1	f	DEPT-SUP-2025-9159e6	\N
HR-DEPT-2025-2e0d12	REG-2504-a218	1	f	DEPT-SUP-2025-e18587	\N
HR-DEPT-2025-bfc4cb	CTR-2504-99c0	2	f	DEPT-SUP-2025-881d4d	\N
HR-DEPT-2025-de1518	REG-2504-f87e	1	f	DEPT-SUP-2025-ac0265	\N
HR-DEPT-2025-bcff30	REG-2504-fb50	1	f	DEPT-SUP-2025-9c9e59	\N
HR-DEPT-2025-2e0d12	REG-2504-d2b8	2	f	DEPT-SUP-2025-4ba3ab	\N
HR-DEPT-2025-0272fb	REG-2504-3a8e	2	f	DEPT-SUP-2025-7390db	\N
HR-DEPT-2025-0272fb	REG-2504-cce8	1	f	DEPT-SUP-2025-6fb448	\N
HR-DEPT-2025-0360bf	REG-2504-131f	1	f	DEPT-SUP-2025-c6cb75	\N
HR-DEPT-2025-26b8a4	REG-2504-4e93	2	f	DEPT-SUP-2025-18d439	\N
HR-DEPT-2025-f57fbb	REG-2504-0bef	2	f	DEPT-SUP-2025-5c1f91	\N
HR-DEPT-2025-75008b	REG-2504-a794	1	f	DEPT-SUP-2025-9a000f	\N
HR-DEPT-2025-f57fbb	REG-2504-8d4e	1	f	DEPT-SUP-2025-8c709f	\N
HR-DEPT-2025-f57fbb	REG-2504-a218	3	f	DEPT-SUP-2025-28c8fc	\N
HR-DEPT-2025-3bb2ca	REG-2504-a0dd	5	t	DEPT-SUP-2025-f5eb09	\N
HR-DEPT-2025-839a42	CTR-2504-99c0	1	f	DEPT-SUP-2025-d3738c	\N
HR-DEPT-2025-bfc4cb	REG-2504-8731	1	f	DEPT-SUP-2025-0177dd	\N
\.


--
-- Data for Name: department_superiors_historicaldepartment_superior; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.department_superiors_historicaldepartment_superior (dept_superior_id, hierarchy_level, is_archived, change_reason, history_id, history_date, history_change_reason, history_type, dept_id, history_user_id, position_id) FROM stdin;
\.


--
-- Data for Name: departments; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.departments (dept_id, dept_name, is_archived, created_by_id, updated_by_id, change_reason) FROM stdin;
HR-DEPT-2025-26b8a4	Accounting	f	\N	\N	\N
HR-DEPT-2025-0272fb	Administration	f	\N	\N	\N
HR-DEPT-2025-345995	Distribution	f	\N	\N	\N
HR-DEPT-2025-2e0d12	Finance	f	\N	\N	\N
HR-DEPT-2025-cca1d0	Inventory	f	\N	\N	\N
HR-DEPT-2025-f57fbb	Management	f	\N	\N	\N
HR-DEPT-2025-75008b	Operations	f	\N	\N	\N
HR-DEPT-2025-0360bf	Production	f	\N	\N	\N
HR-DEPT-2025-0fac18	Project Management	f	\N	\N	\N
HR-DEPT-2025-185182	Purchasing	f	\N	\N	\N
HR-DEPT-2025-bcff30	Sales	f	\N	\N	\N
HR-DEPT-2025-bfc4cb	Services	f	\N	\N	\N
HR-DEPT-2025-7e9a3b	Maintenance & Facilities	f	\N	\N	\N
HR-DEPT-2025-318899	IT & Technical Support	f	\N	\N	\N
HR-DEPT-2025-7a2d06	Quality Assurance & Compliance	f	\N	\N	\N
HR-DEPT-2025-fc8d58	Health, Safety, and Environment	f	\N	\N	\N
HR-DEPT-2025-a118dc	Security	f	\N	\N	\N
HR-DEPT-2025-2a7fd6	asdasdsadas	t	\N	\N	\N
HR-DEPT-2025-fc0aa6	Test Departa	t	\N	\N	\N
HR-DEPT-2025-ff3754	Test Department	t	\N	\N	\N
HR-DEPT-2025-573cc6	asd	t	\N	\N	\N
HR-DEPT-2025-839a42	AYOO WTF!	t	\N	\N	\N
HR-DEPT-2025-9ba632	Department of Slavery and Peasantry - Edited	t	\N	\N	\N
HR-DEPT-2025-de1518	Human Resource	f	\N	\N	\N
HR-DEPT-2025-a1792e	Mark - EDITED	t	\N	\N	\N
HR-DEPT-2025-3bb2ca	Material Resource Planning	f	\N	\N	\N
HR-DEPT-2025-362ae3	Department of Slavery	f	\N	\N	Reverted
\.


--
-- Data for Name: departments_department; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.departments_department (dept_id, name) FROM stdin;
\.


--
-- Data for Name: departments_historicaldepartment; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.departments_historicaldepartment (dept_id, dept_name, is_archived, history_id, history_date, history_change_reason, history_type, history_user_id, change_reason) FROM stdin;
HR-DEPT-2025-7b8e92	Hehehe	f	39	2025-04-10 16:04:26.809935+08	\N	-	1	Wala da
HR-DEPT-2025-98bec8	Hello	f	40	2025-04-10 16:04:30.40276+08	\N	-	1	Hi
HR-DEPT-2025-288e84	c	f	41	2025-04-10 16:07:20.370214+08	\N	-	1	\N
HR-DEPT-2025-87ad87	Test Departamentor	f	42	2025-04-10 16:07:25.364371+08	\N	-	1	sada
HR-DEPT-2025-362ae3	Department of Slavery	f	43	2025-04-10 16:08:21.004236+08	\N	~	1	\N
HR-DEPT-2025-362ae3	Department of Slavery and Peasantry	f	44	2025-04-10 16:08:37.230744+08	Hello	~	1	Hello
HR-DEPT-2025-362ae3	Department of Slavery	f	45	2025-04-10 16:10:21.547822+08	Reverted	~	1	Reverted
HR-DEPT-2025-e330d7	Department of Slaveryresadsa	f	36	2025-04-10 16:04:13.541861+08	\N	-	1	Edited to Slaveryredd
HR-DEPT-2025-542c22	ddsds	f	37	2025-04-10 16:04:21.483891+08	\N	-	1	edsadasd
HR-DEPT-2025-4bf695	f	f	38	2025-04-10 16:04:24.089011+08	\N	-	1	\N
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2025-04-04 09:35:53.132823+08	HR-DEPT-2025-efce4e	AYOO WTF!	1	[{"added": {}}]	7	1
2	2025-04-04 09:38:39.942701+08	HR-DEPT-2025-24c3af	Test Departamento	1	[{"added": {}}]	7	1
3	2025-04-04 09:39:01.05454+08	REG-2504-7a88	POS01 (Regular)	1	[{"added": {}}]	8	1
4	2025-04-04 09:39:58.250112+08	EMP-e8ffa9	Laygo Jhon (EMP-e8ffa9)	1	[{"added": {}}]	9	1
5	2025-04-04 14:47:00.832942+08	AHAHA	HR-EMP-2025-64d72e - AHAHA	1	[{"added": {}}]	11	1
6	2025-04-04 14:47:10.630014+08	AHAHA	HR-EMP-2025-64d72e - AHAHA	3		11	1
7	2025-04-04 14:47:18.597343+08	AHAHA	HR-EMP-2025-64d72e - AHAHA	1	[{"added": {}}]	11	1
8	2025-04-04 14:48:28.414512+08	perf	perf - HR-EMP-2025-64d72e	1	[{"added": {}}]	13	1
9	2025-04-04 15:04:15.796806+08	AHAHA	HR-EMP-2025-64d72e - AHAHA	3		11	1
10	2025-04-04 15:04:26.019611+08	HR-PERF-2025-30b019	HR-PERF-2025-30b019 - HR-EMP-2025-64d72e	3		13	1
11	2025-04-04 16:38:02.253603+08	HR-EMP-2025-4e7df6	Charles Martel (HR-EMP-2025-4e7df6)	2	[{"changed": {"fields": ["First name", "Last name"]}}]	9	1
12	2025-04-04 16:39:57.302578+08	perf	perf - HR-EMP-2025-4e7df6	1	[{"added": {}}]	13	1
13	2025-04-04 16:40:04.418239+08	HR-PERF-2025-ec0836	HR-PERF-2025-ec0836 - HR-EMP-2025-4e7df6	3		13	1
14	2025-04-04 16:43:27.010509+08	ATT000	HR-EMP-2025-4e7df6 - ATT000	1	[{"added": {}}]	11	1
15	2025-04-04 16:44:04.841045+08	PER000	PER000 - HR-EMP-2025-4e7df6	1	[{"added": {}}]	13	1
16	2025-04-04 17:15:11.574687+08	SAL	SAL - HR-EMP-2025-4e7df6	1	[{"added": {}}]	12	1
17	2025-04-04 17:23:24.748272+08	EMP-bc7d86	Julius Caesar (EMP-bc7d86)	1	[{"added": {}}]	9	1
18	2025-04-05 09:11:09.72211+08	AT000	HR-EMP-2025-4e7df6 - AT000	1	[{"added": {}}]	11	1
19	2025-04-05 09:11:39.870813+08	PER00	PER00 - HR-EMP-2025-6304af	1	[{"added": {}}]	13	1
20	2025-04-05 09:12:02.29012+08	SAL01	SAL01 - HR-EMP-2025-6304af	1	[{"added": {}}]	12	1
21	2025-04-05 09:13:35.407015+08	ALLOC01	ALLOC01 - REC01	1	[{"added": {}}]	14	1
22	2025-04-05 09:13:56.880718+08	ALLOC0333	ALLOC0333 - REC01XD	1	[{"added": {}}]	14	1
23	2025-04-05 09:43:12.522913+08	SAL-202504-d3b96a	SAL-202504-d3b96a - HR-EMP-2025-f6cc85	2	[{"changed": {"fields": ["Daily rate"]}}]	12	1
24	2025-04-05 09:52:17.960123+08	SAL-202504-ff1449	SAL-202504-ff1449 - HR-EMP-2025-63e214	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
25	2025-04-05 13:32:12.846895+08	HR-PERF-2025-e55a45	HR-PERF-2025-e55a45 - HR-EMP-2025-384581	2	[{"changed": {"fields": ["Comments", "Bonus payment month"]}}]	13	1
26	2025-04-05 13:38:10.769238+08	HR-PERF-2025-e55a45	HR-PERF-2025-e55a45 - HR-EMP-2025-384581	2	[{"changed": {"fields": ["Comments", "Bonus payment month"]}}]	13	1
27	2025-04-05 13:38:36.442427+08	SAL-202504-fbc204	SAL-202504-fbc204 - HR-EMP-2025-63e214	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
28	2025-04-05 13:44:50.075114+08	SAL-202504-f69dc3	SAL-202504-f69dc3 - HR-EMP-2025-169617	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
29	2025-04-05 13:47:41.892147+08	SAL-202504-b712c8	SAL-202504-b712c8 - HR-EMP-2025-169617	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
30	2025-04-05 13:56:28.869813+08	HR-EMP-2025-f6cc85	Priyas Patel (HR-EMP-2025-f6cc85)	2	[{"changed": {"fields": ["Position id", "First name"]}}]	9	1
31	2025-04-05 13:56:51.706103+08	REG-2504-7a88	Test Position (Regular)	2	[{"changed": {"fields": ["Position title"]}}]	8	1
32	2025-04-05 13:57:02.734431+08	SAL-202504-e1f4b0	SAL-202504-e1f4b0 - HR-EMP-2025-64e9cc	2	[{"changed": {"fields": ["Daily rate"]}}]	12	1
33	2025-04-05 13:57:15.414343+08	SAL-202504-df7e8b	SAL-202504-df7e8b - HR-EMP-2025-e6dbcd	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
34	2025-04-05 13:57:58.948148+08	HR-ATT	HR-EMP-2025-aedda9 - HR-ATT	2	[{"changed": {"fields": ["Attendance id", "Work hours"]}}]	11	1
35	2025-04-05 13:58:57.424358+08	SAL-202504-fc6aba	SAL-202504-fc6aba - HR-EMP-2025-e6dbcd	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
36	2025-04-05 14:01:18.200397+08	SAL-202504-d72e83	SAL-202504-d72e83 - HR-EMP-2025-e6dbcd	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
37	2025-04-05 14:01:22.29392+08	SAL-202504-d600d2	SAL-202504-d600d2 - HR-EMP-2025-64e9cc	2	[{"changed": {"fields": ["Daily rate"]}}]	12	1
38	2025-04-05 14:01:26.0371+08	SAL-202504-cdf282	SAL-202504-cdf282 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
39	2025-04-05 14:01:42.569997+08	SAL-202504-2e511a	SAL-202504-2e511a - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
40	2025-04-05 14:03:36.163719+08	SAL-202504-dd0fc5	SAL-202504-dd0fc5 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
41	2025-04-05 14:06:16.094933+08	SAL-202504-2721b1	SAL-202504-2721b1 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
42	2025-04-05 14:15:18.925178+08	SAL-202504-c53126	SAL-202504-c53126 - HR-EMP-2025-a94e18	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
43	2025-04-05 14:37:58.146983+08	SAL-202504-78f073	SAL-202504-78f073 - HR-EMP-2025-af9c27	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
44	2025-04-05 14:42:40.494352+08	SAL-202504-c0b731	SAL-202504-c0b731 - HR-EMP-2025-1f5dd3	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
45	2025-04-05 14:46:12.278889+08	EMP-1b1233	Holy Tom Tom (EMP-1b1233)	1	[{"added": {}}]	9	1
46	2025-04-05 14:46:26.096384+08	Sal01	Sal01 - HR-EMP-2025-89fa46	1	[{"added": {}}]	12	1
47	2025-04-05 14:59:33.552386+08	HR-PERF-2025-c0eb1c	HR-PERF-2025-c0eb1c - HR-EMP-2025-6304af	2	[{"changed": {"fields": ["Comments", "Bonus payment month"]}}]	13	1
48	2025-04-05 14:59:47.711032+08	SAL-202504-bc53a6	SAL-202504-bc53a6 - HR-EMP-2025-384581	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
49	2025-04-05 14:59:54.986625+08	SAL-202504-0acc39	SAL-202504-0acc39 - HR-EMP-2025-a94e18	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
50	2025-04-05 15:14:38.870906+08	HR-DEPT-2025-228414	WEASA	2	[{"changed": {"fields": ["Dept name"]}}]	7	1
51	2025-04-05 15:16:56.223127+08	HR-DEPT-2025-0101aa	asdasdsadas	1	[{"added": {}}]	7	1
52	2025-04-05 15:18:15.168115+08	HR-DEPT-2025-ff3754	HR-DEPT-2025-ff3754 - HR Manager (Level 2)	2	[{"changed": {"fields": ["Hierarchy level"]}}]	10	1
53	2025-04-05 15:18:22.023971+08	HR-DEPT-2025-ff3754	HR-DEPT-2025-ff3754 - HR Manager (Level 1)	2	[{"changed": {"fields": ["Hierarchy level"]}}]	10	1
54	2025-04-05 15:20:05.05077+08	SEA-2504-60fb	New Year Event Staffs (Seasonal)	2	[{"changed": {"fields": ["Position title"]}}]	8	1
55	2025-04-05 15:21:27.474147+08	REG-2504-a3f4	ASDASD (Regular)	1	[{"added": {}}]	8	1
56	2025-04-05 15:21:47.224446+08	REG-2504-a3f4	ASDASD (Regular)	2	[{"changed": {"fields": ["Salary grade"]}}]	8	1
57	2025-04-05 15:24:51.543443+08	HR-EMP-2025-4e7df6	Charlemagne Martel (HR-EMP-2025-4e7df6)	2	[{"changed": {"fields": ["First name"]}}]	9	1
58	2025-04-05 15:29:21.493762+08	HR-DEPT-2025-ff3754	HR-DEPT-2025-ff3754 - HR Manager (Level 5)	2	[{"changed": {"fields": ["Hierarchy level"]}}]	10	1
59	2025-04-05 15:33:36.028846+08	HR-DEPT-2025-ff3754	HR-DEPT-2025-ff3754 - HR Manager (Level 1)	2	[{"changed": {"fields": ["Hierarchy level"]}}]	10	1
60	2025-04-05 15:58:03.650002+08	EMP-626d6b	DSFSD ASDAS (EMP-626d6b)	1	[{"added": {}}]	9	1
61	2025-04-05 15:59:31.181958+08	EMP-811564	CONTRACTUAL GUY (EMP-811564)	1	[{"added": {}}]	9	1
62	2025-04-05 16:01:52.02392+08	sal013	sal013 - HR-EMP-2025-193fd4	1	[{"added": {}}]	12	1
63	2025-04-05 16:07:24.142285+08	PER01	PER01 - HR-EMP-2025-193fd4	1	[{"added": {}}]	13	1
64	2025-04-05 22:28:59.896485+08	CTR-2504-9554	Project Accountant (Contractual)	2	[{"changed": {"fields": ["Typical duration days"]}}]	8	1
65	2025-04-05 22:45:01.042014+08	HR-EMP-2025-d42736	Michael Chen (HR-EMP-2025-d42736)	2	[{"changed": {"fields": ["Position id"]}}]	9	1
66	2025-04-05 22:52:07.598218+08	HR-DEPT-2025-ff3754	HR-DEPT-2025-ff3754 - HR Manager (Level 5)	2	[{"changed": {"fields": ["Hierarchy level"]}}]	10	1
67	2025-04-05 22:52:12.319979+08	HR-DEPT-2025-ff3754	HR-DEPT-2025-ff3754 - HR Manager (Level 1)	2	[{"changed": {"fields": ["Hierarchy level"]}}]	10	1
68	2025-04-05 22:53:48.107977+08	CTR-2504-f23e	Audit Assistant (Contractual)	2	[{"changed": {"fields": ["Typical duration days"]}}]	8	1
69	2025-04-05 22:54:35.288752+08	CTR-2504-e8a4	System Migration Consultant (Contractual)	2	[{"changed": {"fields": ["Typical duration days"]}}]	8	1
70	2025-04-05 22:56:32.267917+08	REG-2504-20bc	SASA (Regular)	1	[{"added": {}}]	8	1
71	2025-04-05 23:09:19.327366+08	sal024	sal024 - HR-EMP-2025-765d64	1	[{"added": {}}]	12	1
72	2025-04-05 23:10:58.140411+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Bonus payment month"]}}]	13	1
73	2025-04-05 23:16:52.302373+08	ALLOC-202504-1325	ALLOC-202504-1325 - REC021XD	2	[{"changed": {"fields": ["Request id"]}}]	14	1
74	2025-04-06 00:21:33.701289+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Bonus amount"]}}]	13	1
75	2025-04-06 00:21:38.700151+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Bonus amount"]}}]	13	1
76	2025-04-06 00:21:47.137743+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Bonus amount"]}}]	13	1
77	2025-04-06 00:21:47.202317+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[]	13	1
78	2025-04-06 00:33:01.722116+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Bonus amount"]}}]	13	1
79	2025-04-06 00:36:29.509062+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Bonus amount"]}}]	13	1
80	2025-04-06 00:36:29.568813+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Bonus amount"]}}]	13	1
81	2025-04-06 00:36:36.274784+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Bonus amount"]}}]	13	1
82	2025-04-06 00:36:36.333737+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Bonus amount"]}}]	13	1
83	2025-04-06 00:36:56.144816+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Bonus amount"]}}]	13	1
84	2025-04-06 00:36:56.188052+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Bonus amount"]}}]	13	1
85	2025-04-06 00:53:38.74932+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Rating", "Bonus payment month"]}}]	13	1
86	2025-04-06 00:53:44.714052+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Rating"]}}]	13	1
87	2025-04-06 00:53:48.851432+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Rating"]}}]	13	1
88	2025-04-06 00:53:52.379013+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Rating"]}}]	13	1
89	2025-04-06 00:53:52.468125+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[]	13	1
90	2025-04-06 00:53:56.369852+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Rating"]}}]	13	1
91	2025-04-06 00:59:53.349348+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Rating"]}}]	13	1
92	2025-04-06 00:59:59.3913+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Rating"]}}]	13	1
93	2025-04-06 01:02:52.504609+08	SAL-202504-a8a2fb	SAL-202504-a8a2fb - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Daily rate"]}}]	12	1
94	2025-04-06 01:03:03.207122+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[]	13	1
95	2025-04-06 01:05:47.871976+08	SAL-202504-e9c8a3	SAL-202504-e9c8a3 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Contract end date"]}}]	12	1
96	2025-04-06 01:06:00.316389+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[]	13	1
97	2025-04-06 01:06:04.567865+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Bonus payment month"]}}]	13	1
98	2025-04-06 01:06:11.177753+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Bonus payment month"]}}]	13	1
99	2025-04-06 01:07:36.654348+08	SAL-202504-c3fb86	SAL-202504-c3fb86 - HR-EMP-2025-193fd4	2	[{"changed": {"fields": ["Daily rate"]}}]	12	1
100	2025-04-06 01:07:41.454656+08	PER01	PER01 - HR-EMP-2025-193fd4	2	[]	13	1
101	2025-04-06 01:07:50.144058+08	HR-PERF-2025-e55a45	HR-PERF-2025-e55a45 - HR-EMP-2025-384581	2	[]	13	1
102	2025-04-06 01:08:34.768314+08	SAL-202504-b849f4	SAL-202504-b849f4 - HR-EMP-2025-e3eea9	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
103	2025-04-06 01:08:42.568366+08	HR-PERF-2025-0094c7	HR-PERF-2025-0094c7 - HR-EMP-2025-e3eea9	2	[{"changed": {"fields": ["Rating"]}}]	13	1
104	2025-04-06 01:12:11.504774+08	HR-PERF-2025-0094c7	HR-PERF-2025-0094c7 - HR-EMP-2025-e3eea9	2	[]	13	1
105	2025-04-06 01:12:15.478213+08	HR-PERF-2025-0094c7	HR-PERF-2025-0094c7 - HR-EMP-2025-e3eea9	2	[{"changed": {"fields": ["Rating"]}}]	13	1
106	2025-04-06 01:12:19.321744+08	HR-PERF-2025-0094c7	HR-PERF-2025-0094c7 - HR-EMP-2025-e3eea9	2	[{"changed": {"fields": ["Rating"]}}]	13	1
107	2025-04-06 01:12:19.518662+08	HR-PERF-2025-0094c7	HR-PERF-2025-0094c7 - HR-EMP-2025-e3eea9	2	[]	13	1
108	2025-04-06 01:12:23.593616+08	HR-PERF-2025-0094c7	HR-PERF-2025-0094c7 - HR-EMP-2025-e3eea9	2	[{"changed": {"fields": ["Rating"]}}]	13	1
109	2025-04-06 01:14:58.182862+08	SAL-202504-92a70d	SAL-202504-92a70d - HR-EMP-2025-f6cc85	2	[{"changed": {"fields": ["Daily rate"]}}]	12	1
110	2025-04-06 01:15:13.704808+08	SAL-202504-553096	SAL-202504-553096 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
111	2025-04-06 01:15:25.755484+08	HR-PERF-2025-d37087	HR-PERF-2025-d37087 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
112	2025-04-06 01:15:25.851873+08	HR-PERF-2025-d37087	HR-PERF-2025-d37087 - HR-EMP-2025-4e7df6	2	[]	13	1
113	2025-04-06 01:19:09.638217+08	SAL-202504-82ae37	SAL-202504-82ae37 - HR-EMP-2025-4e7df6	2	[]	12	1
114	2025-04-06 01:22:24.465975+08	HR-PERF-2025-d37087	HR-PERF-2025-d37087 - HR-EMP-2025-4e7df6	2	[]	13	1
115	2025-04-06 01:22:33.984903+08	HR-PERF-2025-d37087	HR-PERF-2025-d37087 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Bonus payment month"]}}]	13	1
116	2025-04-06 01:27:09.587674+08	HR-PERF-2025-d37087	HR-PERF-2025-d37087 - HR-EMP-2025-4e7df6	2	[]	13	1
117	2025-04-06 01:27:15.295929+08	HR-PERF-2025-d37087	HR-PERF-2025-d37087 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
118	2025-04-06 07:19:21.193056+08	HR-PERF-2025-d37087	HR-PERF-2025-d37087 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
119	2025-04-06 07:20:14.43831+08	HR-PERF-2025-d37087	HR-PERF-2025-d37087 - HR-EMP-2025-4e7df6	2	[]	13	1
120	2025-04-06 07:20:14.504686+08	HR-PERF-2025-d37087	HR-PERF-2025-d37087 - HR-EMP-2025-4e7df6	2	[]	13	1
121	2025-04-06 08:23:16.938029+08	HR-PERF-2025-d37087	HR-PERF-2025-d37087 - HR-EMP-2025-4e7df6	2	[]	13	1
122	2025-04-06 08:25:57.613935+08	HR-PERF-2025-d37087	HR-PERF-2025-d37087 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
123	2025-04-06 08:26:03.09648+08	HR-PERF-2025-d37087	HR-PERF-2025-d37087 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
124	2025-04-06 08:30:53.962708+08	SAL-202504-a9c0f4	SAL-202504-a9c0f4 - HR-EMP-2025-6304af	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
125	2025-04-06 08:31:30.805809+08	HR-PERF-2025-c0eb1c	HR-PERF-2025-c0eb1c - HR-EMP-2025-6304af	2	[{"changed": {"fields": ["Rating", "Comments"]}}]	13	1
126	2025-04-06 08:48:01.583061+08	HR-PERF-2025-d37087	HR-PERF-2025-d37087 - HR-EMP-2025-4e7df6	2	[]	13	1
127	2025-04-06 08:48:09.333102+08	HR-PERF-2025-c0eb1c	HR-PERF-2025-c0eb1c - HR-EMP-2025-6304af	2	[]	13	1
128	2025-04-06 08:48:24.936793+08	HR-PERF-2025-e2bfed	HR-PERF-2025-e2bfed - HR-EMP-2025-4e7df6	2	[]	13	1
129	2025-04-06 08:58:50.600234+08	HR-PERF-2025-0f1dcc	HR-PERF-2025-0f1dcc - HR-EMP-2025-4e7df6	2	[]	13	1
130	2025-04-06 08:58:56.268328+08	HR-PERF-2025-798f2c	HR-PERF-2025-798f2c - HR-EMP-2025-6304af	2	[]	13	1
131	2025-04-06 08:59:00.790846+08	HR-PERF-2025-069979	HR-PERF-2025-069979 - HR-EMP-2025-4e7df6	2	[]	13	1
132	2025-04-06 09:01:23.983394+08	HR-PERF-2025-a65ea8	HR-PERF-2025-a65ea8 - HR-EMP-2025-4e7df6	2	[]	13	1
133	2025-04-06 09:01:33.213619+08	HR-PERF-2025-9dc289	HR-PERF-2025-9dc289 - HR-EMP-2025-4e7df6	2	[]	13	1
134	2025-04-06 09:01:40.4631+08	HR-PERF-2025-78aa25	HR-PERF-2025-78aa25 - HR-EMP-2025-6304af	2	[]	13	1
135	2025-04-06 09:04:57.497382+08	HR-PERF-2025-5a5fc3	HR-PERF-2025-5a5fc3 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
136	2025-04-06 09:05:05.155075+08	HR-PERF-2025-ac776d	HR-PERF-2025-ac776d - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
137	2025-04-06 09:08:38.156382+08	HR-PERF-2025-21066e	HR-PERF-2025-21066e - HR-EMP-2025-4e7df6	2	[]	13	1
138	2025-04-06 09:10:28.663612+08	REG-2504-7a88	Test Position (Regular)	2	[{"changed": {"fields": ["Min salary", "Max salary"]}}]	8	1
139	2025-04-06 09:10:35.550609+08	SAL-202504-5cbd30	SAL-202504-5cbd30 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
140	2025-04-06 09:10:43.393894+08	HR-PERF-2025-34f3fe	HR-PERF-2025-34f3fe - HR-EMP-2025-4e7df6	2	[]	13	1
141	2025-04-06 09:10:47.824241+08	HR-PERF-2025-524625	HR-PERF-2025-524625 - HR-EMP-2025-4e7df6	2	[]	13	1
142	2025-04-06 09:11:04.710509+08	HR-PERF-2025-297798	HR-PERF-2025-297798 - HR-EMP-2025-4e7df6	2	[]	13	1
143	2025-04-06 09:11:11.050014+08	HR-PERF-2025-c4b66e	HR-PERF-2025-c4b66e - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
144	2025-04-06 09:11:34.132464+08	SAL-202504-d95016	SAL-202504-d95016 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
145	2025-04-06 09:11:57.084699+08	HR-PERF-2025-f60ac6	HR-PERF-2025-f60ac6 - HR-EMP-2025-4e7df6	2	[]	13	1
146	2025-04-06 09:16:00.950888+08	HR-PERF-2025-f4954d	HR-PERF-2025-f4954d - HR-EMP-2025-4e7df6	2	[]	13	1
147	2025-04-06 09:16:07.100029+08	HR-PERF-2025-610088	HR-PERF-2025-610088 - HR-EMP-2025-6304af	2	[{"changed": {"fields": ["Rating"]}}]	13	1
148	2025-04-06 09:16:11.613826+08	HR-PERF-2025-655509	HR-PERF-2025-655509 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
149	2025-04-06 09:16:15.6216+08	HR-PERF-2025-78b56e	HR-PERF-2025-78b56e - HR-EMP-2025-4e7df6	2	[]	13	1
150	2025-04-06 09:19:11.425797+08	HR-PERF-2025-6839a3	HR-PERF-2025-6839a3 - HR-EMP-2025-4e7df6	2	[]	13	1
151	2025-04-06 09:19:19.206215+08	HR-PERF-2025-eb7bd7	HR-PERF-2025-eb7bd7 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
152	2025-04-06 09:19:29.342466+08	HR-PERF-2025-2281ec	HR-PERF-2025-2281ec - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
153	2025-04-06 09:22:26.120807+08	HR-PERF-2025-96b417	HR-PERF-2025-96b417 - HR-EMP-2025-4e7df6	2	[]	13	1
154	2025-04-06 09:22:41.620533+08	HR-PERF-2025-4e54a2	HR-PERF-2025-4e54a2 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
155	2025-04-06 09:23:29.877984+08	HR-PERF-2025-ccf3bc	HR-PERF-2025-ccf3bc - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
156	2025-04-06 09:46:54.292108+08	HR-PERF-2025-838a30	HR-PERF-2025-838a30 - HR-EMP-2025-4e7df6	2	[]	13	1
157	2025-04-06 09:47:10.548495+08	HR-PERF-2025-523246	HR-PERF-2025-523246 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
158	2025-04-06 09:47:18.606065+08	HR-PERF-2025-0f7b0c	HR-PERF-2025-0f7b0c - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
159	2025-04-06 09:59:15.467306+08	HR-PERF-2025-e934d5	HR-PERF-2025-e934d5 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
160	2025-04-06 09:59:20.6599+08	HR-PERF-2025-3f9c08	HR-PERF-2025-3f9c08 - HR-EMP-2025-4e7df6	2	[]	13	1
161	2025-04-06 10:01:28.10477+08	HR-PERF-2025-333c9f	HR-PERF-2025-333c9f - HR-EMP-2025-4e7df6	2	[]	13	1
162	2025-04-06 10:01:38.867696+08	HR-PERF-2025-b6d119	HR-PERF-2025-b6d119 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
163	2025-04-06 10:06:18.210516+08	HR-PERF-2025-5feab7	HR-PERF-2025-5feab7 - HR-EMP-2025-4e7df6	2	[]	13	1
164	2025-04-06 10:21:19.475994+08	HR-PERF-2025-b193b0	HR-PERF-2025-b193b0 - HR-EMP-2025-4e7df6	2	[]	13	1
165	2025-04-06 10:26:50.618142+08	HR-PERF-2025-5574ef	HR-PERF-2025-5574ef - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
166	2025-04-06 10:29:00.506603+08	HR-PERF-2025-c0b7d8	HR-PERF-2025-c0b7d8 - HR-EMP-2025-4e7df6	2	[]	13	1
167	2025-04-06 10:32:15.493757+08	HR-PERF-2025-6a9dac	HR-PERF-2025-6a9dac - HR-EMP-2025-4e7df6	2	[]	13	1
168	2025-04-06 10:34:05.877244+08	SAL-202504-f32d65	SAL-202504-f32d65 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
169	2025-04-06 10:34:09.934648+08	HR-PERF-2025-4bf8a7	HR-PERF-2025-4bf8a7 - HR-EMP-2025-4e7df6	2	[]	13	1
170	2025-04-06 10:34:16.709211+08	HR-PERF-2025-02d7e1	HR-PERF-2025-02d7e1 - HR-EMP-2025-4e7df6	2	[{"changed": {"fields": ["Rating"]}}]	13	1
171	2025-04-06 10:34:26.815485+08	HR-PERF-2025-5a936e	HR-PERF-2025-5a936e - HR-EMP-2025-4e7df6	3		13	1
172	2025-04-06 10:34:53.918585+08	HR-PERF-2025-7068ff	HR-PERF-2025-7068ff - HR-EMP-2025-721405	2	[]	13	1
173	2025-04-06 10:34:58.256881+08	HR-PERF-2025-bd0602	HR-PERF-2025-bd0602 - HR-EMP-2025-e3eea9	2	[]	13	1
174	2025-04-06 10:35:36.667618+08	HR-PERF-2025-45b30e	HR-PERF-2025-45b30e - HR-EMP-2025-e3eea9	2	[]	13	1
175	2025-04-06 10:40:29.542436+08	HR-PERF-2025-aa467e	HR-PERF-2025-aa467e - HR-EMP-2025-e3eea9	2	[]	13	1
176	2025-04-06 10:41:57.398743+08	HR-PERF-2025-b5fa9e	HR-PERF-2025-b5fa9e - HR-EMP-2025-e3eea9	2	[]	13	1
177	2025-04-06 10:44:18.074939+08	HR-PERF-2025-fb5b38	HR-PERF-2025-fb5b38 - HR-EMP-2025-721405	2	[]	13	1
178	2025-04-06 10:44:22.250719+08	HR-PERF-2025-f222a8	HR-PERF-2025-f222a8 - HR-EMP-2025-1f5dd3	2	[{"changed": {"fields": ["Rating"]}}]	13	1
179	2025-04-06 10:44:27.746448+08	HR-PERF-2025-c9c9d0	HR-PERF-2025-c9c9d0 - HR-EMP-2025-1f5dd3	2	[{"changed": {"fields": ["Rating"]}}]	13	1
180	2025-04-06 10:44:34.434263+08	HR-PERF-2025-2659d4	HR-PERF-2025-2659d4 - HR-EMP-2025-1f5dd3	2	[{"changed": {"fields": ["Rating"]}}]	13	1
181	2025-04-06 10:49:53.486539+08	HR-PERF-2025-b9b11d	HR-PERF-2025-b9b11d - HR-EMP-2025-e3eea9	2	[]	13	1
182	2025-04-06 10:56:11.248819+08	AT0002	HR-EMP-2025-4e7df6 - AT0002	1	[{"added": {}}]	11	1
183	2025-04-06 10:56:47.381244+08	SAL-202504-b4f77f	SAL-202504-b4f77f - HR-EMP-2025-af9c27	2	[{"changed": {"fields": ["Base salary"]}}]	12	1
184	2025-04-06 12:07:27.501766+08	REG-2504-fe50	HRasdfas (Regular)	1	[{"added": {}}]	8	1
185	2025-04-06 13:05:04.0186+08	HR-DEPT-2025-ff3754	Human Resource	2	[{"changed": {"fields": ["Is archived"]}}]	7	1
186	2025-04-07 15:47:50.194778+08	HR-DEPT-2025-fc0aa6	asdasdsadas	3		7	1
187	2025-04-07 15:47:57.462514+08	HR-DEPT-2025-a118dc	Test Departamento	3		7	1
188	2025-04-07 22:21:02.007227+08	HR-DEPT-2025-fc0aa6	Test Departa	2	[{"changed": {"fields": ["Dept name"]}}]	7	1
189	2025-04-08 12:43:58.250469+08	HR-DEPT-2025-45580e	Department of Slavery	1	[{"added": {}}]	7	1
190	2025-04-08 12:46:47.341331+08	HR-DEPT-2025-0ce80e	Department of Slavery	3		7	1
191	2025-04-08 12:46:52.241653+08	HR-DEPT-2025-e08715	Department of Slavery	1	[{"added": {}}]	7	1
192	2025-04-08 12:54:58.717208+08	HR-DEPT-2025-d4de2d	asd	1	[{"added": {}}]	7	1
193	2025-04-08 12:56:39.188351+08	HR-DEPT-2025-d8ee49	AYOO WTF!	1	[{"added": {}}]	7	1
194	2025-04-08 13:59:08.4211+08	HR-DEPT-2025-db810e	Department of Slavery and Peasantry	1	[{"added": {}}]	7	1
195	2025-04-08 13:59:16.99647+08	HR-DEPT-2025-9ba632	Department of Slavery and Peasantry - Edited	2	[{"changed": {"fields": ["Dept name"]}}]	7	1
196	2025-04-08 18:40:23.031248+08	REG-2504-ef4a	Laygo's Slave (Regular)	1	[{"added": {}}]	8	1
197	2025-04-08 18:40:47.939107+08	REG-2504-ef4a	Laygo's Slave - Edited (Regular)	2	[{"changed": {"fields": ["Position title"]}}]	8	1
198	2025-04-09 13:14:53.538226+08	HR-DEPT-2025-ea6444	Department of Slavery and Peasantry	1	[{"added": {}}]	7	1
199	2025-04-09 21:40:32.252306+08	HR-EMP-2025-142BEB	Mansa Musa (HR-EMP-2025-142BEB)	1	[{"added": {}}]	9	1
200	2025-04-09 21:40:34.236768+08	HR-EMP-2025-5E6A2B	Mansa Musa (HR-EMP-2025-5E6A2B)	1	[{"added": {}}]	9	1
201	2025-04-09 21:41:18.074901+08	HR-EMP-2025-77B954	Mansa Musa (HR-EMP-2025-77B954)	1	[{"added": {}}]	9	1
202	2025-04-09 21:42:41.287251+08	HR-EMP-2025-1C978F	Mansa Musa (HR-EMP-2025-1C978F)	1	[{"added": {}}]	9	1
203	2025-04-09 21:43:07.056904+08	HR-EMP-2025-D90B6F	Mansa Musa (HR-EMP-2025-D90B6F)	1	[{"added": {}}]	9	1
204	2025-04-09 21:43:08.382478+08	HR-EMP-2025-F08BF5	Mansa Musa (HR-EMP-2025-F08BF5)	1	[{"added": {}}]	9	1
205	2025-04-09 21:43:13.382829+08	HR-EMP-2025-4CD09D	Mansa Musa (HR-EMP-2025-4CD09D)	1	[{"added": {}}]	9	1
206	2025-04-09 21:45:03.111538+08	HR-EMP-2025-793C95	Mansa Musa (HR-EMP-2025-793C95)	1	[{"added": {}}]	9	1
207	2025-04-09 21:45:22.970316+08	HR-EMP-2025-aa521d	Mansa Musa (HR-EMP-2025-aa521d)	3		9	1
208	2025-04-09 21:45:35.606273+08	HR-EMP-2025-bef0a9	Mansa Musa (HR-EMP-2025-bef0a9)	3		9	1
209	2025-04-09 21:45:42.209163+08	HR-EMP-2025-25c892	Mansa Musa (HR-EMP-2025-25c892)	3		9	1
210	2025-04-09 21:46:20.523942+08	HR-EMP-2025-9ae78d	Mansa Musa (HR-EMP-2025-9ae78d)	3		9	1
211	2025-04-09 21:46:29.249445+08	HR-EMP-2025-5727a1	Mansa Musa (HR-EMP-2025-5727a1)	3		9	1
212	2025-04-09 21:46:34.928881+08	HR-EMP-2025-2429a6	Mansa Musa (HR-EMP-2025-2429a6)	3		9	1
213	2025-04-09 21:46:41.875717+08	HR-EMP-2025-153908	Mansa Musa (HR-EMP-2025-153908)	3		9	1
214	2025-04-09 21:46:47.106656+08	HR-EMP-2025-45fd35	Mansa Musa (HR-EMP-2025-45fd35)	3		9	1
215	2025-04-09 21:46:57.510464+08	HR-EMP-2025-C53055	Mansa Musa (HR-EMP-2025-C53055)	1	[{"added": {}}]	9	1
216	2025-04-09 21:53:19.062896+08	HR-EMP-2025-6138cd	Mansa Musa (HR-EMP-2025-6138cd)	3		9	1
217	2025-04-09 21:55:57.718319+08	HR-EMP-2025-F80017	Mansa Musa (HR-EMP-2025-F80017)	1	[{"added": {}}]	9	1
218	2025-04-09 22:01:52.384306+08	HR-EMP-2025-fc89ed	Mansa Musa (HR-EMP-2025-fc89ed)	3		9	1
220	2025-04-09 22:02:31.299708+08	HR-EMP-2025-96D0AD	Mansa Musa (HR-EMP-2025-96D0AD)	1	[{"added": {}}]	9	1
221	2025-04-09 22:02:41.456738+08	HR-EMP-2025-903dc9	Mansa Musa (HR-EMP-2025-903dc9)	3		9	1
222	2025-04-09 22:03:34.946438+08	HR-EMP-2025-C8EFCB	Mansa Musa (HR-EMP-2025-C8EFCB)	1	[{"added": {}}]	9	1
223	2025-04-09 22:06:30.728825+08	HR-EMP-2025-DBECBD	Mansa Musa (HR-EMP-2025-DBECBD)	1	[{"added": {}}]	9	1
224	2025-04-09 22:07:39.856332+08	HR-EMP-2025-A45600	Mansa Musa (HR-EMP-2025-A45600)	1	[{"added": {}}]	9	1
225	2025-04-09 22:07:51.966138+08	HR-EMP-2025-66f87d	Mansa Musa (HR-EMP-2025-66f87d)	3		9	1
226	2025-04-09 22:07:57.368155+08	HR-EMP-2025-88e6f9	Mansa Musa (HR-EMP-2025-88e6f9)	3		9	1
227	2025-04-09 22:08:03.371252+08	HR-EMP-2025-ce47fa	Mansa Musa (HR-EMP-2025-ce47fa)	3		9	1
228	2025-04-09 22:08:11.642615+08	HR-EMP-2025-E54324	Mansa Musa (HR-EMP-2025-E54324)	1	[{"added": {}}]	9	1
229	2025-04-09 22:10:51.571891+08	HR-EMP-2025-50c41c	Mansa Musa (HR-EMP-2025-50c41c)	3		9	1
230	2025-04-09 22:11:26.471889+08	HR-EMP-2025-1DF075	Mansa Musa (HR-EMP-2025-1DF075)	1	[{"added": {}}]	9	1
231	2025-04-09 22:12:49.200371+08	HR-EMP-2025-b6e103	Mansa Musa (HR-EMP-2025-b6e103)	3		9	1
232	2025-04-09 22:14:06.897444+08	HR-EMP-2025-3DE774	Mansa Musa (HR-EMP-2025-3DE774)	1	[{"added": {}}]	9	1
233	2025-04-09 22:16:58.69127+08	HR-EMP-2025-59cbbb	Mansa Musa (HR-EMP-2025-59cbbb)	2	[]	9	1
234	2025-04-09 22:20:25.301141+08	HR-EMP-2025-B2BF69	Kathlyn Bautista (HR-EMP-2025-B2BF69)	1	[{"added": {}}]	9	1
235	2025-04-09 22:20:53.370543+08	HR-EMP-2025-7b93d4	Kathlyn Bautista (HR-EMP-2025-7b93d4)	3		9	1
236	2025-04-09 22:20:59.528698+08	HR-EMP-2025-59cbbb	Mansa Musa (HR-EMP-2025-59cbbb)	3		9	1
237	2025-04-09 22:23:26.960619+08	HR-EMP-2025-36D16A	Kathlyn Bautista (HR-EMP-2025-36D16A)	1	[{"added": {}}]	9	1
238	2025-04-09 22:23:29.34389+08	HR-EMP-2025-AA5348	Kathlyn Bautista (HR-EMP-2025-AA5348)	1	[{"added": {}}]	9	1
239	2025-04-09 22:23:44.508891+08	HR-EMP-2025-a8e9de	Kathlyn Bautista (HR-EMP-2025-a8e9de)	3		9	1
240	2025-04-09 22:23:55.371261+08	HR-EMP-2025-925128	Kathlyn Bautista (HR-EMP-2025-925128)	3		9	1
241	2025-04-09 22:27:39.780388+08	HR-EMP-2025-16E5E0	Kathlyn Bautista (HR-EMP-2025-16E5E0)	1	[{"added": {}}]	9	1
242	2025-04-09 22:29:38.116007+08	HR-EMP-2025-e8ab7d	Kathlyn Bautista (HR-EMP-2025-e8ab7d)	3		9	1
243	2025-04-09 22:31:46.715557+08	HR-EMP-2025-DA5A98	Kathlyn Bautista (HR-EMP-2025-DA5A98)	1	[{"added": {}}]	9	1
244	2025-04-09 22:35:15.526495+08	HR-EMP-2025-C8AACC	Kathlyn Bautista (HR-EMP-2025-C8AACC)	1	[{"added": {}}]	9	1
245	2025-04-09 22:35:17.090921+08	HR-EMP-2025-DCA72F	Kathlyn Bautista (HR-EMP-2025-DCA72F)	1	[{"added": {}}]	9	1
246	2025-04-09 22:35:25.318906+08	HR-EMP-2025-cf664b	Kathlyn Bautista (HR-EMP-2025-cf664b)	3		9	1
247	2025-04-09 22:35:35.178619+08	HR-EMP-2025-db15c1	Kathlyn Bautista (HR-EMP-2025-db15c1)	3		9	1
248	2025-04-09 22:44:23.024594+08	HR-EMP-2025-d551a3	Kathlyn Bautista (HR-EMP-2025-d551a3)	3		9	1
249	2025-04-09 22:59:48.177121+08	HR-EMP-2025-B8E171	Mansa Musa (HR-EMP-2025-B8E171)	1	[{"added": {}}]	9	1
250	2025-04-09 23:00:07.738234+08	HR-EMP-2025-a39dde	Mansa Musa (HR-EMP-2025-a39dde)	3		9	1
251	2025-04-09 23:01:33.750773+08	HR-EMP-2025-9E1659	Mansa Musa (HR-EMP-2025-9E1659)	1	[{"added": {}}]	9	1
252	2025-04-09 23:03:44.810023+08	HR-EMP-2025-084c28	Mansa Musa (HR-EMP-2025-084c28)	3		9	1
253	2025-04-09 23:06:59.108672+08	HR-EMP-2025-481B58	dsa Musa (HR-EMP-2025-481B58)	1	[{"added": {}}]	9	1
254	2025-04-09 23:07:03.61951+08	HR-EMP-2025-C1C9E2	dsa Musa (HR-EMP-2025-C1C9E2)	1	[{"added": {}}]	9	1
255	2025-04-09 23:07:13.784058+08	HR-EMP-2025-ef0b72	dsa Musa (HR-EMP-2025-ef0b72)	3		9	1
256	2025-04-09 23:07:16.980102+08	HR-EMP-2025-ee94dd	dsa Musa (HR-EMP-2025-ee94dd)	3		9	1
257	2025-04-09 23:10:41.613306+08	HR-EMP-2025-7bd2b6	dsa asd (HR-EMP-2025-7bd2b6)	3		9	1
258	2025-04-09 23:20:26.580506+08	HR-EMP-2025-BEFA5F	f dsa (HR-EMP-2025-BEFA5F)	1	[{"added": {}}]	9	1
259	2025-04-09 23:22:42.13385+08	HR-EMP-2025-EBB867	sad dsa (HR-EMP-2025-EBB867)	1	[{"added": {}}]	9	1
260	2025-04-09 23:24:31.894641+08	HR-EMP-2025-993b0a	f dsa (HR-EMP-2025-993b0a)	3		9	1
261	2025-04-10 03:01:04.075387+08	HR-EMP-2025-E3A1A2	sad sad (HR-EMP-2025-E3A1A2)	1	[{"added": {}}]	9	1
262	2025-04-10 03:01:40.162839+08	HR-EMP-2025-bb7e33	sad sad (HR-EMP-2025-bb7e33)	3		9	1
263	2025-04-10 03:08:08.181401+08	HR-EMP-2025-2C5D8D	gg dsds (HR-EMP-2025-2C5D8D)	1	[{"added": {}}]	9	1
264	2025-04-10 03:08:09.374954+08	HR-EMP-2025-97C869	gg dsds (HR-EMP-2025-97C869)	1	[{"added": {}}]	9	1
266	2025-04-10 03:11:42.29203+08	HR-EMP-2025-D5257C	gg dsds (HR-EMP-2025-D5257C)	1	[{"added": {}}]	9	1
267	2025-04-10 03:13:48.691105+08	HR-EMP-2025-7143B6	gg dsds (HR-EMP-2025-7143B6)	1	[{"added": {}}]	9	1
268	2025-04-10 03:14:21.133149+08	HR-EMP-2025-30f3d7	sad dsa (HR-EMP-2025-30f3d7)	3		9	1
269	2025-04-10 03:14:25.312062+08	HR-EMP-2025-fb2983	gg dsds (HR-EMP-2025-fb2983)	3		9	1
270	2025-04-10 03:37:00.30121+08	HR-EMP-2025-827067	sdada dsdsaaa (HR-EMP-2025-827067)	1	[{"added": {}}]	9	1
271	2025-04-10 05:28:16.602844+08	HR-EMP-2025-8C6388	FDS dsdsaaa (HR-EMP-2025-8C6388)	1	[{"added": {}}]	9	1
272	2025-04-10 05:35:46.049935+08	HR-EMP-2025-A3667E	srew1 dsdsaaa (HR-EMP-2025-A3667E)	1	[{"added": {}}]	9	1
273	2025-04-10 05:46:03.822614+08	HR-EMP-2025-17ABE4	dz dsdsaaa (HR-EMP-2025-17ABE4)	1	[{"added": {}}]	9	1
274	2025-04-10 10:52:24.998917+08	HR-EMP-2025-536758	dasdasdas dsdsaaavc (HR-EMP-2025-536758)	1	[{"added": {}}]	9	1
275	2025-04-10 10:52:49.863924+08	HR-EMP-2025-0f6911	dasdasdas dsdsaaavc (HR-EMP-2025-0f6911)	3		9	1
276	2025-04-10 10:53:46.942219+08	HR-EMP-2025-B5665E	asd sda (HR-EMP-2025-B5665E)	1	[{"added": {}}]	9	1
277	2025-04-10 10:55:43.259321+08	HR-EMP-2025-E0CB7D	sadsa sdadd (HR-EMP-2025-E0CB7D)	1	[{"added": {}}]	9	1
278	2025-04-10 10:56:43.971111+08	HR-EMP-2025-BAC653	dsa dsa (HR-EMP-2025-BAC653)	1	[{"added": {}}]	9	1
279	2025-04-10 11:14:02.223701+08	HR-EMP-2025-9383BC	ewr dsa (HR-EMP-2025-9383BC)	1	[{"added": {}}]	9	1
280	2025-04-10 11:14:25.77779+08	HR-EMP-2025-9a6cad	gg dsds (HR-EMP-2025-9a6cad)	3		9	1
281	2025-04-10 11:14:29.314363+08	HR-EMP-2025-ca226a	sdada dsdsaaa (HR-EMP-2025-ca226a)	3		9	1
282	2025-04-10 11:14:33.442515+08	HR-EMP-2025-d894ae	srew1 dsdsaaa (HR-EMP-2025-d894ae)	3		9	1
283	2025-04-10 11:14:36.754067+08	HR-EMP-2025-958c56	gg dsds (HR-EMP-2025-958c56)	3		9	1
284	2025-04-10 11:14:41.292799+08	HR-EMP-2025-5b33d5	ewr dsa (HR-EMP-2025-5b33d5)	3		9	1
285	2025-04-10 11:14:45.550981+08	HR-EMP-2025-695ed7	sadsa sdadd (HR-EMP-2025-695ed7)	3		9	1
286	2025-04-10 11:14:51.030559+08	HR-EMP-2025-1b493c	asd sda (HR-EMP-2025-1b493c)	3		9	1
287	2025-04-10 11:14:54.84107+08	HR-EMP-2025-77d49e	gg dsds (HR-EMP-2025-77d49e)	3		9	1
288	2025-04-10 11:14:58.42636+08	HR-EMP-2025-3c667a	dz dsdsaaa (HR-EMP-2025-3c667a)	3		9	1
289	2025-04-10 11:15:03.652412+08	HR-EMP-2025-1c6781	dsa dsa (HR-EMP-2025-1c6781)	3		9	1
290	2025-04-10 11:18:03.47266+08	HR-EMP-2025-091734	sad dsa (HR-EMP-2025-091734)	1	[{"added": {}}]	9	1
291	2025-04-10 11:33:08.289914+08	HR-EMP-2025-2635b3	FDS dsdsaaa (HR-EMP-2025-2635b3)	3		9	1
292	2025-04-10 11:56:55.943807+08	HR-EMP-2025-3600f1	sad dsa (HR-EMP-2025-3600f1)	3		9	1
293	2025-04-10 12:09:16.948307+08	perf	perf - HR-EMP-2025-5d79fb - John Doe (HR-EMP-2025-5d79fb)	1	[{"added": {}}]	19	1
294	2025-04-10 12:09:40.096646+08	HR-PERF-2025-768d11	HR-PERF-2025-768d11 - HR-EMP-2025-5d79fb - John Doe (HR-EMP-2025-5d79fb)	3		19	1
295	2025-04-10 12:37:56.374409+08	HR-EMP-2025-1AE967	sad dsa (HR-EMP-2025-1AE967)	1	[{"added": {}}]	9	1
296	2025-04-10 12:39:25.194434+08	HR-EMP-2025-ED8AEE	dsa dsa (HR-EMP-2025-ED8AEE)	1	[{"added": {}}]	9	1
297	2025-04-10 12:58:01.341757+08	HR-EMP-2025-075DCF	d dsa (HR-EMP-2025-075DCF)	1	[{"added": {}}]	9	1
298	2025-04-10 12:58:17.748653+08	HR-EMP-2025-b92a33	dsa dsa (HR-EMP-2025-b92a33)	3		9	1
299	2025-04-10 12:58:21.670431+08	HR-EMP-2025-969d9b	sad dsa (HR-EMP-2025-969d9b)	3		9	1
300	2025-04-10 12:58:25.56129+08	HR-EMP-2025-274b74	d dsa (HR-EMP-2025-274b74)	3		9	1
301	2025-04-10 13:00:05.196899+08	HR-EMP-2025-BA6915	WA dsa (HR-EMP-2025-BA6915)	1	[{"added": {}}]	9	1
302	2025-04-10 13:00:46.310279+08	HR-EMP-2025-36c436	WA dsa (HR-EMP-2025-36c436)	3		9	1
308	2025-04-10 13:06:36.515079+08	HR-EMP-2025-43de6c	Test User (HR-EMP-2025-43de6c)	3		9	1
309	2025-04-10 13:06:42.131187+08	HR-EMP-2025-03017f	Test User (HR-EMP-2025-03017f)	3		9	1
310	2025-04-10 13:26:48.948728+08	HR-DEPT-2025-06d0ed	Department of Slavery and Peasantry	2	[]	7	1
311	2025-04-10 13:27:01.544765+08	HR-DEPT-2025-06d0ed	Department of Slavery and Peons	2	[{"changed": {"fields": ["Dept name"]}}]	7	1
312	2025-04-10 13:35:08.601954+08	HR-DEPT-2025-06d0ed	Department of F	2	[{"changed": {"fields": ["Dept name", "Created by", "Updated by"]}}]	7	1
313	2025-04-10 13:36:54.036301+08	HR-DEPT-2025-06d0ed	Department of F	2	[]	7	1
314	2025-04-10 13:40:28.46456+08	HR-DEPT-2025-06d0ed	Department of Fe	2	[{"changed": {"fields": ["Dept name"]}}]	7	1
315	2025-04-10 14:07:25.438039+08	HR-DEPT-2025-06d0ed	Mo	2	[{"changed": {"fields": ["Dept name"]}}]	7	1
316	2025-04-10 14:13:33.86057+08	HR-DEPT-2025-06d0ed	Mor	2	[{"changed": {"fields": ["Dept name"]}}]	7	1
317	2025-04-10 14:20:12.747096+08	HR-DEPT-2025-06d0ed	More	2	[{"changed": {"fields": ["Dept name"]}}]	7	1
318	2025-04-10 14:22:28.515226+08	HR-DEPT-2025-06d0ed	Moree	2	[{"changed": {"fields": ["Dept name"]}}]	7	1
319	2025-04-10 14:26:53.386588+08	HR-DEPT-2025-06d0ed	Moreee	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
320	2025-04-10 14:28:24.403689+08	HR-DEPT-2025-06d0ed	Moreees	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
321	2025-04-10 14:30:25.047403+08	HR-DEPT-2025-06d0ed	Moreeeswqe	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
322	2025-04-10 14:36:55.213639+08	HR-DEPT-2025-06d0ed	Moreeeswqed	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
323	2025-04-10 14:37:17.256351+08	HR-DEPT-2025-06d0ed	Moreeeswqedd	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
324	2025-04-10 14:50:16.172244+08	HR-DEPT-2025-06d0ed	Moreeeswqedddsad	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
325	2025-04-10 14:50:24.565625+08	HR-DEPT-2025-06d0ed	Moreeeswqedddsadd	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
326	2025-04-10 14:50:52.900651+08	HR-DEPT-2025-06d0ed	Moreeeswqedddsadddd	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
327	2025-04-10 14:52:01.979053+08	HR-DEPT-2025-06d0ed	He	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
328	2025-04-10 14:57:00.691759+08	HR-DEPT-2025-06d0ed	He	3		7	1
329	2025-04-10 14:57:06.320332+08	HR-DEPT-2025-ad8573	Hahaha	3		7	1
330	2025-04-10 15:10:51.805245+08	HR-DEPT-2025-4a0c25	Department of SlaveryS	1	[{"added": {}}]	7	1
331	2025-04-10 15:19:58.871786+08	HR-DEPT-2025-e330d7	Department of Slaveryr	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
332	2025-04-10 15:24:35.936382+08	HR-DEPT-2025-ab0b4a	AYOO WTF! ds	1	[{"added": {}}]	7	1
333	2025-04-10 15:26:29.017616+08	HR-DEPT-2025-773e05	haha	1	[{"added": {}}]	7	1
334	2025-04-10 15:28:34.038144+08	HR-DEPT-2025-0f5a95	c	1	[{"added": {}}]	7	1
335	2025-04-10 15:30:45.231813+08	HR-DEPT-2025-f2dcaf	Test Departamento	1	[{"added": {}}]	7	1
336	2025-04-10 15:31:03.206077+08	HR-DEPT-2025-542c22	hahar	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
337	2025-04-10 15:34:16.435975+08	HR-DEPT-2025-e330d7	Department of Slaveryre	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
338	2025-04-10 15:39:22.959466+08	HR-DEPT-2025-7b8e92	AYOO WTF! dssd	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
339	2025-04-10 15:44:51.647683+08	HR-DEPT-2025-7b8e92	AYOO WTF! dssdDD	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
340	2025-04-10 15:45:55.413892+08	HR-DEPT-2025-7b8e92	AYOO WTF! dssdDDsdada	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
341	2025-04-10 15:50:11.477649+08	HR-DEPT-2025-542c22	d	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
342	2025-04-10 15:53:08.599518+08	HR-DEPT-2025-542c22	ddsds	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
343	2025-04-10 15:55:08.331938+08	HR-DEPT-2025-7b8e92	Hehehe	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
344	2025-04-10 15:56:00.325314+08	HR-DEPT-2025-e330d7	Department of Slaveryresadsa	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
345	2025-04-10 16:00:24.026277+08	HR-DEPT-2025-711b2e	f	1	[{"added": {}}]	7	1
346	2025-04-10 16:01:08.722523+08	HR-DEPT-2025-87ad87	Test Departamentor	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
347	2025-04-10 16:02:07.709063+08	HR-DEPT-2025-30df39	d	1	[{"added": {}}]	7	1
348	2025-04-10 16:02:15.688097+08	HR-DEPT-2025-98bec8	der	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
349	2025-04-10 16:02:23.681462+08	HR-DEPT-2025-98bec8	derr	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
350	2025-04-10 16:02:58.542177+08	HR-DEPT-2025-98bec8	Hello	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
351	2025-04-10 16:04:13.534081+08	HR-DEPT-2025-e330d7	Department of Slaveryresadsa	3		7	1
352	2025-04-10 16:04:21.480392+08	HR-DEPT-2025-542c22	ddsds	3		7	1
353	2025-04-10 16:04:24.08563+08	HR-DEPT-2025-4bf695	f	3		7	1
354	2025-04-10 16:04:26.805053+08	HR-DEPT-2025-7b8e92	Hehehe	3		7	1
355	2025-04-10 16:04:30.399134+08	HR-DEPT-2025-98bec8	Hello	3		7	1
356	2025-04-10 16:07:20.352688+08	HR-DEPT-2025-288e84	c	3		7	1
357	2025-04-10 16:07:25.35839+08	HR-DEPT-2025-87ad87	Test Departamentor	3		7	1
358	2025-04-10 16:08:37.242803+08	HR-DEPT-2025-362ae3	Department of Slavery and Peasantry	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
359	2025-04-10 16:10:21.568452+08	HR-DEPT-2025-362ae3	Department of Slavery	2	[{"changed": {"fields": ["Dept name", "Change reason"]}}]	7	1
375	2025-04-10 18:06:39.428974+08		asda dsa ()	1	[{"added": {}}]	9	1
376	2025-04-10 18:06:57.681436+08	HR-EMP-2025-bf0844	asda dsa (HR-EMP-2025-bf0844)	3		9	1
377	2025-04-10 18:07:24.566828+08		Leave me when you foudn me sadaddont kleeeaohhhhhhhhhh i just llve way got ()	1	[{"added": {}}]	9	1
378	2025-04-10 18:11:31.540662+08		HAHA HAHAHA ()	1	[{"added": {}}]	9	1
390	2025-04-10 19:35:42.483364+08	HR-EMP-2025-7177FE	dsada dsada (HR-EMP-2025-7177FE)	1	[{"added": {}}]	9	1
391	2025-04-10 19:35:55.927713+08	HR-EMP-2025-119984	Leave me when you foudn me sadaddont kleeeaohhhhhhhhhh i just llve way got (HR-EMP-2025-119984)	3		9	1
392	2025-04-10 19:36:01.191588+08	HR-EMP-2025-0b9318	Leave me when you foudn me sadaddont kleeeaohhhhhhhhhh i just llve way got (HR-EMP-2025-0b9318)	3		9	1
393	2025-04-10 19:36:12.288732+08	HR-EMP-2025-521605	asda dsa (HR-EMP-2025-521605)	3		9	1
394	2025-04-10 19:36:15.488878+08	HR-EMP-2025-eefb18	HAHA HAHAHA (HR-EMP-2025-eefb18)	3		9	1
395	2025-04-10 19:36:19.073014+08	HR-EMP-2025-d3f6f0	HAHA HAHAHA (HR-EMP-2025-d3f6f0)	3		9	1
396	2025-04-10 19:36:25.097892+08	HR-EMP-2025-7005e9	dsada dsada (HR-EMP-2025-7005e9)	3		9	1
417	2025-04-10 20:40:42.779632+08	HR-EMP-2025-375A57	sadas dsada (HR-EMP-2025-375A57)	1	[{"added": {}}]	9	1
418	2025-04-10 20:41:33.397607+08	HR-EMP-2025-179bd5	sadas dsada (HR-EMP-2025-179bd5)	3		9	1
447	2025-04-10 21:30:53.327703+08	perf	perf - HR-EMP-2025-3b7600 - Melissa Garcia (HR-EMP-2025-3b7600)	1	[{"added": {}}]	19	1
448	2025-04-10 21:31:08.001594+08	HR-PERF-2025-58af43	HR-PERF-2025-58af43 - HR-EMP-2025-3b7600 - Melissa Garcia (HR-EMP-2025-3b7600)	3		19	1
449	2025-04-10 21:32:59.666388+08	asa	asa - HR-EMP-2025-3b7600 - Melissa Garcia (HR-EMP-2025-3b7600)	1	[{"added": {}}]	19	1
463	2025-04-10 21:42:40.469492+08	perf	perf - HR-EMP-2025-256de7 - Mark Johnson (HR-EMP-2025-256de7)	1	[{"added": {}}]	19	1
464	2025-04-10 21:42:50.627663+08	HR-PERF-2025-607018	HR-PERF-2025-607018 - HR-EMP-2025-3b7600 - Melissa Garcia (HR-EMP-2025-3b7600)	3		19	1
465	2025-04-10 21:44:35.574237+08	HR-PERF-2025-4b5a92	HR-PERF-2025-4b5a92 - HR-EMP-2025-256de7 - Mark Johnson (HR-EMP-2025-256de7)	3		19	1
467	2025-04-10 21:50:58.480427+08	perf	perf - HR-EMP-2025-3b7600 - Melissa Garcia (HR-EMP-2025-3b7600)	1	[{"added": {}}]	19	1
468	2025-04-10 21:51:12.491406+08	HR-PERF-2025-3d6fbb	HR-PERF-2025-3d6fbb - HR-EMP-2025-3b7600 - Melissa Garcia (HR-EMP-2025-3b7600)	3		19	1
475	2025-04-10 23:07:05.696468+08	perf	perf - HR-EMP-2025-3b7600 - Melissa Garcia (HR-EMP-2025-3b7600)	1	[{"added": {}}]	19	1
476	2025-04-10 23:13:29.327403+08	SAL	SAL - HR-EMP-2025-f36f96	1	[{"added": {}}]	23	1
477	2025-04-10 23:13:46.027483+08	SAL-202504-23c020	SAL-202504-23c020 - HR-EMP-2025-f36f96	3		23	1
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	auth	user
5	contenttypes	contenttype
6	sessions	session
7	departments	department
8	positions	position
9	employees	employee
10	department_superiors	departmentsuperior
11	attendance_tracking	attendance
12	employee_salary	employeesalary
13	employee_performance	employeeperformance
14	workforce_allocation	workforceallocation
15	department_superiors	department
16	department_superiors	position
17	department_superiors	employee
18	attendance_tracking	attendance_tracking
19	employee_performance	employee_performance
20	workforce_allocation	workforce_allocation
21	calendar_dates	calendar_date
22	department_superiors	department_superior
23	employee_salary	employee_salary
24	departments	historicaldepartment
25	department_superiors	historicaldepartment_superior
26	positions	historicalposition
27	employees	historicalemployee
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2025-04-04 08:02:44.818879+08
2	auth	0001_initial	2025-04-04 08:02:44.863051+08
3	admin	0001_initial	2025-04-04 08:02:44.874019+08
4	admin	0002_logentry_remove_auto_add	2025-04-04 08:02:44.882642+08
5	admin	0003_logentry_add_action_flag_choices	2025-04-04 08:02:44.886906+08
6	contenttypes	0002_remove_content_type_name	2025-04-04 08:02:44.896929+08
7	auth	0002_alter_permission_name_max_length	2025-04-04 08:02:44.902072+08
8	auth	0003_alter_user_email_max_length	2025-04-04 08:02:44.906069+08
9	auth	0004_alter_user_username_opts	2025-04-04 08:02:44.910424+08
10	auth	0005_alter_user_last_login_null	2025-04-04 08:02:44.915218+08
11	auth	0006_require_contenttypes_0002	2025-04-04 08:02:44.916061+08
12	auth	0007_alter_validators_add_error_messages	2025-04-04 08:02:44.919941+08
13	auth	0008_alter_user_username_max_length	2025-04-04 08:02:44.926904+08
14	auth	0009_alter_user_last_name_max_length	2025-04-04 08:02:44.931511+08
15	auth	0010_alter_group_name_max_length	2025-04-04 08:02:44.936596+08
16	auth	0011_update_proxy_permissions	2025-04-04 08:02:44.940591+08
17	auth	0012_alter_user_first_name_max_length	2025-04-04 08:02:44.944985+08
18	departments	0001_initial	2025-04-04 08:02:44.949862+08
19	sessions	0001_initial	2025-04-04 08:02:44.956442+08
20	positions	0001_initial	2025-04-04 08:19:35.02542+08
21	employees	0001_initial	2025-04-04 08:55:38.888072+08
22	department_superiors	0001_initial	2025-04-04 08:58:28.82547+08
23	attendance_tracking	0001_initial	2025-04-04 09:47:40.52836+08
24	employee_performance	0001_initial	2025-04-04 11:37:39.724043+08
25	employee_salary	0001_initial	2025-04-04 14:37:01.896102+08
26	workforce_allocation	0001_initial	2025-04-04 14:37:01.905718+08
27	positions	0002_alter_position_typical_duration_days	2025-04-06 00:06:33.32613+08
28	departments	0002_department_is_archived	2025-04-06 13:01:41.281632+08
29	positions	0003_alter_position_typical_duration_days	2025-04-06 15:00:56.784035+08
30	department_superiors	0002_initial	2025-04-06 15:14:35.547663+08
31	positions	0002_add_employee_id	2025-04-07 14:19:17.460148+08
32	attendance_tracking	0002_alter_attendance_tracking_options	2025-04-09 14:51:58.310677+08
33	calendar_dates	0001_initial	2025-04-09 19:57:57.037135+08
34	departments	0002_department_created_by_department_updated_by	2025-04-10 13:34:30.308848+08
35	departments	0002_historicaldepartment	2025-04-10 14:13:29.084833+08
36	departments	0003_department_change_reason_and_more	2025-04-10 14:26:38.145837+08
37	department_superiors	0002_department_superior_change_reason_and_more	2025-04-10 16:30:45.06014+08
38	positions	0002_position_change_reason_historicalposition	2025-04-10 16:58:29.822496+08
39	employees	0002_employee_change_reason_historicalemployee	2025-04-10 17:32:03.236304+08
40	employee_salary	0002_employee_salary_contract_end_date_and_more	2025-04-10 22:27:42.958824+08
41	calendar_dates	0002_calendar_date_holiday_type	2025-04-11 14:09:14.043615+08
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.django_session (session_key, session_data, expire_date) FROM stdin;
248dnk7c5wxkeogp4o0gdrr4szudaz9e	.eJxVjDsOwjAQBe_iGln-R6ak5wzWrneNA8iW4qRC3B0ipYD2zcx7iQTbWtM2eEkzibPQ4vS7IeQHtx3QHdqty9zbuswod0UedMhrJ35eDvfvoMKo3xpUDJM1oD0V4z1apAKFopu8QjAxo_LFaochGkZmBzGbGJBRU7FYxPsD8e045g:1u0Ubr:uhC2g8pEeRq1CnYT125jrIV8wFXdxdNC_8w5pGZcUWI	2025-04-18 08:08:35.945712+08
\.


--
-- Data for Name: employee_leave_balances; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.employee_leave_balances (balance_id, employee_id, year, sick_leave_remaining, vacation_leave_remaining, maternity_leave_remaining, paternity_leave_remaining, solo_parent_leave_remaining, unpaid_leave_taken) FROM stdin;
\.


--
-- Data for Name: employee_performance; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.employee_performance (performance_id, employee_id, immediate_superior_id, rating, bonus_amount, bonus_payment_month, review_date, updated_at, is_archived) FROM stdin;
HR-PERF-2025-6fdeb7	HR-EMP-2025-bb6f41	\N	4	\N	12	2023-11-01	2025-04-08 20:31:22.835042	f
HR-PERF-2025-c12216	HR-EMP-2025-000a28	\N	5	\N	12	2023-11-02	2025-04-08 20:32:15.171836	f
HR-PERF-2025-536a06	HR-EMP-2025-eae9ae	\N	3	\N	12	2023-11-03	2025-04-08 20:32:15.171836	f
HR-PERF-2025-7dd8c9	HR-EMP-2025-e4973e	\N	4	\N	12	2023-11-05	2025-04-08 20:32:15.171836	f
HR-PERF-2025-97fac0	HR-EMP-2025-a86f5e	\N	2	\N	12	2023-11-06	2025-04-08 20:32:15.171836	f
HR-PERF-2025-f2ab30	HR-EMP-2025-6bcb48	\N	4	\N	12	2023-11-07	2025-04-08 20:32:15.171836	f
HR-PERF-2025-10ca63	HR-EMP-2025-9c43f8	\N	3	\N	12	2023-11-08	2025-04-08 20:32:15.171836	f
HR-PERF-2025-f11d71	HR-EMP-2025-daef61	\N	5	\N	12	2023-11-09	2025-04-08 20:32:15.171836	f
HR-PERF-2025-9b4380	HR-EMP-2025-88221b	HR-EMP-2025-bb6f41	4	\N	12	2023-11-10	2025-04-08 20:32:15.171836	f
HR-PERF-2025-0e9b13	HR-EMP-2025-09a3af	HR-EMP-2025-88221b	3	\N	12	2023-11-11	2025-04-08 20:32:15.171836	f
HR-PERF-2025-ec3fbc	HR-EMP-2025-55fefe	HR-EMP-2025-bb6f41	4	\N	3	2023-08-15	2025-04-08 20:32:15.171836	f
HR-PERF-2025-b25dfe	HR-EMP-2025-4e30cc	HR-EMP-2025-e4973e	3	\N	6	2023-05-15	2025-04-08 20:32:15.171836	f
HR-PERF-2025-0018fe	HR-EMP-2025-5b3ddf	HR-EMP-2025-6bcb48	5	\N	9	2023-08-15	2025-04-08 20:32:15.171836	f
HR-PERF-2025-3a24a6	HR-EMP-2025-83e9c8	HR-EMP-2025-000a28	2	\N	12	2023-11-15	2025-04-08 20:32:15.171836	f
HR-PERF-2025-f3d8aa	HR-EMP-2025-ae73bb	HR-EMP-2025-000a28	3	\N	12	2023-11-16	2025-04-08 20:32:15.171836	f
HR-PERF-2025-8d2e2f	HR-EMP-2025-eb5761	HR-EMP-2025-a86f5e	4	\N	12	2023-11-17	2025-04-08 20:32:15.171836	f
HR-PERF-2025-319710	HR-EMP-2025-550d02	HR-EMP-2025-a86f5e	3	\N	12	2023-11-18	2025-04-08 20:32:15.171836	f
HR-PERF-2025-a58921	HR-EMP-2025-5b3435	HR-EMP-2025-a86f5e	5	\N	12	2023-11-19	2025-04-08 20:32:15.171836	f
HR-PERF-2025-2ef1b1	HR-EMP-2025-01dd64	HR-EMP-2025-000a28	2	\N	12	2023-11-20	2025-04-08 20:32:15.171836	f
HR-PERF-2025-fbd925	HR-EMP-2025-e134d7	HR-EMP-2025-daef61	4	\N	12	2023-11-21	2025-04-08 20:32:15.171836	f
HR-PERF-2025-a00435	HR-EMP-2025-01a7a1	HR-EMP-2025-bb6f41	3	\N	1	2024-01-05	2025-04-08 20:32:15.171836	f
HR-PERF-2025-3334b4	HR-EMP-2025-f2b0c8	HR-EMP-2025-000a28	4	\N	7	2023-07-10	2025-04-08 20:32:15.171836	f
HR-PERF-2025-111b89	HR-EMP-2025-29e5aa	HR-EMP-2025-e4973e	5	\N	4	2023-04-20	2025-04-08 20:32:15.171836	f
HR-PERF-2025-646e11	HR-EMP-2025-d53b94	HR-EMP-2025-9c43f8	3	\N	1	2024-01-15	2025-04-08 20:32:15.171836	f
HR-PERF-2025-bced09	HR-EMP-2025-102b28	HR-EMP-2025-a86f5e	2	\N	1	2024-01-10	2025-04-08 20:32:15.171836	f
HR-PERF-2025-cfe0f4	HR-EMP-2025-36b72f	HR-EMP-2025-eae9ae	4	\N	7	2023-07-15	2025-04-08 20:32:15.171836	f
HR-PERF-2025-fc9cc7	HR-EMP-2025-30fa23	\N	3	\N	1	2024-01-05	2025-04-08 20:32:15.171836	f
HR-PERF-2025-04d985	HR-EMP-2025-0db8ff	HR-EMP-2025-a86f5e	5	\N	1	2024-01-08	2025-04-08 20:32:15.171836	f
HR-PERF-2025-a63268	HR-EMP-2025-f3469c	HR-EMP-2025-a86f5e	4	\N	1	2024-01-09	2025-04-08 20:32:15.171836	f
HR-PERF-2025-0072e6	HR-EMP-2025-fa97ff	HR-EMP-2025-a86f5e	3	\N	1	2024-01-10	2025-04-08 20:32:15.171836	f
HR-PERF-2025-70a86d	HR-EMP-2025-3b7600	HR-EMP-2025-bb6f41	1	0.00	1	2025-04-10	2025-04-10 15:07:05.662595	f
\.


--
-- Data for Name: employee_salary; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.employee_salary (salary_id, employee_id, base_salary, daily_rate, effective_date, updated_at, contract_end_date, contract_start_date) FROM stdin;
SAL-2023-HR-EMP-2025-bb6f41	HR-EMP-2025-bb6f41	65000.00	\N	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-e4973e	HR-EMP-2025-e4973e	38000.00	\N	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-6bcb48	HR-EMP-2025-6bcb48	25000.00	\N	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-000a28	HR-EMP-2025-000a28	55000.00	\N	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-eae9ae	HR-EMP-2025-eae9ae	95000.00	\N	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-a86f5e	HR-EMP-2025-a86f5e	32000.00	\N	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-3b7600	HR-EMP-2025-3b7600	33000.00	\N	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-9c43f8	HR-EMP-2025-9c43f8	70000.00	\N	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-daef61	HR-EMP-2025-daef61	48000.00	\N	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-256de7	HR-EMP-2025-256de7	23000.00	\N	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-09a3af	HR-EMP-2025-09a3af	\N	1800.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-88221b	HR-EMP-2025-88221b	\N	1350.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-55fefe	HR-EMP-2025-55fefe	\N	2750.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-83e9c8	HR-EMP-2025-83e9c8	\N	1450.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-4e30cc	HR-EMP-2025-4e30cc	\N	1100.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-36b72f	HR-EMP-2025-36b72f	\N	1000.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-ae73bb	HR-EMP-2025-ae73bb	\N	600.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-2bd2fd	HR-EMP-2025-2bd2fd	\N	1250.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-01a7a1	HR-EMP-2025-01a7a1	\N	600.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-5b3ddf	HR-EMP-2025-5b3ddf	\N	1250.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-5b3435	HR-EMP-2025-5b3435	\N	1000.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-e134d7	HR-EMP-2025-e134d7	\N	700.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-c8bba3	HR-EMP-2025-c8bba3	\N	1650.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-acbe1e	HR-EMP-2025-acbe1e	\N	1000.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-550d02	HR-EMP-2025-550d02	\N	850.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-eb5761	HR-EMP-2025-eb5761	\N	625.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-f3469c	HR-EMP-2025-f3469c	\N	625.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-0b9b73	HR-EMP-2025-0b9b73	\N	625.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-9e750f	HR-EMP-2025-9e750f	\N	700.00	2023-01-01	\N	\N	\N
SAL-2023-HR-EMP-2025-6a01ba	HR-EMP-2025-6a01ba	\N	700.00	2023-01-01	\N	\N	\N
\.


--
-- Data for Name: employees; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.employees (employee_id, user_id, dept_id, position_id, first_name, last_name, phone, employment_type, status, reports_to, is_supervisor, created_at, updated_at, is_archived, change_reason) FROM stdin;
HR-EMP-2025-bb6f41	\N	HR-DEPT-2025-26b8a4	REG-2504-9b2a	Kate	Tan	09165824756	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-e4973e	\N	HR-DEPT-2025-0272fb	REG-2504-4e93	Camille	Rivera	09341234567	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-6bcb48	\N	HR-DEPT-2025-345995	REG-2504-cce8	Francis	Lim	09678901236	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-000a28	\N	HR-DEPT-2025-2e0d12	REG-2504-3a8e	Karen	Mendoza	09139485762	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-eae9ae	\N	HR-DEPT-2025-de1518	REG-2504-eb03	Juan	Dela Cruz	09123456789	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-a86f5e	\N	HR-DEPT-2025-cca1d0	REG-2504-a218	Aaron	Dela Cruz	09171234561	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-3b7600	\N	HR-DEPT-2025-f57fbb	REG-2504-d2b8	Melissa	Garcia	09185649362	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-9c43f8	\N	HR-DEPT-2025-318899	REG-2504-f87e	Steven	Lee	09223456789	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-daef61	\N	HR-DEPT-2025-7a2d06	REG-2504-6363	Natalie	Vega	09181234568	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-256de7	\N	HR-DEPT-2025-bcff30	REG-2504-fb38	Mark	Johnson	09387654321	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-09a3af	\N	HR-DEPT-2025-7e9a3b	REG-2504-8d4e	Sophia	Lopez	09163458762	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-88221b	\N	HR-DEPT-2025-7e9a3b	REG-2504-0bef	John	Martinez	09261234567	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-55fefe	\N	HR-DEPT-2025-318899	REG-2504-8ab5	Lucia	Wang	09123456788	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-83e9c8	\N	HR-DEPT-2025-7a2d06	REG-2504-a0dd	Olivia	Chavez	09123456780	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-4e30cc	\N	HR-DEPT-2025-f57fbb	REG-2504-a794	Jack	Nguyen	09223456780	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-36b72f	\N	HR-DEPT-2025-7a2d06	REG-2504-131f	Emily	Shen	09123456779	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-ae73bb	\N	HR-DEPT-2025-7e9a3b	REG-2504-5eef	Dan	Liu	09345678901	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-2bd2fd	\N	HR-DEPT-2025-318899	REG-2504-d999	Sophia	Tan	09133456790	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-01a7a1	\N	HR-DEPT-2025-bcff30	REG-2504-fb50	David	Lopez	09177893327	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-5b3ddf	\N	HR-DEPT-2025-bcff30	REG-2504-8731	Chloe	Yang	09223456780	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-f36f96	\N	HR-DEPT-2025-bcff30	CTR-2504-99c0	Peter	Li	09123456781	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-d03af7	\N	HR-DEPT-2025-7a2d06	CTR-2504-769b	Victoria	Zhang	09345678902	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-102b28	\N	HR-DEPT-2025-318899	CTR-2504-70d0	Grace	Wang	09123456782	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-d53b94	\N	HR-DEPT-2025-318899	CTR-2504-6589	Mason	Li	09234567893	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-0b9b73	\N	HR-DEPT-2025-f57fbb	CTR-2504-1f9e	Benjamin	Li	09123456789	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-9e750f	\N	HR-DEPT-2025-318899	CTR-2504-ccc6	Gabriel	Zhang	09341234560	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-c5e1a7	\N	HR-DEPT-2025-318899	CTR-2504-bd5d	Samantha	Chen	09123456790	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-f2b0c8	\N	HR-DEPT-2025-bcff30	CTR-2504-152f	Charlie	Yang	09234567891	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-5b3435	\N	HR-DEPT-2025-bcff30	CTR-2504-f05b	Catherine	Wu	09356789012	Regular	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-e134d7	\N	HR-DEPT-2025-7a2d06	CTR-2504-dced	Alice	Smith	09237894567	Contractual	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-29e5aa	\N	HR-DEPT-2025-318899	CTR-2504-594e	Sam	Lee	09197835612	Contractual	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-c8bba3	\N	HR-DEPT-2025-318899	CTR-2504-177a	Tom	Brown	09237894561	Contractual	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-acbe1e	\N	HR-DEPT-2025-318899	CTR-2504-60d2	Jenny	Garcia	09198765432	Contractual	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-550d02	\N	HR-DEPT-2025-bcff30	CTR-2504-df3d	Emma	Wang	09123456783	Contractual	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-eb5761	\N	HR-DEPT-2025-bcff30	CTR-2504-2094	Sophia	Davis	09341234560	Contractual	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-f3469c	\N	HR-DEPT-2025-bcff30	SEA-2504-ccdc	Andrew	Taylor	09123456785	Contractual	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-0db8ff	\N	HR-DEPT-2025-bcff30	SEA-2504-8866	James	Lee	09234567894	Contractual	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-01dd64	\N	HR-DEPT-2025-bcff30	SEA-2504-d576	Olivia	Chen	09123456786	Contractual	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-6a01ba	\N	HR-DEPT-2025-bcff30	SEA-2504-4fef	John	Smith	09341234562	Contractual	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-30fa23	\N	HR-DEPT-2025-bcff30	SEA-2504-e256	Michael	Moore	09123456784	Contractual	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-7cd0bf	\N	HR-DEPT-2025-bcff30	SEA-2504-c690	Jessica	Miller	09123456788	Seasonal	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-07 18:15:34.305617	f	\N
HR-EMP-2025-fa97ff	\N	HR-DEPT-2025-bcff30	SEA-2504-4c4e	Linda	Thomas	09234567892	Seasonal	Active	\N	f	2025-04-07 18:15:34.305617	2025-04-08 10:52:10.943957	f	\N
HR-EMP-2025-5d79fb	\N	\N	\N	John	Doe	9876543210	Regular	Active	\N	f	2025-04-10 03:59:53.795306	2025-04-10 03:59:53.795975	f	\N
HR-EMP-2025-999e86	\N	\N	\N	John	Doe	9876543210	Regular	Active	\N	f	2025-04-10 04:07:35.718368	2025-04-10 04:07:35.719723	f	\N
\.


--
-- Data for Name: employees_historicalemployee; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.employees_historicalemployee (employee_id, user_id, first_name, last_name, phone, employment_type, status, reports_to, is_supervisor, created_at, updated_at, is_archived, change_reason, history_id, history_date, history_change_reason, history_type, dept_id, history_user_id, position_id) FROM stdin;
HR-EMP-2025-7177FE	User01d	dsada	dsada	123412	Regular	Active	\N	f	2025-04-10 19:35:42.386991+08	2025-04-10 19:35:42.427242+08	f	\N	1543	2025-04-10 19:35:42.471016+08	\N	+	HR-DEPT-2025-26b8a4	1	REG-2504-ef4a
HR-EMP-2025-119984	User01	Leave me when you foudn me	sadaddont kleeeaohhhhhhhhhh i just llve way got	09123456dd	Regular	Active	\N	f	2025-04-10 18:07:24.552695+08	2025-04-10 18:07:24.553235+08	f	\N	1544	2025-04-10 19:35:55.950004+08	\N	-	HR-DEPT-2025-26b8a4	1	REG-2504-ef4a
HR-EMP-2025-0b9318	User01	Leave me when you foudn me	sadaddont kleeeaohhhhhhhhhh i just llve way got	09123456dd	Regular	Active	\N	f	2025-04-10 18:07:24.552695+08	2025-04-10 18:07:24.553235+08	f	\N	1545	2025-04-10 19:36:01.207618+08	\N	-	HR-DEPT-2025-26b8a4	1	REG-2504-ef4a
HR-EMP-2025-521605	User01	asda	dsa	09123456	Regular	Active	\N	f	2025-04-10 18:06:39.412664+08	2025-04-10 18:06:39.413305+08	f	\N	1546	2025-04-10 19:36:12.29851+08	\N	-	HR-DEPT-2025-26b8a4	1	REG-2504-ef4a
HR-EMP-2025-eefb18	User01	HAHA	HAHAHA	342423432	Regular	Active	\N	f	2025-04-10 18:11:31.481383+08	2025-04-10 18:11:31.48278+08	f	\N	1547	2025-04-10 19:36:15.498253+08	\N	-	HR-DEPT-2025-26b8a4	1	REG-2504-ef4a
HR-EMP-2025-d3f6f0	User01	HAHA	HAHAHA	342423432	Regular	Active	\N	f	2025-04-10 18:11:31.481383+08	2025-04-10 18:11:31.48278+08	f	\N	1548	2025-04-10 19:36:19.085841+08	\N	-	HR-DEPT-2025-26b8a4	1	REG-2504-ef4a
HR-EMP-2025-7005e9	User01d	dsada	dsada	123412	Regular	Active	\N	f	2025-04-10 19:35:42.386991+08	2025-04-10 19:35:42.388588+08	f	\N	1549	2025-04-10 19:36:25.107581+08	\N	-	HR-DEPT-2025-26b8a4	1	REG-2504-ef4a
	User01	asda	dsa	09123456	Regular	Active	\N	f	2025-04-10 18:06:39.412664+08	2025-04-10 18:06:39.420685+08	f	\N	1497	2025-04-10 18:06:39.425365+08	\N	+	HR-DEPT-2025-26b8a4	1	REG-2504-ef4a
	User01	asda	dsa	09123456	Regular	Active	\N	f	2025-04-10 18:06:39.412664+08	2025-04-10 18:06:39.430577+08	f	\N	1498	2025-04-10 18:06:39.43102+08	\N	+	HR-DEPT-2025-26b8a4	1	REG-2504-ef4a
HR-EMP-2025-bf0844	User01	asda	dsa	09123456	Regular	Active	\N	f	2025-04-10 18:06:39.412664+08	2025-04-10 18:06:39.413305+08	f	\N	1499	2025-04-10 18:06:57.702662+08	\N	-	HR-DEPT-2025-26b8a4	1	REG-2504-ef4a
	User01	Leave me when you foudn me	sadaddont kleeeaohhhhhhhhhh i just llve way got	09123456dd	Regular	Active	\N	f	2025-04-10 18:07:24.552695+08	2025-04-10 18:07:24.560154+08	f	\N	1500	2025-04-10 18:07:24.564447+08	\N	+	HR-DEPT-2025-26b8a4	1	REG-2504-ef4a
	User01	Leave me when you foudn me	sadaddont kleeeaohhhhhhhhhh i just llve way got	09123456dd	Regular	Active	\N	f	2025-04-10 18:07:24.552695+08	2025-04-10 18:07:24.569397+08	f	\N	1501	2025-04-10 18:07:24.569987+08	\N	+	HR-DEPT-2025-26b8a4	1	REG-2504-ef4a
	User01	HAHA	HAHAHA	342423432	Regular	Active	\N	f	2025-04-10 18:11:31.481383+08	2025-04-10 18:11:31.503831+08	f	\N	1502	2025-04-10 18:11:31.533091+08	\N	+	HR-DEPT-2025-26b8a4	1	REG-2504-ef4a
	User01	HAHA	HAHAHA	342423432	Regular	Active	\N	f	2025-04-10 18:11:31.481383+08	2025-04-10 18:11:31.544241+08	f	\N	1503	2025-04-10 18:11:31.54513+08	\N	+	HR-DEPT-2025-26b8a4	1	REG-2504-ef4a
HR-EMP-2025-375A57	User01d	sadas	dsada	123412	Regular	Active	\N	f	2025-04-10 20:40:42.75641+08	2025-04-10 20:40:42.767817+08	f	\N	1610	2025-04-10 20:40:42.774135+08	\N	+	HR-DEPT-2025-26b8a4	1	REG-2504-ef4a
HR-EMP-2025-179bd5	User01d	sadas	dsada	123412	Regular	Active	\N	f	2025-04-10 20:40:42.75641+08	2025-04-10 20:40:42.757619+08	f	\N	1611	2025-04-10 20:41:33.414782+08	\N	-	HR-DEPT-2025-26b8a4	1	REG-2504-ef4a
\.


--
-- Data for Name: human_resources.department_superiors; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources."human_resources.department_superiors" (id, dept_id, superior_job_title, hierarchy_level) FROM stdin;
\.


--
-- Data for Name: human_resources.employees; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources."human_resources.employees" (employee_id, dept_id, position_id, first_name, last_name, phone, employment_type, status, reports_to, is_supervisor, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: human_resources.positions; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources."human_resources.positions" (position_id, position_title, salary_grade, min_salary, max_salary, employment_type, typical_duration_days, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: job_posting; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.job_posting (job_id, dept_id, position_id, position_title, description, requirements, employment_type, base_salary, daily_rate, duration_days, finance_approval_id, finance_approval_status, posting_status, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: leave_requests; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.leave_requests (leave_id, employee_id, dept_id, immediate_superior_id, management_approval_id, leave_type, start_date, end_date, total_days, is_paid, status, updated_at) FROM stdin;
\.


--
-- Data for Name: payroll; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.payroll (payroll_id, employee_id, pay_period_start, pay_period_end, employment_type, base_salary, overtime_hours, overtime_pay, holiday_pay, bonus_pay, thirteenth_month_pay, sss_contribution, philhealth_contribution, pagibig_contribution, tax, late_deduction, absent_deduction, undertime_deduction, status, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: positions; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.positions (position_id, position_title, salary_grade, min_salary, max_salary, employment_type, typical_duration_days, is_active, created_at, updated_at, employee_id, is_archived, change_reason) FROM stdin;
REG-2504-ef4a	Laygo's Slave - Edited	1	0.00	1.00	Regular	\N	t	2025-04-08 10:40:23.013926	2025-04-08 10:41:31.577248	\N	f	\N
SEA-2504-d576	Legal Consultant	SG-CT-09	500.00	700.00	Contractual	60	t	2025-04-07 18:12:29.217568	2025-04-08 00:07:28.506223	\N	f	\N
SEA-2504-e256	Marketing Assistant	SG-CT-11	900.00	1200.00	Contractual	60	t	2025-04-07 18:12:29.217568	2025-04-08 00:07:38.410592	\N	f	\N
REG-2504-9b2a	Chief Accountant	SG-CA-3	60000.00	68000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-4e93	Accounting Supervisor	SG-AS-5	35000.00	38000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-cce8	Administrative Manager	SG-AM-4	55000.00	60000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-3a8e	Office Administrator	SG-O6	22000.00	25000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-eb03	Distribution Manager	SG-DM-3	95000.00	105000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-a218	Chief Financial Officer	SG-CFO-7	150000.00	170000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-d2b8	Finance Manager	SG-FM-3	46000.00	50000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-f87e	HR Director	SG-HRD-9	110000.00	130000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-6363	HR Manager	SG-HRM-5	64000.00	72000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-fb38	Inventory Manager	SG-IM-3	32000.00	38000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-8d4e	Chief Executive Officer	SG-CEO-5	240000.00	260000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-0bef	Chief Operations Officer	SG-COO-3	170000.00	190000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-8ab5	General Manager	SG-GM-6	110000.00	130000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-a0dd	Assistant Manager	SG-AMGR-8	55000.00	65000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-a794	MRP Manager	SG-MRP-1	37000.00	42000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-131f	Operations Manager	SG-OM-2	85000.00	95000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-5eef	Production Manager	SG-PM-5	76000.00	84000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-d999	Project Manager	SG-PM-6	60000.00	65000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-fb50	Purchasing Manager	SG-PM-7	43000.00	47000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-8731	Sales Director	SG-SD-9	54000.00	58000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
CTR-2504-99c0	Sales Manager	SG-SM-4	33000.00	37000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
CTR-2504-769b	Customer Service Manager	SG-CSM-6	48000.00	52000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
CTR-2504-70d0	Maintenance Manager	SG-MM-6	43000.00	47000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
CTR-2504-6589	IT Manager	SG-ITM-3	70000.00	76000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
CTR-2504-1f9e	Network Administrator	SG-NA-8	33000.00	37000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
CTR-2504-ccc6	System Administrator	SG-SA-2	43000.00	47000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
CTR-2504-bd5d	Quality Control Inspector	SG-QCI-3	16000.00	20000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
CTR-2504-152f	HSE Manager	SG-HSEM-7	23000.00	27000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
CTR-2504-f05b	Security Manager	SG-SM-6	61000.00	67000.00	Regular	\N	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
CTR-2504-dced	Project Accountant	SG-CT-01	1500.00	2000.00	Contractual	90	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
CTR-2504-594e	Inventory Specialist	SG-CT-02	1200.00	1500.00	Contractual	60	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
CTR-2504-177a	System Migration Consultant	SG-CT-03	2500.00	3000.00	Contractual	180	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
CTR-2504-60d2	Audit Assistant	SG-CT-04	1300.00	1600.00	Contractual	120	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
CTR-2504-df3d	Data Entry Specialist	SG-CT-05	1000.00	1200.00	Contractual	30	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
CTR-2504-2094	Marketing Assistant	SG-CT-06	800.00	1200.00	Contractual	60	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
SEA-2504-ccdc	Sales Promoter	SG-CT-07	515.00	700.00	Contractual	30	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
SEA-2504-8866	Graphic Designer	SG-CT-08	1100.00	1400.00	Contractual	90	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
SEA-2504-4fef	Company Nurse	SG-CT-10	1100.00	1400.00	Contractual	150	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
SEA-2504-4c4e	Sales Promoter	SG-CT-12	500.00	700.00	Contractual	30	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
SEA-2504-c690	Graphic Designer	SG-CT-13	1100.00	1300.00	Contractual	90	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
SEA-2504-6194	Legal Consultant	SG-CT-14	500.00	700.00	Contractual	60	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
SEA-2504-a707	Company Nurse	SG-CT-15	1200.00	1400.00	Contractual	150	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
SEA-2504-b97b	Holiday Sales Associate	SG-SN-01	800.00	1200.00	Seasonal	21	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
SEA-2504-a94e	Tax Season Accountant	SG-SN-02	1500.00	1800.00	Seasonal	28	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
SEA-2504-4390	Summer Intern	SG-SN-03	600.00	800.00	Seasonal	14	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
SEA-2504-98f9	Christmas Warehouse Helper	SG-SN-04	900.00	1100.00	Seasonal	20	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
SEA-2504-14fa	New Year Event Staff	SG-SN-05	750.00	950.00	Seasonal	7	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
SEA-2504-88e4	Logistic Support	SG-SN-06	500.00	750.00	Seasonal	14	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-d22e	Temporary Security Guard	SG-SN-07	500.00	750.00	Seasonal	7	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-d1b1	Product Demonstrator	SG-SN-08	500.00	750.00	Seasonal	21	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-3dab	Promotion Staff	SG-SN-09	600.00	800.00	Seasonal	14	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-42b9	Product Ambassador	SG-SN-10	600.00	800.00	Seasonal	28	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-e9c2	Logistic Support	SG-SN-11	550.00	600.00	Seasonal	14	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-1b64	Temporary Security Guard	SG-SN-12	550.00	600.00	Seasonal	7	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-b608	Product Demonstrator	SG-SN-13	550.00	600.00	Seasonal	21	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-945e	Promotion Staff	SG-SN-14	630.00	660.00	Seasonal	14	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
REG-2504-46e7	Product Ambassador	SG-SN-15	590.00	630.00	Seasonal	29	t	2025-04-07 18:12:29.217568	2025-04-07 18:12:29.217568	\N	f	\N
\.


--
-- Data for Name: positions_historicalposition; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.positions_historicalposition (position_id, position_title, salary_grade, min_salary, max_salary, employment_type, typical_duration_days, is_active, created_at, updated_at, is_archived, change_reason, history_id, history_date, history_change_reason, history_type, history_user_id) FROM stdin;
\.


--
-- Data for Name: resignations; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.resignations (resignation_id, employee_id, submission_date, notice_period_days, hr_approver_id, approval_status, clearance_status, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: workforce_allocation; Type: TABLE DATA; Schema: human_resources; Owner: postgres
--

COPY human_resources.workforce_allocation (allocation_id, request_id, requesting_dept_id, required_skills, task_description, employee_id, current_dept_id, hr_approver_id, approval_status, status, start_date, end_date, rejection_reason, submitted_at, approved_at, is_archived) FROM stdin;
ALLOC-202504-6512	REQ-2025-885319	HR-DEPT-2025-26b8a4	Welding, Equipment Handling	Assist with steel frame assembly in construction site.	HR-EMP-2025-e4973e	HR-DEPT-2025-0272fb	HR-EMP-2025-6bcb48	Approved	Active	2025-04-10	2025-04-30	\N	\N	\N	f
ALLOC-202504-3066	REQ-2025-848444	HR-DEPT-2025-0272fb	Inventory Management, Basic Accounting	Support warehouse inventory tracking and reporting.	HR-EMP-2025-6bcb48	HR-DEPT-2025-345995	HR-EMP-2025-6bcb48	Pending	Draft	2025-04-12	2025-04-25	\N	\N	\N	f
ALLOC-202504-4099	REQ-2025-394806	HR-DEPT-2025-345995	Machine Operation, Safety Compliance	Operate CNC machines and monitor production safety.	HR-EMP-2025-000a28	HR-DEPT-2025-2e0d12	HR-EMP-2025-a86f5e	Approved	Active	2025-04-15	2025-05-15	\N	\N	\N	f
ALLOC-202504-2718	REQ-2025-759976	HR-DEPT-2025-2e0d12	Customer Service, Communication Skills	Assist in client onboarding and inquiries handling.	HR-EMP-2025-a86f5e	HR-DEPT-2025-cca1d0	HR-EMP-2025-ae73bb	Rejected	Draft	2025-04-10	2025-04-20	\N	\N	\N	f
ALLOC-202504-6926	REQ-2025-961669	HR-DEPT-2025-cca1d0	Data Entry, Attention to Detail	Input survey data from field agents to system.	HR-EMP-2025-3b7600	HR-DEPT-2025-f57fbb	HR-EMP-2025-9c43f8	Approved	Active	2025-04-09	2025-04-18	\N	\N	\N	f
\.


--
-- Data for Name: attendance_tracking; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.attendance_tracking (attendance_id, employee_id, time_in, time_out, work_hours, status, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: employee_performance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employee_performance (performance_id, rating, bonus_percentage, bonus_amount, review_date, comments, created_at, updated_at, employee_id, immediate_superior_id) FROM stdin;
\.


--
-- Data for Name: employee_salary; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employee_salary (salary_id, employee_id, base_salary, daily_rate, contract_start_date, contract_end_date, effective_date, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: workforce_allocation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workforce_allocation (allocation_id, request_id, requesting_dept_id, required_skills, task_description, employee_id, current_dept_id, hr_approver_id, approval_status, status, start_date, end_date, rejection_reason, created_at, submitted_at, approved_at, updated_at) FROM stdin;
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: human_resources; Owner: postgres
--

SELECT pg_catalog.setval('human_resources.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: human_resources; Owner: postgres
--

SELECT pg_catalog.setval('human_resources.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: human_resources; Owner: postgres
--

SELECT pg_catalog.setval('human_resources.auth_permission_id_seq', 108, true);


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: human_resources; Owner: postgres
--

SELECT pg_catalog.setval('human_resources.auth_user_groups_id_seq', 1, false);


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: human_resources; Owner: postgres
--

SELECT pg_catalog.setval('human_resources.auth_user_id_seq', 1, true);


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: human_resources; Owner: postgres
--

SELECT pg_catalog.setval('human_resources.auth_user_user_permissions_id_seq', 1, false);


--
-- Name: department_superiors_historicaldepartment_superi_history_id_seq; Type: SEQUENCE SET; Schema: human_resources; Owner: postgres
--

SELECT pg_catalog.setval('human_resources.department_superiors_historicaldepartment_superi_history_id_seq', 1, false);


--
-- Name: departments_historicaldepartment_history_id_seq; Type: SEQUENCE SET; Schema: human_resources; Owner: postgres
--

SELECT pg_catalog.setval('human_resources.departments_historicaldepartment_history_id_seq', 45, true);


--
-- Name: dept_superior_seq; Type: SEQUENCE SET; Schema: human_resources; Owner: postgres
--

SELECT pg_catalog.setval('human_resources.dept_superior_seq', 22, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: human_resources; Owner: postgres
--

SELECT pg_catalog.setval('human_resources.django_admin_log_id_seq', 477, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: human_resources; Owner: postgres
--

SELECT pg_catalog.setval('human_resources.django_content_type_id_seq', 27, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: human_resources; Owner: postgres
--

SELECT pg_catalog.setval('human_resources.django_migrations_id_seq', 41, true);


--
-- Name: employees_historicalemployee_history_id_seq; Type: SEQUENCE SET; Schema: human_resources; Owner: postgres
--

SELECT pg_catalog.setval('human_resources.employees_historicalemployee_history_id_seq', 1612, true);


--
-- Name: human_resources.department_superiors_id_seq; Type: SEQUENCE SET; Schema: human_resources; Owner: postgres
--

SELECT pg_catalog.setval('human_resources."human_resources.department_superiors_id_seq"', 1, false);


--
-- Name: positions_historicalposition_history_id_seq; Type: SEQUENCE SET; Schema: human_resources; Owner: postgres
--

SELECT pg_catalog.setval('human_resources.positions_historicalposition_history_id_seq', 1, false);


--
-- Name: attendance_tracking attendance_tracking_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.attendance_tracking
    ADD CONSTRAINT attendance_tracking_pkey PRIMARY KEY (attendance_id);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_user_id_group_id_94350c0c_uniq; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);


--
-- Name: auth_user auth_user_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_permission_id_14a6b632_uniq; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);


--
-- Name: auth_user auth_user_username_key; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: calendar_dates calendar_dates_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.calendar_dates
    ADD CONSTRAINT calendar_dates_pkey PRIMARY KEY (date);


--
-- Name: candidates candidates_email_key; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.candidates
    ADD CONSTRAINT candidates_email_key UNIQUE (email);


--
-- Name: candidates candidates_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.candidates
    ADD CONSTRAINT candidates_pkey PRIMARY KEY (candidate_id);


--
-- Name: department_superiors_historicaldepartment_superior department_superiors_historicaldepartment_superior_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.department_superiors_historicaldepartment_superior
    ADD CONSTRAINT department_superiors_historicaldepartment_superior_pkey PRIMARY KEY (history_id);


--
-- Name: department_superiors department_superiors_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.department_superiors
    ADD CONSTRAINT department_superiors_pkey PRIMARY KEY (dept_superior_id);


--
-- Name: departments_department departments_department_name_key; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.departments_department
    ADD CONSTRAINT departments_department_name_key UNIQUE (name);


--
-- Name: departments_department departments_department_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.departments_department
    ADD CONSTRAINT departments_department_pkey PRIMARY KEY (dept_id);


--
-- Name: departments departments_dept_name_key; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.departments
    ADD CONSTRAINT departments_dept_name_key UNIQUE (dept_name);


--
-- Name: departments_historicaldepartment departments_historicaldepartment_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.departments_historicaldepartment
    ADD CONSTRAINT departments_historicaldepartment_pkey PRIMARY KEY (history_id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: employee_leave_balances employee_leave_balances_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.employee_leave_balances
    ADD CONSTRAINT employee_leave_balances_pkey PRIMARY KEY (balance_id);


--
-- Name: employee_performance employee_performance_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.employee_performance
    ADD CONSTRAINT employee_performance_pkey PRIMARY KEY (performance_id);


--
-- Name: employee_salary employee_salary_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.employee_salary
    ADD CONSTRAINT employee_salary_pkey PRIMARY KEY (salary_id);


--
-- Name: employees_historicalemployee employees_historicalemployee_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.employees_historicalemployee
    ADD CONSTRAINT employees_historicalemployee_pkey PRIMARY KEY (history_id);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (employee_id);


--
-- Name: human_resources.department_superiors human_resources.departme_dept_id_superior_job_tit_f66fc219_uniq; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources."human_resources.department_superiors"
    ADD CONSTRAINT "human_resources.departme_dept_id_superior_job_tit_f66fc219_uniq" UNIQUE (dept_id, superior_job_title);


--
-- Name: human_resources.department_superiors human_resources.department_superiors_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources."human_resources.department_superiors"
    ADD CONSTRAINT "human_resources.department_superiors_pkey" PRIMARY KEY (id);


--
-- Name: human_resources.employees human_resources.employees_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources."human_resources.employees"
    ADD CONSTRAINT "human_resources.employees_pkey" PRIMARY KEY (employee_id);


--
-- Name: human_resources.positions human_resources.positions_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources."human_resources.positions"
    ADD CONSTRAINT "human_resources.positions_pkey" PRIMARY KEY (position_id);


--
-- Name: job_posting job_posting_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.job_posting
    ADD CONSTRAINT job_posting_pkey PRIMARY KEY (job_id);


--
-- Name: leave_requests leave_requests_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.leave_requests
    ADD CONSTRAINT leave_requests_pkey PRIMARY KEY (leave_id);


--
-- Name: payroll payroll_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.payroll
    ADD CONSTRAINT payroll_pkey PRIMARY KEY (payroll_id);


--
-- Name: departments pk_departments; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.departments
    ADD CONSTRAINT pk_departments PRIMARY KEY (dept_id);


--
-- Name: positions_historicalposition positions_historicalposition_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.positions_historicalposition
    ADD CONSTRAINT positions_historicalposition_pkey PRIMARY KEY (history_id);


--
-- Name: positions positions_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.positions
    ADD CONSTRAINT positions_pkey PRIMARY KEY (position_id);


--
-- Name: resignations resignations_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.resignations
    ADD CONSTRAINT resignations_pkey PRIMARY KEY (resignation_id);


--
-- Name: employee_leave_balances unique_employee_year; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.employee_leave_balances
    ADD CONSTRAINT unique_employee_year UNIQUE (employee_id, year);


--
-- Name: departments uq_departments_department_name; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.departments
    ADD CONSTRAINT uq_departments_department_name UNIQUE (dept_name);


--
-- Name: workforce_allocation workforce_allocation_pkey; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.workforce_allocation
    ADD CONSTRAINT workforce_allocation_pkey PRIMARY KEY (allocation_id);


--
-- Name: workforce_allocation workforce_allocation_request_id_key; Type: CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.workforce_allocation
    ADD CONSTRAINT workforce_allocation_request_id_key UNIQUE (request_id);


--
-- Name: attendance_tracking attendance_tracking_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance_tracking
    ADD CONSTRAINT attendance_tracking_pkey PRIMARY KEY (attendance_id);


--
-- Name: employee_performance employee_performance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_performance
    ADD CONSTRAINT employee_performance_pkey PRIMARY KEY (performance_id);


--
-- Name: employee_salary employee_salary_employee_id_effective_date_abd6f234_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_salary
    ADD CONSTRAINT employee_salary_employee_id_effective_date_abd6f234_uniq UNIQUE (employee_id, effective_date);


--
-- Name: employee_salary employee_salary_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_salary
    ADD CONSTRAINT employee_salary_pkey PRIMARY KEY (salary_id);


--
-- Name: workforce_allocation workforce_allocation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workforce_allocation
    ADD CONSTRAINT workforce_allocation_pkey PRIMARY KEY (allocation_id);


--
-- Name: workforce_allocation workforce_allocation_request_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workforce_allocation
    ADD CONSTRAINT workforce_allocation_request_id_key UNIQUE (request_id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX auth_group_name_a6ea08ec_like ON human_resources.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON human_resources.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON human_resources.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON human_resources.auth_permission USING btree (content_type_id);


--
-- Name: auth_user_groups_group_id_97559544; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX auth_user_groups_group_id_97559544 ON human_resources.auth_user_groups USING btree (group_id);


--
-- Name: auth_user_groups_user_id_6a12ed8b; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX auth_user_groups_user_id_6a12ed8b ON human_resources.auth_user_groups USING btree (user_id);


--
-- Name: auth_user_user_permissions_permission_id_1fbb5f2c; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON human_resources.auth_user_user_permissions USING btree (permission_id);


--
-- Name: auth_user_user_permissions_user_id_a95ead1b; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON human_resources.auth_user_user_permissions USING btree (user_id);


--
-- Name: auth_user_username_6821ab7c_like; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX auth_user_username_6821ab7c_like ON human_resources.auth_user USING btree (username varchar_pattern_ops);


--
-- Name: department_superiors_his_dept_id_2e4634d9_like; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX department_superiors_his_dept_id_2e4634d9_like ON human_resources.department_superiors_historicaldepartment_superior USING btree (dept_id varchar_pattern_ops);


--
-- Name: department_superiors_his_dept_superior_id_8382c7fe_like; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX department_superiors_his_dept_superior_id_8382c7fe_like ON human_resources.department_superiors_historicaldepartment_superior USING btree (dept_superior_id varchar_pattern_ops);


--
-- Name: department_superiors_his_position_id_31f9bcdd_like; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX department_superiors_his_position_id_31f9bcdd_like ON human_resources.department_superiors_historicaldepartment_superior USING btree (position_id varchar_pattern_ops);


--
-- Name: department_superiors_histo_dept_id_2e4634d9; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX department_superiors_histo_dept_id_2e4634d9 ON human_resources.department_superiors_historicaldepartment_superior USING btree (dept_id);


--
-- Name: department_superiors_histo_dept_superior_id_8382c7fe; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX department_superiors_histo_dept_superior_id_8382c7fe ON human_resources.department_superiors_historicaldepartment_superior USING btree (dept_superior_id);


--
-- Name: department_superiors_histo_history_date_8ffef604; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX department_superiors_histo_history_date_8ffef604 ON human_resources.department_superiors_historicaldepartment_superior USING btree (history_date);


--
-- Name: department_superiors_histo_history_user_id_50d6722d; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX department_superiors_histo_history_user_id_50d6722d ON human_resources.department_superiors_historicaldepartment_superior USING btree (history_user_id);


--
-- Name: department_superiors_histo_position_id_31f9bcdd; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX department_superiors_histo_position_id_31f9bcdd ON human_resources.department_superiors_historicaldepartment_superior USING btree (position_id);


--
-- Name: departments_created_by_id_86cf2aef; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX departments_created_by_id_86cf2aef ON human_resources.departments USING btree (created_by_id);


--
-- Name: departments_department_dept_id_2e912e0f_like; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX departments_department_dept_id_2e912e0f_like ON human_resources.departments_department USING btree (dept_id varchar_pattern_ops);


--
-- Name: departments_department_name_f57acac7_like; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX departments_department_name_f57acac7_like ON human_resources.departments_department USING btree (name varchar_pattern_ops);


--
-- Name: departments_historicaldepartment_dept_id_bf962f94; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX departments_historicaldepartment_dept_id_bf962f94 ON human_resources.departments_historicaldepartment USING btree (dept_id);


--
-- Name: departments_historicaldepartment_dept_id_bf962f94_like; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX departments_historicaldepartment_dept_id_bf962f94_like ON human_resources.departments_historicaldepartment USING btree (dept_id varchar_pattern_ops);


--
-- Name: departments_historicaldepartment_history_date_c0ad87eb; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX departments_historicaldepartment_history_date_c0ad87eb ON human_resources.departments_historicaldepartment USING btree (history_date);


--
-- Name: departments_historicaldepartment_history_user_id_83883ee1; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX departments_historicaldepartment_history_user_id_83883ee1 ON human_resources.departments_historicaldepartment USING btree (history_user_id);


--
-- Name: departments_updated_by_id_53cf681d; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX departments_updated_by_id_53cf681d ON human_resources.departments USING btree (updated_by_id);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON human_resources.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON human_resources.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX django_session_expire_date_a5c62663 ON human_resources.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX django_session_session_key_c0390e0f_like ON human_resources.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: employees_historicalemployee_dept_id_92befd3a; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX employees_historicalemployee_dept_id_92befd3a ON human_resources.employees_historicalemployee USING btree (dept_id);


--
-- Name: employees_historicalemployee_dept_id_92befd3a_like; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX employees_historicalemployee_dept_id_92befd3a_like ON human_resources.employees_historicalemployee USING btree (dept_id varchar_pattern_ops);


--
-- Name: employees_historicalemployee_employee_id_7249b5da; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX employees_historicalemployee_employee_id_7249b5da ON human_resources.employees_historicalemployee USING btree (employee_id);


--
-- Name: employees_historicalemployee_employee_id_7249b5da_like; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX employees_historicalemployee_employee_id_7249b5da_like ON human_resources.employees_historicalemployee USING btree (employee_id varchar_pattern_ops);


--
-- Name: employees_historicalemployee_history_date_15cf4a49; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX employees_historicalemployee_history_date_15cf4a49 ON human_resources.employees_historicalemployee USING btree (history_date);


--
-- Name: employees_historicalemployee_history_user_id_2d5aeee2; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX employees_historicalemployee_history_user_id_2d5aeee2 ON human_resources.employees_historicalemployee USING btree (history_user_id);


--
-- Name: employees_historicalemployee_position_id_fe633e8a; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX employees_historicalemployee_position_id_fe633e8a ON human_resources.employees_historicalemployee USING btree (position_id);


--
-- Name: employees_historicalemployee_position_id_fe633e8a_like; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX employees_historicalemployee_position_id_fe633e8a_like ON human_resources.employees_historicalemployee USING btree (position_id varchar_pattern_ops);


--
-- Name: human_resources.employees_employee_id_6bc3de20_like; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX "human_resources.employees_employee_id_6bc3de20_like" ON human_resources."human_resources.employees" USING btree (employee_id varchar_pattern_ops);


--
-- Name: human_resources.positions_position_id_75eabd7f_like; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX "human_resources.positions_position_id_75eabd7f_like" ON human_resources."human_resources.positions" USING btree (position_id varchar_pattern_ops);


--
-- Name: positions_historicalposition_history_date_17cc8faf; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX positions_historicalposition_history_date_17cc8faf ON human_resources.positions_historicalposition USING btree (history_date);


--
-- Name: positions_historicalposition_history_user_id_3d25c8f2; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX positions_historicalposition_history_user_id_3d25c8f2 ON human_resources.positions_historicalposition USING btree (history_user_id);


--
-- Name: positions_historicalposition_position_id_a1f79178; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX positions_historicalposition_position_id_a1f79178 ON human_resources.positions_historicalposition USING btree (position_id);


--
-- Name: positions_historicalposition_position_id_a1f79178_like; Type: INDEX; Schema: human_resources; Owner: postgres
--

CREATE INDEX positions_historicalposition_position_id_a1f79178_like ON human_resources.positions_historicalposition USING btree (position_id varchar_pattern_ops);


--
-- Name: attendance_tracking_attendance_id_5953b3fc_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX attendance_tracking_attendance_id_5953b3fc_like ON public.attendance_tracking USING btree (attendance_id varchar_pattern_ops);


--
-- Name: employee_performance_employee_id_ba623e40; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX employee_performance_employee_id_ba623e40 ON public.employee_performance USING btree (employee_id);


--
-- Name: employee_performance_employee_id_ba623e40_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX employee_performance_employee_id_ba623e40_like ON public.employee_performance USING btree (employee_id varchar_pattern_ops);


--
-- Name: employee_performance_immediate_superior_id_124c7722; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX employee_performance_immediate_superior_id_124c7722 ON public.employee_performance USING btree (immediate_superior_id);


--
-- Name: employee_performance_immediate_superior_id_124c7722_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX employee_performance_immediate_superior_id_124c7722_like ON public.employee_performance USING btree (immediate_superior_id varchar_pattern_ops);


--
-- Name: employee_performance_performance_id_2ca4fc41_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX employee_performance_performance_id_2ca4fc41_like ON public.employee_performance USING btree (performance_id varchar_pattern_ops);


--
-- Name: employee_salary_salary_id_108398b6_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX employee_salary_salary_id_108398b6_like ON public.employee_salary USING btree (salary_id varchar_pattern_ops);


--
-- Name: workforce_allocation_allocation_id_8d07ca23_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX workforce_allocation_allocation_id_8d07ca23_like ON public.workforce_allocation USING btree (allocation_id varchar_pattern_ops);


--
-- Name: workforce_allocation_request_id_f6d99541_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX workforce_allocation_request_id_f6d99541_like ON public.workforce_allocation USING btree (request_id varchar_pattern_ops);


--
-- Name: attendance_tracking before_insert_attendance; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER before_insert_attendance BEFORE INSERT ON human_resources.attendance_tracking FOR EACH ROW WHEN ((new.attendance_id IS NULL)) EXECUTE FUNCTION human_resources.generate_attendance_id();


--
-- Name: departments before_insert_department; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER before_insert_department BEFORE INSERT ON human_resources.departments FOR EACH ROW EXECUTE FUNCTION human_resources.generate_department_id();


--
-- Name: employees before_insert_employee; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER before_insert_employee BEFORE INSERT ON human_resources.employees FOR EACH ROW EXECUTE FUNCTION human_resources.generate_employee_id();


--
-- Name: workforce_allocation before_insert_request_id; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER before_insert_request_id BEFORE INSERT ON human_resources.workforce_allocation FOR EACH ROW EXECUTE FUNCTION human_resources.generate_request_id();


--
-- Name: workforce_allocation trg_allocation_id; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_allocation_id BEFORE INSERT ON human_resources.workforce_allocation FOR EACH ROW EXECUTE FUNCTION human_resources.generate_allocation_id();


--
-- Name: employee_performance trg_calculate_performance_bonus; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_calculate_performance_bonus BEFORE INSERT OR UPDATE ON human_resources.employee_performance FOR EACH ROW EXECUTE FUNCTION human_resources.calculate_performance_bonus();


--
-- Name: attendance_tracking trg_calculate_work_hours; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_calculate_work_hours BEFORE INSERT OR UPDATE ON human_resources.attendance_tracking FOR EACH ROW EXECUTE FUNCTION human_resources.calculate_work_hours();


--
-- Name: workforce_allocation trg_check_assignment_overlap; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_check_assignment_overlap BEFORE INSERT OR UPDATE ON human_resources.workforce_allocation FOR EACH ROW EXECUTE FUNCTION public.check_assignment_overlap();


--
-- Name: leave_requests trg_deduct_leave_balances; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_deduct_leave_balances AFTER UPDATE ON human_resources.leave_requests FOR EACH ROW EXECUTE FUNCTION human_resources.deduct_leave_balances();


--
-- Name: employees trg_final_payroll; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_final_payroll AFTER UPDATE OF status ON human_resources.employees FOR EACH ROW WHEN ((((new.status)::text = 'Resigned'::text) AND ((old.status)::text <> 'Resigned'::text))) EXECUTE FUNCTION human_resources.generate_final_payroll();


--
-- Name: department_superiors trg_generate_dept_superior_id; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_generate_dept_superior_id BEFORE INSERT ON human_resources.department_superiors FOR EACH ROW EXECUTE FUNCTION human_resources.generate_dept_superior_id();


--
-- Name: job_posting trg_generate_job_id; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_generate_job_id BEFORE INSERT ON human_resources.job_posting FOR EACH ROW EXECUTE FUNCTION human_resources.generate_job_id();


--
-- Name: employee_leave_balances trg_generate_leave_balance_id; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_generate_leave_balance_id BEFORE INSERT ON human_resources.employee_leave_balances FOR EACH ROW EXECUTE FUNCTION human_resources.generate_leave_balance_id();


--
-- Name: payroll trg_generate_payroll; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_generate_payroll BEFORE INSERT ON human_resources.payroll FOR EACH ROW EXECUTE FUNCTION human_resources.generate_bi_monthly_payroll();


--
-- Name: positions trg_generate_position_id; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_generate_position_id BEFORE INSERT ON human_resources.positions FOR EACH ROW WHEN ((new.position_id IS NULL)) EXECUTE FUNCTION human_resources.generate_position_id();


--
-- Name: leave_requests trg_handle_leave_approval; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_handle_leave_approval BEFORE UPDATE ON human_resources.leave_requests FOR EACH ROW EXECUTE FUNCTION human_resources.handle_leave_approval();


--
-- Name: leave_requests trg_process_leave_request; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_process_leave_request BEFORE INSERT ON human_resources.leave_requests FOR EACH ROW EXECUTE FUNCTION human_resources.process_leave_request();


--
-- Name: resignations trg_process_resignation; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_process_resignation BEFORE INSERT ON human_resources.resignations FOR EACH ROW EXECUTE FUNCTION human_resources.process_resignation();


--
-- Name: job_posting trg_set_compensation; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_set_compensation BEFORE INSERT OR UPDATE ON human_resources.job_posting FOR EACH ROW EXECUTE FUNCTION human_resources.set_compensation_values();


--
-- Name: positions trg_set_position_defaults; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_set_position_defaults BEFORE INSERT OR UPDATE ON human_resources.positions FOR EACH ROW EXECUTE FUNCTION human_resources.set_position_defaults();


--
-- Name: employees trg_set_supervisor_flag; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_set_supervisor_flag BEFORE INSERT OR UPDATE ON human_resources.employees FOR EACH ROW EXECUTE FUNCTION human_resources.set_supervisor_flag();


--
-- Name: workforce_allocation trg_track_status; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_track_status BEFORE UPDATE ON human_resources.workforce_allocation FOR EACH ROW EXECUTE FUNCTION human_resources.track_allocation_status();


--
-- Name: employees trg_update_employee_timestamp; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_update_employee_timestamp BEFORE UPDATE ON human_resources.employees FOR EACH ROW EXECUTE FUNCTION human_resources.update_employee_timestamp();


--
-- Name: leave_requests trg_update_leave_balances; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_update_leave_balances AFTER UPDATE ON human_resources.leave_requests FOR EACH ROW EXECUTE FUNCTION public.update_leave_balances();


--
-- Name: payroll trg_update_payroll_status; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_update_payroll_status BEFORE UPDATE ON human_resources.payroll FOR EACH ROW EXECUTE FUNCTION human_resources.update_payroll_status();


--
-- Name: positions trg_update_position_timestamp; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_update_position_timestamp BEFORE UPDATE ON human_resources.positions FOR EACH ROW EXECUTE FUNCTION human_resources.update_position_timestamp();


--
-- Name: candidates trg_update_timestamp_candidates; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_update_timestamp_candidates BEFORE UPDATE ON human_resources.candidates FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- Name: employees trg_update_timestamp_employees; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_update_timestamp_employees BEFORE UPDATE ON human_resources.employees FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- Name: job_posting trg_update_timestamp_job_posting; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_update_timestamp_job_posting BEFORE UPDATE ON human_resources.job_posting FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- Name: leave_requests trg_update_timestamp_leave_requests; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_update_timestamp_leave_requests BEFORE UPDATE ON human_resources.leave_requests FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- Name: payroll trg_update_timestamp_payroll; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_update_timestamp_payroll BEFORE UPDATE ON human_resources.payroll FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- Name: positions trg_update_timestamp_positions; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_update_timestamp_positions BEFORE UPDATE ON human_resources.positions FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- Name: workforce_allocation trg_update_timestamp_workforce_allocation; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_update_timestamp_workforce_allocation BEFORE UPDATE ON human_resources.workforce_allocation FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();


--
-- Name: job_posting trg_update_timestamps; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_update_timestamps BEFORE UPDATE ON human_resources.job_posting FOR EACH ROW EXECUTE FUNCTION human_resources.update_job_timestamps();


--
-- Name: job_posting trg_validate_approval; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_validate_approval BEFORE INSERT OR UPDATE ON human_resources.job_posting FOR EACH ROW EXECUTE FUNCTION human_resources.validate_finance_approval();


--
-- Name: leave_requests trg_validate_leave_request; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_validate_leave_request BEFORE INSERT ON human_resources.leave_requests FOR EACH ROW EXECUTE FUNCTION human_resources.validate_leave_request();


--
-- Name: employee_salary trg_validate_salary; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_validate_salary BEFORE INSERT OR UPDATE ON human_resources.employee_salary FOR EACH ROW EXECUTE FUNCTION human_resources.validate_salary();


--
-- Name: employees trg_validate_superior; Type: TRIGGER; Schema: human_resources; Owner: postgres
--

CREATE TRIGGER trg_validate_superior BEFORE INSERT OR UPDATE ON human_resources.employees FOR EACH ROW EXECUTE FUNCTION human_resources.validate_superior();


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES human_resources.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES human_resources.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES human_resources.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_group_id_97559544_fk_auth_group_id; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES human_resources.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_user_id_6a12ed8b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES human_resources.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES human_resources.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES human_resources.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: department_superiors_historicaldepartment_superior department_superiors_history_user_id_50d6722d_fk_auth_user; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.department_superiors_historicaldepartment_superior
    ADD CONSTRAINT department_superiors_history_user_id_50d6722d_fk_auth_user FOREIGN KEY (history_user_id) REFERENCES human_resources.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: departments departments_created_by_id_86cf2aef_fk_auth_user_id; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.departments
    ADD CONSTRAINT departments_created_by_id_86cf2aef_fk_auth_user_id FOREIGN KEY (created_by_id) REFERENCES human_resources.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: departments_historicaldepartment departments_historic_history_user_id_83883ee1_fk_auth_user; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.departments_historicaldepartment
    ADD CONSTRAINT departments_historic_history_user_id_83883ee1_fk_auth_user FOREIGN KEY (history_user_id) REFERENCES human_resources.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: departments departments_updated_by_id_53cf681d_fk_auth_user_id; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.departments
    ADD CONSTRAINT departments_updated_by_id_53cf681d_fk_auth_user_id FOREIGN KEY (updated_by_id) REFERENCES human_resources.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES human_resources.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_auth_user_id; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES human_resources.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: employees_historicalemployee employees_historical_history_user_id_2d5aeee2_fk_auth_user; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.employees_historicalemployee
    ADD CONSTRAINT employees_historical_history_user_id_2d5aeee2_fk_auth_user FOREIGN KEY (history_user_id) REFERENCES human_resources.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: attendance_tracking fk_attendance_date; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.attendance_tracking
    ADD CONSTRAINT fk_attendance_date FOREIGN KEY (date) REFERENCES human_resources.calendar_dates(date);


--
-- Name: attendance_tracking fk_attendance_employee; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.attendance_tracking
    ADD CONSTRAINT fk_attendance_employee FOREIGN KEY (employee_id) REFERENCES human_resources.employees(employee_id) ON DELETE CASCADE;


--
-- Name: workforce_allocation fk_current_dept; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.workforce_allocation
    ADD CONSTRAINT fk_current_dept FOREIGN KEY (current_dept_id) REFERENCES human_resources.departments(dept_id) ON DELETE RESTRICT;


--
-- Name: department_superiors fk_department_superiors_dept; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.department_superiors
    ADD CONSTRAINT fk_department_superiors_dept FOREIGN KEY (dept_id) REFERENCES human_resources.departments(dept_id) ON DELETE CASCADE;


--
-- Name: department_superiors fk_department_superiors_position; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.department_superiors
    ADD CONSTRAINT fk_department_superiors_position FOREIGN KEY (position_id) REFERENCES human_resources.positions(position_id) ON DELETE CASCADE;


--
-- Name: workforce_allocation fk_employee; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.workforce_allocation
    ADD CONSTRAINT fk_employee FOREIGN KEY (employee_id) REFERENCES human_resources.employees(employee_id) ON DELETE RESTRICT;


--
-- Name: employee_performance fk_employee_performance_employee; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.employee_performance
    ADD CONSTRAINT fk_employee_performance_employee FOREIGN KEY (employee_id) REFERENCES human_resources.employees(employee_id) ON DELETE CASCADE;


--
-- Name: employee_performance fk_employee_performance_superior; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.employee_performance
    ADD CONSTRAINT fk_employee_performance_superior FOREIGN KEY (immediate_superior_id) REFERENCES human_resources.employees(employee_id) ON DELETE SET NULL;


--
-- Name: employees fk_employees_dept; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.employees
    ADD CONSTRAINT fk_employees_dept FOREIGN KEY (dept_id) REFERENCES human_resources.departments(dept_id) ON DELETE RESTRICT;


--
-- Name: employees fk_employees_position; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.employees
    ADD CONSTRAINT fk_employees_position FOREIGN KEY (position_id) REFERENCES human_resources.positions(position_id) ON DELETE SET NULL;


--
-- Name: employees fk_employees_superior; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.employees
    ADD CONSTRAINT fk_employees_superior FOREIGN KEY (reports_to) REFERENCES human_resources.employees(employee_id) ON DELETE SET NULL;


--
-- Name: workforce_allocation fk_hr_approver; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.workforce_allocation
    ADD CONSTRAINT fk_hr_approver FOREIGN KEY (hr_approver_id) REFERENCES human_resources.employees(employee_id) ON DELETE SET NULL;


--
-- Name: workforce_allocation fk_requesting_dept; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.workforce_allocation
    ADD CONSTRAINT fk_requesting_dept FOREIGN KEY (requesting_dept_id) REFERENCES human_resources.departments(dept_id) ON DELETE RESTRICT;


--
-- Name: resignations fk_resignation_approver; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.resignations
    ADD CONSTRAINT fk_resignation_approver FOREIGN KEY (hr_approver_id) REFERENCES human_resources.employees(employee_id);


--
-- Name: resignations fk_resignation_employee; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.resignations
    ADD CONSTRAINT fk_resignation_employee FOREIGN KEY (employee_id) REFERENCES human_resources.employees(employee_id);


--
-- Name: employee_salary fk_salary_employee; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.employee_salary
    ADD CONSTRAINT fk_salary_employee FOREIGN KEY (employee_id) REFERENCES human_resources.employees(employee_id) ON DELETE CASCADE;


--
-- Name: positions_historicalposition positions_historical_history_user_id_3d25c8f2_fk_auth_user; Type: FK CONSTRAINT; Schema: human_resources; Owner: postgres
--

ALTER TABLE ONLY human_resources.positions_historicalposition
    ADD CONSTRAINT positions_historical_history_user_id_3d25c8f2_fk_auth_user FOREIGN KEY (history_user_id) REFERENCES human_resources.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: SCHEMA accounting; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA accounting TO PUBLIC;


--
-- Name: SCHEMA admin; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA admin TO PUBLIC;


--
-- Name: SCHEMA distribution; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA distribution TO PUBLIC;


--
-- Name: SCHEMA finance; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA finance TO PUBLIC;


--
-- Name: SCHEMA human_resources; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA human_resources TO PUBLIC;


--
-- Name: SCHEMA inventory; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA inventory TO PUBLIC;


--
-- Name: SCHEMA management; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA management TO PUBLIC;


--
-- Name: SCHEMA mrp; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA mrp TO PUBLIC;


--
-- Name: SCHEMA operations; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA operations TO PUBLIC;


--
-- Name: SCHEMA production; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA production TO PUBLIC;


--
-- Name: SCHEMA project_management; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA project_management TO PUBLIC;


--
-- Name: SCHEMA purchasing; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA purchasing TO PUBLIC;


--
-- Name: SCHEMA sales; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA sales TO PUBLIC;


--
-- Name: SCHEMA services; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA services TO PUBLIC;


--
-- Name: SCHEMA solution_customizing; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA solution_customizing TO PUBLIC;


--
-- Name: TABLE attendance_tracking; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.attendance_tracking TO erp_user;


--
-- Name: TABLE auth_group; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.auth_group TO erp_user;


--
-- Name: TABLE auth_group_permissions; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.auth_group_permissions TO erp_user;


--
-- Name: TABLE auth_permission; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.auth_permission TO erp_user;


--
-- Name: TABLE auth_user; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.auth_user TO erp_user;


--
-- Name: TABLE auth_user_groups; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.auth_user_groups TO erp_user;


--
-- Name: TABLE auth_user_user_permissions; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.auth_user_user_permissions TO erp_user;


--
-- Name: TABLE calendar_dates; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.calendar_dates TO erp_user;


--
-- Name: TABLE candidates; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.candidates TO erp_user;


--
-- Name: TABLE department_superiors; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.department_superiors TO erp_user;


--
-- Name: TABLE department_superiors_historicaldepartment_superior; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.department_superiors_historicaldepartment_superior TO erp_user;


--
-- Name: TABLE departments; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.departments TO erp_user;


--
-- Name: TABLE employees; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.employees TO erp_user;


--
-- Name: TABLE positions; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.positions TO erp_user;


--
-- Name: TABLE department_superiors_view; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.department_superiors_view TO erp_user;


--
-- Name: TABLE departments_department; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.departments_department TO erp_user;


--
-- Name: TABLE departments_historicaldepartment; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.departments_historicaldepartment TO erp_user;


--
-- Name: TABLE django_admin_log; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.django_admin_log TO erp_user;


--
-- Name: TABLE django_content_type; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.django_content_type TO erp_user;


--
-- Name: TABLE django_migrations; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.django_migrations TO erp_user;


--
-- Name: TABLE django_session; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.django_session TO erp_user;


--
-- Name: TABLE employee_leave_balances; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.employee_leave_balances TO erp_user;


--
-- Name: TABLE employee_performance; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.employee_performance TO erp_user;


--
-- Name: TABLE employee_salary; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.employee_salary TO erp_user;


--
-- Name: TABLE employees_historicalemployee; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.employees_historicalemployee TO erp_user;


--
-- Name: TABLE "human_resources.department_superiors"; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources."human_resources.department_superiors" TO erp_user;


--
-- Name: TABLE "human_resources.employees"; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources."human_resources.employees" TO erp_user;


--
-- Name: TABLE "human_resources.positions"; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources."human_resources.positions" TO erp_user;


--
-- Name: TABLE job_posting; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.job_posting TO erp_user;


--
-- Name: TABLE leave_requests; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.leave_requests TO erp_user;


--
-- Name: TABLE payroll; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.payroll TO erp_user;


--
-- Name: TABLE positions_historicalposition; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.positions_historicalposition TO erp_user;


--
-- Name: TABLE resignations; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.resignations TO erp_user;


--
-- Name: TABLE workforce_allocation; Type: ACL; Schema: human_resources; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE human_resources.workforce_allocation TO erp_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: accounting; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA accounting GRANT SELECT,INSERT,UPDATE ON TABLES TO erp_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: admin; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA admin GRANT SELECT,INSERT,UPDATE ON TABLES TO erp_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: distribution; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA distribution GRANT SELECT,INSERT,UPDATE ON TABLES TO erp_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: finance; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA finance GRANT SELECT,INSERT,UPDATE ON TABLES TO erp_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: human_resources; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA human_resources GRANT SELECT,INSERT,UPDATE ON TABLES TO erp_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: inventory; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA inventory GRANT SELECT,INSERT,UPDATE ON TABLES TO erp_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: management; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA management GRANT SELECT,INSERT,UPDATE ON TABLES TO erp_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: mrp; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA mrp GRANT SELECT,INSERT,UPDATE ON TABLES TO erp_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: operations; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA operations GRANT SELECT,INSERT,UPDATE ON TABLES TO erp_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: production; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA production GRANT SELECT,INSERT,UPDATE ON TABLES TO erp_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: project_management; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA project_management GRANT SELECT,INSERT,UPDATE ON TABLES TO erp_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: purchasing; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA purchasing GRANT SELECT,INSERT,UPDATE ON TABLES TO erp_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: sales; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA sales GRANT SELECT,INSERT,UPDATE ON TABLES TO erp_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: services; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA services GRANT SELECT,INSERT,UPDATE ON TABLES TO erp_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: solution_customizing; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA solution_customizing GRANT SELECT,INSERT,UPDATE ON TABLES TO erp_user;


--
-- PostgreSQL database dump complete
--

