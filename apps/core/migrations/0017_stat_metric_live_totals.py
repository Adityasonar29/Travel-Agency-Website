from django.db import migrations, models


def configure_site_stats(apps, schema_editor):
    Stat = apps.get_model("core", "Stat")

    metric_labels = {
        "tours": "Tours",
        "destinations": "Destinations",
        "travelers": "Happy Travelers",
        "satisfaction": "Satisfaction",
    }

    for stat in Stat.objects.all():
        label = stat.label.lower()
        if "destination" in label:
            stat.metric = "destinations"
        elif "traveler" in label or "traveller" in label:
            stat.metric = "travelers"
        elif "satisfaction" in label:
            stat.metric = "satisfaction"
        elif "tour" in label:
            stat.metric = "tours"

        if stat.metric in {"tours", "destinations", "travelers"}:
            stat.suffix = ""
            stat.save(update_fields=["metric", "suffix"])
        elif stat.metric == "satisfaction":
            stat.suffix = "%"
            stat.save(update_fields=["metric", "suffix"])

    next_order = (Stat.objects.order_by("-order").values_list("order", flat=True).first() or 0) + 1
    defaults = {
        "tours": {"value": 0, "suffix": ""},
        "destinations": {"value": 0, "suffix": ""},
        "travelers": {"value": 0, "suffix": ""},
        "satisfaction": {"value": 98, "suffix": "%"},
    }
    for metric, label in metric_labels.items():
        if not Stat.objects.filter(metric=metric).exists():
            Stat.objects.create(
                label=label,
                metric=metric,
                order=next_order,
                **defaults[metric],
            )
            next_order += 1

    if not Stat.objects.filter(label__icontains="years experience").exists():
        Stat.objects.create(
            label="Years Experience",
            value=15,
            suffix="+",
            metric="manual",
            order=next_order,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0016_emaillog_body_html"),
    ]

    operations = [
        migrations.AddField(
            model_name="stat",
            name="metric",
            field=models.CharField(
                choices=[
                    ("manual", "Manually maintained"),
                    ("tours", "Total tours"),
                    ("destinations", "Total destinations"),
                    ("travelers", "Total travelers"),
                    ("satisfaction", "Customer satisfaction"),
                ],
                default="manual",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="stat",
            name="value",
            field=models.IntegerField(
                help_text="Used for manually maintained stats and as the satisfaction fallback before reviews exist."
            ),
        ),
        migrations.RunPython(configure_site_stats, migrations.RunPython.noop),
    ]
