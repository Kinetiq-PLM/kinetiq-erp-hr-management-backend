# Generated by Django 5.1.6 on 2025-04-04 00:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('dept_id', models.CharField(editable=False, max_length=20, primary_key=True, serialize=False)),
                ('dept_name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'db_table': 'departments',
            },
        ),
    ]
