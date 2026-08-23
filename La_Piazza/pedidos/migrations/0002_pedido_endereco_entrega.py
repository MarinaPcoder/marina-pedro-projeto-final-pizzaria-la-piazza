import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pedidos", "0001_initial"),
        ("usuarios", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="pedido",
            name="endereco_entrega",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="pedidos",
                to="usuarios.enderecousuario",
                verbose_name="endereço de entrega",
            ),
        ),
    ]
