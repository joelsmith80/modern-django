# Generated by Django 2.1.1 on 2019-01-03 04:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('races', '0014_league_is_classic'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinalResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='races.Race')),
                ('rider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='races.Rider')),
            ],
            options={
                'db_table': 'final_results',
            },
        ),
        migrations.CreateModel(
            name='Jersey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('bib', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='races.Race')),
                ('rider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='races.Rider')),
            ],
            options={
                'db_table': 'jerseys',
            },
        ),
    ]
