# Generated by Django 2.2.2 on 2019-11-01 17:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0008_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoicelineitem',
            name='product_code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invoice.Product'),
        ),
    ]
