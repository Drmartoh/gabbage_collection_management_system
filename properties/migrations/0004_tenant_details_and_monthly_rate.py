# Generated manually for tenant details and per-tenant rate

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0003_landlord_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='house_no',
            field=models.CharField(blank=True, help_text='House/unit number', max_length=50),
        ),
        migrations.AddField(
            model_name='tenant',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='tenant',
            name='monthly_rate',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Leave blank to use the standard fee. Set to override for this tenant (KES/month).',
                max_digits=10,
                null=True,
            ),
        ),
    ]
