from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


USUARIO_BACKUP = "usuarios_usuario_abstractuser_backup"
GRUPOS_BACKUP = "usuarios_usuario_groups_abstractuser_backup"
PERMISSOES_BACKUP = "usuarios_usuario_user_permissions_abstractuser_backup"


def _table_exists(cursor, table_name):
    cursor.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table' AND name = %s
        """,
        [table_name],
    )
    return cursor.fetchone() is not None


def migrar_para_user_direto(apps, schema_editor):
    connection = schema_editor.connection

    if connection.vendor != "sqlite":
        raise RuntimeError(
            "A migração para User direto foi criada para o SQLite "
            "deste projeto."
        )

    cursor = connection.cursor()

    if not _table_exists(cursor, "usuarios_usuario"):
        return

    if _table_exists(cursor, USUARIO_BACKUP):
        raise RuntimeError(
            f"A tabela de backup {USUARIO_BACKUP} já existe. "
            "Verifique a migração antes de continuar."
        )

    # Copia os dados de autenticação para a tabela oficial do Django,
    # mantendo os mesmos IDs para preservar todas as referências.
    cursor.execute(
        """
        INSERT INTO auth_user (
            id,
            password,
            last_login,
            is_superuser,
            username,
            first_name,
            last_name,
            email,
            is_staff,
            is_active,
            date_joined
        )
        SELECT
            id,
            password,
            last_login,
            is_superuser,
            username,
            first_name,
            last_name,
            email,
            is_staff,
            is_active,
            date_joined
        FROM usuarios_usuario
        """
    )

    # Os campos próprios da pizzaria passam a pertencer a um perfil 1:1.
    cursor.execute(
        """
        CREATE TABLE usuarios_perfilusuario (
            id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            telefone varchar(20) NOT NULL,
            cpf varchar(14) NULL UNIQUE,
            observacoes TEXT NOT NULL,
            criado_em datetime NOT NULL,
            atualizado_em datetime NOT NULL,
            usuario_id bigint NOT NULL UNIQUE
                REFERENCES auth_user (id)
                DEFERRABLE INITIALLY DEFERRED
        )
        """
    )
    cursor.execute(
        """
        INSERT INTO usuarios_perfilusuario (
            id,
            telefone,
            cpf,
            observacoes,
            criado_em,
            atualizado_em,
            usuario_id
        )
        SELECT
            id,
            COALESCE(telefone, ''),
            cpf,
            COALESCE(observacoes, ''),
            criado_em,
            atualizado_em,
            id
        FROM usuarios_usuario
        """
    )

    cursor.execute(
        """
        INSERT INTO auth_user_groups (user_id, group_id)
        SELECT usuario_id, group_id
        FROM usuarios_usuario_groups
        """
    )
    cursor.execute(
        """
        INSERT INTO auth_user_user_permissions (user_id, permission_id)
        SELECT usuario_id, permission_id
        FROM usuarios_usuario_user_permissions
        """
    )

    # Mantém as tabelas antigas como backup e libera seus nomes para que
    # apenas as tabelas oficiais auth_user_* sejam usadas daqui em diante.
    for table_name, backup_name in (
        ("usuarios_usuario_groups", GRUPOS_BACKUP),
        ("usuarios_usuario_user_permissions", PERMISSOES_BACKUP),
        ("usuarios_usuario", USUARIO_BACKUP),
    ):
        if _table_exists(cursor, table_name):
            cursor.execute(
                f'ALTER TABLE "{table_name}" RENAME TO "{backup_name}"'
            )

    # Recria as tabelas que apontavam para usuarios_usuario, agora com
    # uma FK para auth_user. O schema editor preserva colunas, dados,
    # índices e IDs dessas tabelas.
    for app_label, model_name in (
        ("usuarios", "EnderecoUsuario"),
        ("estoque", "MovimentacaoEstoque"),
        ("pedidos", "Pedido"),
        ("admin", "LogEntry"),
    ):
        model = apps.get_model(app_label, model_name)
        if _table_exists(cursor, model._meta.db_table):
            schema_editor._remake_table(model)


def impedir_reversao(apps, schema_editor):
    raise RuntimeError(
        "A migração para User direto não pode ser desfeita automaticamente, "
        "pois os dados foram copiados para as tabelas oficiais do Django."
    )


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0002_migrar_usuario_legado"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    migrar_para_user_direto,
                    impedir_reversao,
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name="PerfilUsuario",
                    fields=[
                        (
                            "id",
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        (
                            "telefone",
                            models.CharField(
                                blank=True,
                                max_length=20,
                                verbose_name="telefone",
                            ),
                        ),
                        (
                            "cpf",
                            models.CharField(
                                blank=True,
                                max_length=14,
                                null=True,
                                unique=True,
                                verbose_name="CPF",
                            ),
                        ),
                        (
                            "observacoes",
                            models.TextField(
                                blank=True,
                                verbose_name="observações",
                            ),
                        ),
                        (
                            "criado_em",
                            models.DateTimeField(
                                auto_now_add=True,
                                verbose_name="criado em",
                            ),
                        ),
                        (
                            "atualizado_em",
                            models.DateTimeField(
                                auto_now=True,
                                verbose_name="atualizado em",
                            ),
                        ),
                        (
                            "usuario",
                            models.OneToOneField(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="perfil",
                                to="auth.user",
                                verbose_name="usuário",
                            ),
                        ),
                    ],
                    options={
                        "verbose_name": "perfil do usuário",
                        "verbose_name_plural": "perfis dos usuários",
                        "ordering": ["usuario__username"],
                    },
                ),
                migrations.DeleteModel(name="Usuario"),
            ],
        ),
    ]
