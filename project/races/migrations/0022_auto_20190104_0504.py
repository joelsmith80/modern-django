# Generated by Django 2.1.1 on 2019-01-04 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('races', '0021_auto_20190104_0500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rider',
            name='id',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
    ]
