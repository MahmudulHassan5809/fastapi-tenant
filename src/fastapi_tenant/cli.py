import os
import shutil
import subprocess

import typer
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url

app = typer.Typer()
MIGRATIONS_DIR = "migrations"


def run_alembic(args, env=None):
    env_vars = os.environ.copy()
    if env:
        env_vars.update(env)
    result = subprocess.run(["alembic"] + args, env=env_vars, cwd=MIGRATIONS_DIR)
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
    typer.echo(f"Created schema '{schema}'")


@app.command()
def revision(message: str, schema: str = "shared", branch: str = None):
    cmd = ["revision", "--autogenerate", "-m", message]
    # if branch:
    #     cmd.append(f"--branch-label={branch}")
    run_alembic(cmd, env={"TENANT_SCHEMA": schema, "ALEMBIC_BRANCH": branch})
    typer.echo(f"Revision created for schema '{schema}' with branch '{branch}'")


@app.command()
def upgrade(schema: str = "shared", branch: str = None):
    typer.echo(f"Upgrading schema: {schema} (branch: {branch})")
    env = {"TENANT_SCHEMA": schema}
    if branch:
        env["ALEMBIC_BRANCH"] = branch
    run_alembic(["upgrade", "head"], env=env)


@app.command()
def downgrade(schema: str = "shared", target: str = "base", branch: str = None):
    typer.echo(f"Downgrading schema '{schema}' to: {target} (branch: {branch})")
    if target == "base":
        confirm = typer.confirm(
            f"This will remove ALL migrations from schema '{schema}'. Continue?"
        )
        if not confirm:
            typer.echo("Downgrade cancelled")
            raise typer.Exit(0)
    env = {"TENANT_SCHEMA": schema}
    if branch:
        env["ALEMBIC_BRANCH"] = branch
    run_alembic(["downgrade", target], env=env)


@app.command()
def history(schema: str = "shared", branch: str = None):
    typer.echo(f"Migration history for schema '{schema}' (branch: {branch}):")
    env = {"TENANT_SCHEMA": schema}
    cmd = ["history"]
    if branch:
        env["ALEMBIC_BRANCH"] = branch
    run_alembic(cmd, env=env)


@app.command()
def current(schema: str = "shared", branch: str = None):
    typer.echo(f"Current revision for schema '{schema}' (branch: {branch}):")
    env = {"TENANT_SCHEMA": schema}
    cmd = ["current"]
    if branch:
        env["ALEMBIC_BRANCH"] = branch
    run_alembic(cmd, env=env)


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
    typer.echo(f"Reset database '{db_name}'")


@app.command()
def reset_migrations():
    """Clear all migration version files."""
    folder = os.path.join(MIGRATIONS_DIR, "versions")
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)
    typer.echo("Cleared migration versions")


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
    typer.echo(f"All tables in schema '{schema}' have been truncated")


if __name__ == "__main__":
    app()
