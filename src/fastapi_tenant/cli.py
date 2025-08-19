import os
import shutil
import subprocess

import typer
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url

app = typer.Typer()


def run_alembic(args, env=None, cwd=None):
    env_vars = os.environ.copy()
    if env:
        env_vars.update(env)
    result = subprocess.run(["alembic"] + args, env=env_vars, cwd=cwd)
    if result.returncode != 0:
        raise typer.Exit(result.returncode)


@app.command()
def create_tenant(schema: str):
    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(db_url)
    with engine.connect() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
        conn.commit()
    typer.echo(f"Created schema '{schema}'")


@app.command()
def revision_shared(message: str):
    cmd = ["revision", "--autogenerate", "-m", message]
    run_alembic(cmd, env={"TENANT_SCHEMA": "shared"}, cwd="migrations-org")
    typer.echo("Revision created in migrations-tenant")


@app.command()
def revision(message: str, schema: str):
    cmd = ["revision", "--autogenerate", "-m", message]
    run_alembic(cmd, env={"TENANT_SCHEMA": schema}, cwd="migrations-tenant")
    typer.echo("Revision created in migrations-tenant")


@app.command()
def upgrade_shared():
    typer.echo("Upgrading tenant: shared")
    run_alembic(["upgrade", "head"], env={"TENANT_SCHEMA": "shared"}, cwd="migrations-org")


@app.command()
def upgrade(schema: str):
    typer.echo(f"Upgrading tenant: {schema}")
    run_alembic(["upgrade", "head"], env={"TENANT_SCHEMA": schema}, cwd="migrations-tenant")


@app.command()
def downgrade_shared(
    target: str,
):
    typer.echo(f"Downgrading tenant 'shared' to: {target}")

    if target == "base":
        confirm = typer.confirm("This will remove ALL migrations from tenant 'shared'. Continue?")
        if not confirm:
            typer.echo("Downgrade cancelled")
            raise typer.Exit(0)

    run_alembic(["downgrade", target], env={"TENANT_SCHEMA": "shared"}, cwd="migrations-org")
    typer.echo(f"Tenant 'shared' downgraded to: {target}")


@app.command()
def downgrade(
    schema: str,
    target: str,
):
    typer.echo(f"Downgrading tenant '{schema}' to: {target}")
    if target == "base":
        confirm = typer.confirm(
            f"This will remove ALL migrations from tenant '{schema}'. Continue?"
        )
        if not confirm:
            typer.echo("Downgrade cancelled")
            raise typer.Exit(0)

    run_alembic(["downgrade", target], env={"TENANT_SCHEMA": schema}, cwd="migrations-tenant")
    typer.echo(f"Tenant '{schema}' downgraded to: {target}")


@app.command()
def history_shared():
    typer.echo("Migration history for tenant 'shared':")
    run_alembic(["history"], env={"TENANT_SCHEMA": "shared"}, cwd="migrations-org")


@app.command()
def history(schema: str):
    typer.echo(f"Migration history for tenant '{schema}':")
    run_alembic(["history"], env={"TENANT_SCHEMA": schema}, cwd="migrations-tenant")


@app.command()
def current_shared():
    typer.echo("Current revision for tenant 'shared':")
    run_alembic(["current"], env={"TENANT_SCHEMA": "shared"}, cwd="migrations-org")


@app.command()
def current(schema: str):
    typer.echo(f"Current revision for tenant '{schema}':")
    run_alembic(["current"], env={"TENANT_SCHEMA": schema}, cwd="migrations-tenant")


@app.command()
def reset_db():
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
    for folder in ["migrations-org/versions", "migrations-tenant/versions"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)
    typer.echo("Cleared migration versions")


@app.command()
def clean_schema(schema: str):
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
