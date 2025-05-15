import requests
import io
import time
import random
from PIL import Image
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from employees.models import Employee
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Synchronizes employees from external API'

    def handle(self, *args, **options):
        self.stdout.write('Fetching employees from API...')
        
        try:
            # Fetch employees from API
            response = requests.get('https://x0crs910m2.execute-api.ap-southeast-1.amazonaws.com/dev/api/employees/employees')
            
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Failed to fetch employees: {response.status_code}'))
                return
                
            try:
                employees_data = response.json()
                self.stdout.write(f"Employees data structure: {employees_data}")  # Debugging line
            except ValueError as e:
                self.stdout.write(self.style.ERROR(f"Failed to parse JSON: {e}"))
                return
            
            if not isinstance(employees_data, list):
                self.stdout.write(self.style.WARNING(f"Unexpected data format: {employees_data}"))
                return

            self.stdout.write(f'Fetched {len(employees_data)} employees')

            for employee_data in employees_data:
                if not isinstance(employee_data, dict):
                    self.stdout.write(self.style.WARNING(f"Skipping invalid employee data: {employee_data}"))
                    continue
                
                employee_id = employee_data.get('employee_id', '')
                if not employee_id:
                    self.stdout.write(self.style.WARNING(f"Skipping employee with missing employee_id: {employee_data}"))
                    continue

                generated_email = f"{employee_id.lower()}@company.com"

                # Get or create employee
                employee, created = Employee.objects.update_or_create(
                    employee_id=employee_data.get('employee_id'),
                    defaults={
                        'first_name': employee_data.get('first_name', ''),
                        'last_name': employee_data.get('last_name', ''),
                        'phone': employee_data.get('phone', ''),
                        'designation': employee_data.get('position_title', ''),
                        'email': generated_email,
                    }
                )
                
                # Add an AI-generated face photo if none exists
                if not employee.photo:
                    try:
                        random_param = random.randint(1, 1000000)
                        img_response = requests.get(f'https://thispersondoesnotexist.com?{random_param}', 
                                                  headers={'User-Agent': 'Mozilla/5.0'})
                        
                        if img_response.status_code == 200:
                            img = Image.open(io.BytesIO(img_response.content))
                            output = io.BytesIO()
                            img = img.convert('RGB')
                            img.save(output, format='JPEG', quality=85)
                            output.seek(0)
                            file_name = f'{employee.first_name}_{employee.last_name}.jpg'
                            employee.photo.save(file_name, ContentFile(output.read()), save=True)
                            self.stdout.write(f'Added AI-generated face image for {employee.first_name} {employee.last_name}')
                            time.sleep(1)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Failed to add AI-generated image: {e}'))
                        # Fallback to placeholder
                        try:
                            placeholder_url = f"https://placehold.co/400x500/gray/white?text={employee.first_name[0]}{employee.last_name[0]}"
                            img_response = requests.get(placeholder_url)
                            if img_response.status_code == 200:
                                img = Image.open(io.BytesIO(img_response.content))
                                output = io.BytesIO()
                                img = img.convert('RGB')
                                img.save(output, format='JPEG', quality=85)
                                output.seek(0)
                                
                                employee.photo.save(f'{employee.first_name}_{employee.last_name}.jpg', 
                                                  ContentFile(output.read()), save=True)
                                self.stdout.write(f'Added placeholder image for {employee.first_name} {employee.last_name}')
                        except Exception as fallback_error:
                            self.stdout.write(self.style.ERROR(f'Fallback placeholder also failed: {fallback_error}'))
                
                status = 'Created' if created else 'Updated'
                self.stdout.write(self.style.SUCCESS(f'{status} employee: {employee.first_name} {employee.last_name}'))
                
            self.stdout.write(self.style.SUCCESS('Employee synchronization completed'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error synchronizing employees: {str(e)}'))
