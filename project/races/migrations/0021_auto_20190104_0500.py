# Generated by Django 2.1.1 on 2019-01-04 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('races', '0020_auto_20190103_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rider',
            name='id',
            field=models.PositiveIntegerField(primary_key=True, serialize=False),
        ),
    ]
