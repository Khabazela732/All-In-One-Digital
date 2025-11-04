# some_app/management/commands/run_sql_file.py
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from pathlib import Path

class Command(BaseCommand):
    help = "Run a .sql file against the current DB connection"

    def add_arguments(self, parser):
        parser.add_argument("sql_path", type=str)

    def handle(self, *args, **opts):
        path = Path(opts["sql_path"]).expanduser().resolve()
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        sql = path.read_text(encoding="utf-8")

        # SQLite special case: executescript allows multiple statements
        if connection.vendor == "sqlite":
            with connection.cursor() as cursor:
                connection.connection.executescript(sql)
            self.stdout.write(self.style.SUCCESS(f"Executed {path}"))
            return

        # Other backends: split on ';' safely
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        with connection.cursor() as cursor:
            for stmt in statements:
                cursor.execute(stmt)
        self.stdout.write(self.style.SUCCESS(f"Executed {path}"))
