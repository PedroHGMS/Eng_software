# Generated by Django 5.2 on 2025-05-02 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_alter_review_professor'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='disciplina',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
