# Generated by Django 5.1.7 on 2025-04-08 00:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('departments', '0001_initial'),
        ('positions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DepartmentSuperior',
            fields=[
                ('dept_superior_id', models.AutoField(primary_key=True, serialize=False)),
                ('hierarchy_level', models.PositiveIntegerField()),
                ('is_archived', models.BooleanField(default=False)),
                ('dept', models.ForeignKey(db_column='dept_id', on_delete=django.db.models.deletion.CASCADE, to='departments.department')),
                ('position', models.ForeignKey(db_column='position_id', on_delete=django.db.models.deletion.CASCADE, to='positions.position')),
            ],
            options={
                'db_table': 'department_superiors',
                'unique_together': {('dept', 'position')},
            },
        ),
    ]
