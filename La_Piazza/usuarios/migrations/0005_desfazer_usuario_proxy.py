from django.db import migrations


def remover_permissoes_do_proxy(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    ContentType.objects.filter(
        app_label="usuarios",
        model="usuario",
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0004_usuario_proxy"),
    ]

    operations = [
        migrations.DeleteModel(name="Usuario"),
        migrations.RunPython(
            remover_permissoes_do_proxy,
            migrations.RunPython.noop,
        ),
    ]
