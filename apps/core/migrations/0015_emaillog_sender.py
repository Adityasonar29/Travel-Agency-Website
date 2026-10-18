from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0014_contactmessage_replied_at_contactmessage_reply_body_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="emaillog",
            name="sender",
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
