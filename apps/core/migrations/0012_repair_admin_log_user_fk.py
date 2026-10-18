from django.conf import settings
from django.db import migrations


def repair_admin_log_user_fk(apps, schema_editor):
    """Point Django's admin audit log at the configured custom user table.

    This database was created while Django still used ``auth.User``.  The
    project now uses ``accounts.User``; SQLite keeps the old foreign-key
    target until the table itself is rebuilt.
    """
    connection = schema_editor.connection

    if connection.vendor != "sqlite":
        return

    table = connection.ops.quote_name("django_admin_log")
    user_table = connection.ops.quote_name(
        apps.get_model(settings.AUTH_USER_MODEL.split(".")[0], settings.AUTH_USER_MODEL.split(".")[1])._meta.db_table
    )

    foreign_keys = connection.cursor()
    try:
        foreign_keys.execute("PRAGMA foreign_key_list(django_admin_log)")
        targets = {row[2] for row in foreign_keys.fetchall()}
    finally:
        foreign_keys.close()

    if user_table.strip('"') in targets:
        return

    # The admin log is audit data.  Remove only rows that cannot be retained
    # because their old user no longer exists in the configured user table.
    with connection.cursor() as cursor:
        cursor.execute(
            f"DELETE FROM {table} WHERE user_id NOT IN "
            f"(SELECT id FROM {user_table})"
        )
        cursor.execute(
            """
            CREATE TABLE django_admin_log_new (
                id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                object_id text NULL,
                object_repr varchar(200) NOT NULL,
                action_flag smallint unsigned NOT NULL CHECK (action_flag >= 0),
                change_message text NOT NULL,
                content_type_id integer NULL
                    REFERENCES django_content_type (id)
                    DEFERRABLE INITIALLY DEFERRED,
                user_id integer NOT NULL
                    REFERENCES {user_table} (id)
                    DEFERRABLE INITIALLY DEFERRED,
                action_time datetime NOT NULL
            )
            """.format(user_table=user_table)
        )
        cursor.execute(
            """
            INSERT INTO django_admin_log_new
                (id, object_id, object_repr, action_flag, change_message,
                 content_type_id, user_id, action_time)
            SELECT id, object_id, object_repr, action_flag, change_message,
                   content_type_id, user_id, action_time
            FROM django_admin_log
            """
        )
        cursor.execute("DROP TABLE django_admin_log")
        cursor.execute("ALTER TABLE django_admin_log_new RENAME TO django_admin_log")


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_user_role"),
        ("core", "0011_alter_sitesettings_youtube"),
    ]

    operations = [
        migrations.RunPython(repair_admin_log_user_fk, migrations.RunPython.noop),
    ]
