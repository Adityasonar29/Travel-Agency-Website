from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('booking', '0009_alter_review_rating_alter_review_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='cancellation_reason',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='cancelled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='refund_status',
            field=models.CharField(
                choices=[
                    ('not_applicable', 'Not applicable'),
                    ('pending', 'Refund pending'),
                    ('processed', 'Refund processed'),
                ],
                default='not_applicable',
                max_length=20,
            ),
        ),
    ]
