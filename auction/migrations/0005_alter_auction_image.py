# Generated by Django 4.2.5 on 2023-10-09 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0004_rename_image_url_auction_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='static\\sneaker1.jpg'),
        ),
    ]
