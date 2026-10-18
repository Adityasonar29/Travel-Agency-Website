from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0015_emaillog_sender"),
    ]

    operations = [
        migrations.AddField(
            model_name="emaillog",
            name="body_html",
            field=models.TextField(blank=True),
        ),
    ]
