# Generated by Django 2.1.1 on 2019-01-04 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('races', '0023_auto_20190104_0507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rider',
            name='birthday',
            field=models.DateField(blank=True, null=True),
        ),
    ]