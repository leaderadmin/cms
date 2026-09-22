from django.db import migrations, models


def migrate_article_tags(apps, schema_editor):
    Article = apps.get_model("api", "Article")
    Tag = apps.get_model("api", "Tag")
    for article in Article.objects.all():
        for value in article.tags or []:
            name = str(value).strip()[:80]
            if not name:
                continue
            tag, _ = Tag.objects.get_or_create(name=name, defaults={"slug": name.lower().replace(" ", "-")[:100]})
            article.managed_tags.add(tag)


class Migration(migrations.Migration):
    dependencies = [("api", "0023_menu_menuitem_menu")]

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True)),
                ("slug", models.SlugField(max_length=100, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.AddField(
            model_name="article",
            name="managed_tags",
            field=models.ManyToManyField(blank=True, related_name="articles", to="api.tag"),
        ),
        migrations.RunPython(migrate_article_tags, migrations.RunPython.noop),
    ]