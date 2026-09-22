from django.db import migrations, models
import django.db.models.deletion


def assign_existing_items_to_main_menu(apps, schema_editor):
    Menu = apps.get_model("api", "Menu")
    MenuItem = apps.get_model("api", "MenuItem")
    menu, _ = Menu.objects.get_or_create(name="Main menu", slug="main")
    MenuItem.objects.filter(menu__isnull=True).update(menu=menu)


def remove_main_menu(apps, schema_editor):
    Menu = apps.get_model("api", "Menu")
    Menu.objects.filter(slug="main").delete()


class Migration(migrations.Migration):
    dependencies = [("api", "0022_page")]

    operations = [
        migrations.CreateModel(
            name="Menu",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("slug", models.SlugField(max_length=120, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ("name", "id")},
        ),
        migrations.AddField(
            model_name="menuitem",
            name="menu",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name="items", to="api.menu"),
        ),
        migrations.RunPython(assign_existing_items_to_main_menu, remove_main_menu),
        migrations.AlterField(
            model_name="menuitem",
            name="menu",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="api.menu"),
        ),
    ]
