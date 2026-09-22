from django.db import connection


COLUMN_TYPES = {
    "CharField": "varchar",
    "SlugField": "varchar",
    "EmailField": "varchar",
    "TextField": "text",
    "IntegerField": "integer",
    "BigIntegerField": "bigint",
    "PositiveIntegerField": "integer",
    "PositiveSmallIntegerField": "smallint",
    "BooleanField": "boolean",
    "DateField": "date",
    "DateTimeField": "timestamp",
    "DecimalField": "decimal",
    "FloatField": "double precision",
    "JSONField": "jsonb",
}

SUPPORTED_TYPES = {"varchar", "text", "integer", "bigint", "smallint", "boolean", "date", "timestamp", "decimal", "double precision", "jsonb"}


def table_names():
    return [name for name in connection.introspection.table_names() if name != "sqlite_sequence"]


def table_schema(table_name):
    if table_name not in table_names():
        return None
    with connection.cursor() as cursor:
        description = connection.introspection.get_table_description(cursor, table_name)
        constraints = connection.introspection.get_constraints(cursor, table_name)
        cursor.execute(
            """
            SELECT column_name, data_type, character_maximum_length, numeric_precision, numeric_scale
            FROM information_schema.columns
            WHERE table_schema = current_schema() AND table_name = %s
            """,
            [table_name],
        )
        database_metadata = {
            row[0]: {
                "db_type": row[1],
                "length": row[2],
                "precision": row[3],
                "scale": row[4],
            }
            for row in cursor.fetchall()
        }
    primary_keys = {name for name, value in constraints.items() if value.get("primary_key") for name in value.get("columns", [])}

    def column_metadata(column):
        field_type = connection.introspection.get_field_type(column.type_code, column)
        db_type = {
            "CharField": "varchar",
            "SlugField": "varchar",
            "EmailField": "varchar",
            "TextField": "text",
            "IntegerField": "integer",
            "BigIntegerField": "bigint",
            "PositiveIntegerField": "integer",
            "PositiveSmallIntegerField": "smallint",
            "BooleanField": "boolean",
            "DateField": "date",
            "DateTimeField": "timestamp",
            "DecimalField": "decimal",
            "FloatField": "double precision",
            "JSONField": "jsonb",
        }.get(field_type, field_type.lower())
        metadata = database_metadata.get(column.name, {})
        length = metadata.get("length")
        precision = metadata.get("precision")
        scale = metadata.get("scale")
        return {
            "name": column.name,
            "type": field_type,
            "db_type": metadata.get("db_type") or db_type,
            "length": length,
            "precision": precision,
            "scale": scale,
            "nullable": column.null_ok,
            "primary_key": column.name in primary_keys,
            "default": column.default,
        }

    return {
        "name": table_name,
        "columns": [column_metadata(column) for column in description],
        "indexes": [
            {"name": name, "columns": value.get("columns", []), "unique": value.get("unique", False)}
            for name, value in constraints.items()
            if value.get("index") or value.get("unique")
        ],
    }


def schema_catalog():
    return [table_schema(name) for name in table_names()]


def validate_name(name):
    if not name or not name.replace("_", "").isalnum() or name[0].isdigit():
        raise ValueError("Names may contain only letters, numbers and underscores.")


def quote(name):
    return connection.ops.quote_name(name)


def add_column(table_name, payload):
    name = payload.get("name", "").strip()
    validate_name(name)
    field_type = payload.get("type", "varchar")
    if field_type not in SUPPORTED_TYPES:
        raise ValueError("Unsupported column type.")
    nullable = bool(payload.get("nullable", True))
    default = payload.get("default")
    default_sql = ""
    params = []
    if default not in (None, ""):
        default_sql = " DEFAULT %s"
        params.append(default)
    if not nullable and default in (None, ""):
        raise ValueError("A new non-nullable column requires a default value.")
    with connection.cursor() as cursor:
        cursor.execute(f"ALTER TABLE {quote(table_name)} ADD COLUMN {quote(name)} {field_type}{' NULL' if nullable else ' NOT NULL'}{default_sql}", params)


def alter_column(table_name, column_name, payload):
    schema = table_schema(table_name)
    if schema is None:
        raise ValueError("Table not found.")
    column = next((item for item in schema["columns"] if item["name"] == column_name), None)
    if column is None:
        raise ValueError("Column not found.")
    if column["primary_key"]:
        raise ValueError("Primary key columns cannot be altered here.")

    field_type = payload.get("type", column["db_type"])
    field_type = {
        "character varying": "varchar",
        "timestamp with time zone": "timestamp",
        "numeric": "decimal",
    }.get(field_type, field_type)
    if field_type not in SUPPORTED_TYPES:
        raise ValueError("Unsupported column type.")

    def positive_integer(value, label, maximum):
        if value in (None, ""):
            return None
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"{label} must be a positive integer.")
        if parsed <= 0 or parsed > maximum:
            raise ValueError(f"{label} is outside the allowed range.")
        return parsed

    length = positive_integer(payload.get("length"), "Length", 10485760) if field_type == "varchar" else None
    precision = positive_integer(payload.get("precision"), "Precision", 1000) if field_type == "decimal" else None
    scale = positive_integer(payload.get("scale"), "Scale", 1000) if field_type == "decimal" else None
    if scale is not None and precision is not None and scale > precision:
        raise ValueError("Scale cannot be greater than precision.")
    type_sql = field_type
    if length is not None:
        type_sql = f"varchar({length})"
    elif precision is not None:
        type_sql = f"decimal({precision}{f',{scale}' if scale is not None else ''})"

    nullable = bool(payload.get("nullable", column["nullable"]))
    statements = [f"ALTER COLUMN {quote(column_name)} TYPE {type_sql} USING {quote(column_name)}::{type_sql}"]
    statements.append(f"ALTER COLUMN {quote(column_name)} {'DROP NOT NULL' if nullable else 'SET NOT NULL'}")
    default = payload.get("default", column["default"])
    if default in (None, ""):
        statements.append(f"ALTER COLUMN {quote(column_name)} DROP DEFAULT")
        params = []
    else:
        statements.append(f"ALTER COLUMN {quote(column_name)} SET DEFAULT {connection.ops.quote_value(str(default))}")
        params = []
    with connection.cursor() as cursor:
        cursor.execute(f"ALTER TABLE {quote(table_name)} {', '.join(statements)}", params)


def rename_column(table_name, old_name, new_name):
    validate_name(new_name)
    schema = table_schema(table_name)
    if schema is None or old_name not in {column["name"] for column in schema["columns"]}:
        raise ValueError("Column not found.")
    with connection.cursor() as cursor:
        cursor.execute(f"ALTER TABLE {quote(table_name)} RENAME COLUMN {quote(old_name)} TO {quote(new_name)}")


def drop_column(table_name, column_name):
    schema = table_schema(table_name)
    if schema is None:
        raise ValueError("Table not found.")
    column = next((column for column in schema["columns"] if column["name"] == column_name), None)
    if column is None:
        raise ValueError("Column not found.")
    if column["primary_key"]:
        raise ValueError("Primary key columns cannot be dropped here.")
    with connection.cursor() as cursor:
        cursor.execute(f"ALTER TABLE {quote(table_name)} DROP COLUMN {quote(column_name)}")
