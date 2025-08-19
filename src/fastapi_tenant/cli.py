import os
import shutil
import subprocess

import typer
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url

app = typer.Typer()

# Base migrations folder
MIGRATIONS_DIR = "migrations"


def get_migrations_dir(scope: str) -> str:
    """Return the correct migrations folder for the given scope."""
    return os.path.join(MIGRATIONS_DIR, scope)


def run_alembic(args, env=None, scope: str = "shared"):
    env_vars = os.environ.copy()
    if env:
        env_vars.update(env)
    scope_dir = get_migrations_dir(scope)
    alembic_ini = os.path.abspath(os.path.join(scope_dir, "..", "alembic.ini"))
    if not os.path.exists(alembic_ini):
        raise FileNotFoundError(f"No alembic.ini found at {alembic_ini}")
    result = subprocess.run(["alembic", "-c", alembic_ini] + args, env=env_vars)
    if result.returncode != 0:
        raise typer.Exit(result.returncode)


@app.command()
def create_tenant(schema: str):
    """Create a new tenant schema in the database."""
    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(db_url)
    with engine.connect() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
        conn.commit()
    typer.echo(f"✅ Created schema '{schema}'")


@app.command()
def revision(message: str, schema: str = "shared", scope: str = "shared"):
    """Create a new migration revision."""
    # Ensure versions folder exists
    versions_dir = os.path.join(get_migrations_dir(scope), "versions")
    os.makedirs(versions_dir, exist_ok=True)

    cmd = ["revision", "--autogenerate", "-m", message]
    run_alembic(
        cmd,
        env={"TENANT_SCHEMA": schema, "ALEMBIC_SCOPE": scope},
        scope=scope,
    )
    typer.echo(f"✅ Revision created for schema '{schema}' with scope '{scope}'")


@app.command()
def upgrade(schema: str = "shared", scope: str = "shared"):
    """Apply all migrations up to the latest for a schema."""
    typer.echo(f"⏫ Upgrading schema: {schema} (scope: {scope})")
    run_alembic(
        ["upgrade", "head"],
        env={"TENANT_SCHEMA": schema, "ALEMBIC_SCOPE": scope},
        scope=scope,
    )


@app.command()
def downgrade(schema: str = "shared", target: str = "base", scope: str = "shared"):
    """Downgrade schema migrations to a target revision."""
    typer.echo(f"⏬ Downgrading schema '{schema}' to: {target} (scope: {scope})")
    if target == "base":
        confirm = typer.confirm(
            f"This will remove ALL migrations from schema '{schema}'. Continue?"
        )
        if not confirm:
            typer.echo("❌ Downgrade cancelled")
            raise typer.Exit(0)

    run_alembic(
        ["downgrade", target],
        env={"TENANT_SCHEMA": schema, "ALEMBIC_SCOPE": scope},
        scope=scope,
    )


@app.command()
def history(schema: str = "shared", scope: str = "shared"):
    """Show migration history for a schema."""
    typer.echo(f"📜 Migration history for schema '{schema}' (scope: {scope}):")
    run_alembic(
        ["history"],
        env={"TENANT_SCHEMA": schema, "ALEMBIC_SCOPE": scope},
        scope=scope,
    )


@app.command()
def current(schema: str = "shared", scope: str = "shared"):
    """Show current migration for a schema."""
    typer.echo(f"🔖 Current revision for schema '{schema}' (scope: {scope}):")
    run_alembic(
        ["current"],
        env={"TENANT_SCHEMA": schema, "ALEMBIC_SCOPE": scope},
        scope=scope,
    )


@app.command()
def reset_db():
    """Drop and recreate the database."""
    db_url = os.environ["DATABASE_URL"]
    url = make_url(db_url)
    admin_url = url.set(database="postgres")
    db_name = url.database
    engine = create_engine(admin_url)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
        conn.execute(text(f"CREATE DATABASE {db_name}"))
    typer.echo(f"🗑️ Reset database '{db_name}'")


@app.command()
def reset_migrations(scope: str = "shared"):
    """Clear all migration version files for a scope."""
    folder = os.path.join(get_migrations_dir(scope), "versions")
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)
    typer.echo(f"🧹 Cleared migration versions for scope '{scope}'")


@app.command()
def clean_schema(schema: str):
    """Truncate all tables in a schema."""
    db_url = os.environ["DATABASE_URL"]
    url = make_url(db_url)
    engine = create_engine(url)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        result = conn.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = :schema
                AND table_type = 'BASE TABLE';
                """
            ),
            {"schema": schema},
        )
        tables = [row[0] for row in result.fetchall()]
        if not tables:
            typer.echo(f"⚠️  No tables found in schema '{schema}'")
            return
        for table in tables:
            conn.execute(text(f'TRUNCATE TABLE "{schema}"."{table}" CASCADE;'))
    typer.echo(f"✅ All tables in schema '{schema}' have been truncated")


if __name__ == "__main__":
    app()
