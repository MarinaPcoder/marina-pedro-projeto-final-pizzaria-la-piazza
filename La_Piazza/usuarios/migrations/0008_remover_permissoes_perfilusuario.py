from django.db import migrations


def remover_permissoes_antigas(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    ContentType.objects.filter(
        app_label="usuarios",
        model="perfilusuario",
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0007_alter_usuario_options"),
    ]

    operations = [
        migrations.RunPython(
            remover_permissoes_antigas,
            migrations.RunPython.noop,
        ),
    ]
