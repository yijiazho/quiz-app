"""Command-line interface for managing the application."""
import click
import logging
from app.core.database_config import db_config, DatabaseError
from app.core.migrations import migration_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """QuizForge CLI tool."""
    pass

@cli.command()
def init_db():
    """Initialize the database."""
    try:
        logger.info("Initializing database...")
        migration_manager.apply_migrations()
        logger.info("Database initialized successfully")
    except DatabaseError as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise click.ClickException(str(e))

@cli.command()
def list_migrations():
    """List all migrations and their status."""
    try:
        applied = set(migration_manager.get_applied_migrations())
        for migration in migration_manager._migrations:
            status = "✓" if migration.version in applied else " "
            click.echo(f"[{status}] {migration.version}: {migration.name}")
    except DatabaseError as e:
        logger.error(f"Failed to list migrations: {str(e)}")
        raise click.ClickException(str(e))

@cli.command()
@click.argument('version', type=int)
def rollback(version):
    """Rollback a specific migration."""
    try:
        logger.info(f"Rolling back migration {version}...")
        migration_manager.rollback_migration(version)
        logger.info(f"Migration {version} rolled back successfully")
    except DatabaseError as e:
        logger.error(f"Failed to rollback migration: {str(e)}")
        raise click.ClickException(str(e))

@cli.command()
def check_health():
    """Check database health."""
    try:
        if not db_config.test_connection():
            raise click.ClickException("Database connection failed")
        
        db_info = db_config.get_db_info()
        applied_migrations = migration_manager.get_applied_migrations()
        
        click.echo("Database Health Check:")
        click.echo(f"Status: {'Healthy' if db_info else 'Unhealthy'}")
        click.echo(f"Version: {db_info.get('version', 'Unknown')}")
        click.echo(f"Tables: {db_info.get('table_count', 0)}")
        click.echo(f"Environment: {db_info.get('environment', 'Unknown')}")
        click.echo(f"Applied Migrations: {len(applied_migrations)}/{len(migration_manager._migrations)}")
    except DatabaseError as e:
        logger.error(f"Health check failed: {str(e)}")
        raise click.ClickException(str(e))

if __name__ == '__main__':
    cli() 