from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0005_desfazer_usuario_proxy"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="PerfilUsuario",
            new_name="Usuario",
        ),
    ]
