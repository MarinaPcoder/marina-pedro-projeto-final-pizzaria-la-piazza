from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0003_usar_user_direto"),
    ]

    operations = [
        migrations.CreateModel(
            name="Usuario",
            fields=[],
            options={
                "verbose_name": "usuário",
                "verbose_name_plural": "usuários",
                "ordering": ["username"],
                "proxy": True,
            },
            bases=("auth.user",),
        ),
    ]
