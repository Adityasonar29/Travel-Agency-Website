from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0012_repair_admin_log_user_fk'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=255)),
                ('template_path', models.CharField(blank=True, max_length=255)),
                ('event', models.CharField(blank=True, max_length=120)),
                ('body_text', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('sent', 'Sent'), ('failed', 'Failed')], default='sent', max_length=20)),
                ('error_message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
