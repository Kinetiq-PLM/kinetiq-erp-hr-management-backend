# Generated by Django 5.1.7 on 2025-04-07 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('attendance_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('employee_id', models.CharField(default='HR-EMP-0000', max_length=20)),
                ('time_in', models.DateTimeField()),
                ('time_out', models.DateTimeField(blank=True, null=True)),
                ('work_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('status', models.CharField(choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Late', 'Late'), ('Half-Day', 'Half-Day'), ('On Leave', 'On Leave')], default='Present', max_length=10)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'attendance_tracking',
            },
        ),
    ]
