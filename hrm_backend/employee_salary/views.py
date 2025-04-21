from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import DatabaseError
from .models import Employee_Salary
from .serializers import (
    Employee_Salary_Serializer,
    Employee_Salary_CreateSerializer
)
from employees.models import Employee

class IsHRMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.has_perm('employee_salary.view_employee_salary'):
            raise PermissionDenied("You do not have permission to view this resource.")
        return True

class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    queryset = Employee_Salary.objects.all()
    lookup_field = 'salary_id'
    # permission_classes = [permissions.IsAuthenticated, IsHRMember]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['employee__employee_id']
    ordering_fields = ['effective_date', 'base_salary', 'daily_rate']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Employee_Salary_CreateSerializer
        return Employee_Salary_Serializer

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except DatabaseError as e:
            error_message = str(e)
            
            # Foreign key constraint violation from labor_cost table
            if "violates foreign key constraint" in error_message and "labor_cost" in error_message:
                raise ValidationError({
                    "non_field_errors": [
                        "This salary record is currently being used in labor cost calculations and cannot be modified. "
                        "Please contact your administrator for assistance."
                    ]
                })
            
            # Format trigger validation errors into user-friendly messages
            if "Regular employees must have a positive base salary" in error_message:
                raise ValidationError({"base_salary": ["Regular employees must have a positive base salary."]})
            elif "Contractual/Seasonal employees must have a positive daily rate" in error_message:
                raise ValidationError({"daily_rate": ["Contractual/Seasonal employees must have a positive daily rate."]})
            elif "Base salary must be within position's min/max range" in error_message:
                # Get salary range info to provide a helpful error message
                instance = self.get_object()
                employee = instance.employee
                try:
                    position = employee.position
                    min_salary = position.min_salary
                    max_salary = position.max_salary
                    range_message = f"Base salary must be between {min_salary} and {max_salary} for this position."
                except:
                    range_message = "Base salary must be within the allowed range for this position."
                
                raise ValidationError({"base_salary": [range_message]})
            elif "Regular employees should not have a daily rate" in error_message:
                raise ValidationError({"daily_rate": ["Regular employees should not have a daily rate."]})
            elif "Contractual/Seasonal employees should not have a base salary" in error_message:
                raise ValidationError({"base_salary": ["Contractual/Seasonal employees should not have a base salary."]})
            else:
                # For any other database errors
                raise ValidationError({"non_field_errors": [f"Database error: {error_message}"]})

    def partial_update(self, request, *args, **kwargs):
        # Handle specific validation for partial updates
        try:
            # Get the salary instance and employee's employment type
            instance = self.get_object()
            employee = instance.employee
            employment_type = employee.employment_type
            
            # Pre-validate based on employment type
            if employment_type == 'Regular':
                if 'daily_rate' in request.data and request.data['daily_rate'] is not None:
                    raise ValidationError({"daily_rate": ["Regular employees should not have a daily rate."]})
                if 'base_salary' in request.data:
                    if request.data['base_salary'] is None or float(request.data['base_salary']) <= 0:
                        raise ValidationError({"base_salary": ["Regular employees must have a positive base salary."]})
                    
                    # Check salary range if possible
                    try:
                        position = employee.position
                        base_salary = float(request.data['base_salary'])
                        if base_salary < position.min_salary or base_salary > position.max_salary:
                            raise ValidationError({
                                "base_salary": [f"Base salary must be between {position.min_salary} and {position.max_salary} for this position."]
                            })
                    except AttributeError:
                        # If we can't access position data, let the database trigger handle it
                        pass
            
            elif employment_type in ['Contractual', 'Seasonal']:
                if 'base_salary' in request.data and request.data['base_salary'] is not None:
                    raise ValidationError({"base_salary": ["Contractual/Seasonal employees should not have a base salary."]})
                if 'daily_rate' in request.data:
                    if request.data['daily_rate'] is None or float(request.data['daily_rate']) <= 0:
                        raise ValidationError({"daily_rate": ["Contractual/Seasonal employees must have a positive daily rate."]})
            
            return super().partial_update(request, *args, **kwargs)
        
        except ValidationError:
            # Re-raise validation errors
            raise
        except DatabaseError as e:
            error_message = str(e)
            
            # Foreign key constraint violation from labor_cost table
            if "violates foreign key constraint" in error_message and "labor_cost" in error_message:
                raise ValidationError({
                    "non_field_errors": [
                        "This salary record is currently being used in labor cost calculations and cannot be modified. "
                        "Please contact your administrator for assistance."
                    ]
                })
                
            # Handle other database errors using existing update method handler
            return self.update(request, *args, **kwargs)
        except Exception as e:
            # Catch any other unexpected errors
            raise ValidationError({"non_field_errors": [f"An error occurred: {str(e)}"]})

    @action(detail=False, methods=['get'], url_path='history/(?P<employee_id>[^/.]+)')
    def salary_history(self, request, employee_id=None):
        salaries = self.queryset.filter(employee__employee_id=employee_id).order_by('-effective_date')
        serializer = self.get_serializer(salaries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='employee-type/(?P<employee_id>[^/.]+)')
    def get_employee_type(self, request, employee_id=None):
        """Get employee's employment type for frontend validation"""
        try:
            employee = Employee.objects.get(employee_id=employee_id)
            return Response({
                "employee_id": employee_id,
                "employment_type": employee.employment_type
            })
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )