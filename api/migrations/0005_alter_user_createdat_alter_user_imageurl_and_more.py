# Generated by Django 4.1.13 on 2025-04-01 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_rename_clerk_id_user_clerkid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='createdAt',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='user',
            name='imageUrl',
            field=models.URLField(max_length=500),
        ),
        migrations.AlterField(
            model_name='user',
            name='updatedAt',
            field=models.DateTimeField(),
        ),
    ]
