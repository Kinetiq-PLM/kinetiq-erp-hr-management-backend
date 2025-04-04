from rest_framework.test import APITestCase
from rest_framework import status
from .models import Department

class DepartmentTests(APITestCase):

    def test_create_department(self):
        response = self.client.post('/departments/', {'name': 'Logistics Department'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('dept_id', response.data)

    def test_delete_department(self):
        dept = Department.objects.create(name='Temp Department')
        response = self.client.delete(f'/departments/{dept.dept_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
