# Generated by Django 3.2.6 on 2022-06-04 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_unitsmetrobusstatus_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitsmetrobusstatus',
            name='address',
            field=models.CharField(max_length=300),
        ),
    ]
