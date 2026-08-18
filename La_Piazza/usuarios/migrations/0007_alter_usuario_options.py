from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0006_renomear_perfilusuario_para_usuario"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="usuario",
            options={
                "ordering": ["usuario__username"],
                "verbose_name": "usuário",
                "verbose_name_plural": "usuários",
            },
        ),
    ]
