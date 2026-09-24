from django.db import migrations, models
import django.db.models.deletion


def seed_locations(apps, schema_editor):
    Region = apps.get_model("api", "RecruitmentRegion")
    Area = apps.get_model("api", "RecruitmentArea")
    Dealer = apps.get_model("api", "Dealer")
    north, _ = Region.objects.get_or_create(name="Miền Bắc", defaults={"slug": "mien-bac", "status": 1})
    south, _ = Region.objects.get_or_create(name="Miền Nam", defaults={"slug": "mien-nam", "status": 1})
    hanoi, _ = Area.objects.get_or_create(region=north, name="Hà Nội", defaults={"slug": "ha-noi", "status": 1})
    hcm, _ = Area.objects.get_or_create(region=south, name="Hồ Chí Minh", defaults={"slug": "ho-chi-minh", "status": 1})
    Dealer.objects.filter(province_city__icontains="Hà Nội").update(area=hanoi)
    Dealer.objects.filter(province_city__icontains="Hồ Chí Minh").update(area=hcm)


class Migration(migrations.Migration):
    dependencies = [("api", "0049_delete_recruitmenttag_and_more")]
    operations = [
        migrations.CreateModel(
            name="RecruitmentRegion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
                ("slug", models.SlugField(max_length=140, unique=True)),
                ("status", models.SmallIntegerField(default=1)),
            ],
            options={"ordering": ("name", "id")},
        ),
        migrations.CreateModel(
            name="RecruitmentArea",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("slug", models.SlugField(max_length=180)),
                ("status", models.SmallIntegerField(default=1)),
                ("region", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="areas", to="api.recruitmentregion")),
            ],
            options={"ordering": ("name", "id"), "constraints": [models.UniqueConstraint(fields=("region", "name"), name="unique_recruitment_area_region_name")]},
        ),
        migrations.AddField(model_name="dealer", name="area", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="business_units", to="api.recruitmentarea")),
        migrations.AddField(model_name="recruitmentjob", name="area", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="recruitment_jobs", to="api.recruitmentarea")),
        migrations.AddField(model_name="recruitmentjob", name="business_unit", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="recruitment_jobs", to="api.dealer")),
        migrations.AddField(model_name="recruitmentjob", name="region", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="recruitment_jobs", to="api.recruitmentregion")),
        migrations.RunPython(seed_locations, migrations.RunPython.noop),
    ]
