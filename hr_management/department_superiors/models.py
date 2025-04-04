from django.db import models

class DepartmentSuperior(models.Model):
    dept_id = models.CharField(max_length=255, primary_key=True)
    superior_job_title = models.CharField(max_length=100)
    hierarchy_level = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.dept_id} - {self.superior_job_title} (Level {self.hierarchy_level})"

    class Meta:
        db_table = "department_superiors"
        unique_together = ('dept_id', 'superior_job_title')
