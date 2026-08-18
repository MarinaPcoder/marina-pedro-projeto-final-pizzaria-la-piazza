from django.db import migrations


LEGACY_USER_TABLE = "usuarios_usuario_legacy"


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


def _drop_indexes(cursor, table_name):
    cursor.execute(f'PRAGMA index_list("{table_name}")')

    for row in cursor.fetchall():
        index_name = row[1]
        origin = row[3] if len(row) > 3 else None

        if origin != "pk":
            cursor.execute(
                f'DROP INDEX IF EXISTS "{index_name}"'
            )


def migrar_usuario_legado(apps, schema_editor):
    connection = schema_editor.connection

    if connection.vendor != "sqlite":
        raise RuntimeError(
            "A migração do usuário legado foi criada para o "
            "SQLite deste projeto."
        )

    cursor = connection.cursor()

    if not _table_exists(cursor, "usuarios_usuario"):
        return

    cursor.execute('PRAGMA table_info("usuarios_usuario")')
    columns = {row[1] for row in cursor.fetchall()}

    # Bancos novos já possuem a estrutura correta.
    if "id" in columns:
        return

    if "user_ptr_id" not in columns:
        raise RuntimeError(
            "A tabela usuarios_usuario não corresponde nem ao "
            "modelo atual nem ao modelo legado conhecido."
        )

    if _table_exists(cursor, LEGACY_USER_TABLE):
        raise RuntimeError(
            "A tabela de backup usuarios_usuario_legacy já existe. "
            "Verifique a migração antes de continuar."
        )

    # Mantém a tabela antiga intacta como cópia de segurança durante a
    # conversão. O SQLite atualiza as referências dos relacionamentos
    # para o nome temporário, que será corrigido ao recriar cada tabela.
    cursor.execute(
        'ALTER TABLE "usuarios_usuario" '
        'RENAME TO "usuarios_usuario_legacy"'
    )

    usuario_model = apps.get_model("usuarios", "Usuario")
    schema_editor.create_model(usuario_model)

    # Os dados de autenticação estavam em auth_user. Os dados específicos
    # da pizzaria estavam na tabela filha antiga.
    cursor.execute(
        """
        INSERT INTO usuarios_usuario (
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
            date_joined,
            telefone,
            cpf,
            observacoes,
            criado_em,
            atualizado_em
        )
        SELECT
            auth.id,
            auth.password,
            auth.last_login,
            auth.is_superuser,
            auth.username,
            auth.first_name,
            auth.last_name,
            auth.email,
            auth.is_staff,
            auth.is_active,
            auth.date_joined,
            COALESCE(legacy.telefone, ''),
            legacy.cpf,
            COALESCE(legacy.observacoes, ''),
            COALESCE(
                legacy.criado_em,
                auth.date_joined
            ),
            COALESCE(
                legacy.atualizado_em,
                auth.date_joined
            )
        FROM auth_user AS auth
        LEFT JOIN usuarios_usuario_legacy AS legacy
            ON legacy.user_ptr_id = auth.id
        """
    )

    # O modelo atual usa tabelas próprias para grupos e permissões.
    cursor.execute(
        """
        INSERT OR IGNORE INTO usuarios_usuario_groups (
            usuario_id,
            group_id
        )
        SELECT user_id, group_id
        FROM auth_user_groups
        """
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO usuarios_usuario_user_permissions (
            usuario_id,
            permission_id
        )
        SELECT user_id, permission_id
        FROM auth_user_user_permissions
        """
    )

    # Recria as tabelas que apontavam para user_ptr_id. Os dados e IDs
    # são copiados pelo schema editor; somente a referência passa a
    # apontar para usuarios_usuario.id.
    for app_label, model_name in (
        ("usuarios", "EnderecoUsuario"),
        ("estoque", "MovimentacaoEstoque"),
        ("pedidos", "Pedido"),
        ("admin", "LogEntry"),
    ):
        model = apps.get_model(app_label, model_name)
        table_name = model._meta.db_table

        if _table_exists(cursor, table_name):
            _drop_indexes(cursor, table_name)
            schema_editor._remake_table(model)


def impedir_reversao(apps, schema_editor):
    raise RuntimeError(
        "A migração de compatibilidade do usuário não pode ser "
        "desfeita automaticamente, pois a tabela antiga foi mantida "
        "como backup."
    )


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            migrar_usuario_legado,
            impedir_reversao,
        ),
    ]
