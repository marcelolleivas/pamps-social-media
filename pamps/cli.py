import typer
import uvicorn
from rich.console import Console
from rich.table import Table
from sqlmodel import Session, select

from .config import settings
from .db import engine
from .models import Post, Social, SQLModel, User

cli = typer.Typer(name="Pamps CLI")


@cli.command()
def run(
    port: int = settings.server.port,
    host: str = settings.server.host,
    log_level: str = settings.server.log_level,
    reload: bool = settings.server.reload,
):  # pragma: no cover
    """Run the API server."""
    uvicorn.run(
        "project_name.app:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=reload,
    )


@cli.command()
def shell():
    """Opens interactive shell"""
    _vars = {
        "settings": settings,
        "engine": engine,
        "select": select,
        "session": Session(engine),
        "User": User,
        "Post": Post,
    }
    typer.echo(f"Auto imports: {list(_vars.keys())}")
    try:
        from IPython import start_ipython

        start_ipython(argv=["--ipython-dir=/tmp", "--no-banner"], user_ns=_vars)
    except ImportError:
        import code

        code.InteractiveConsole(_vars).interact()


@cli.command()
def user_list():
    """Lists all users"""
    table = Table(title="Pamps users")
    fields = ["username", "email"]
    for header in fields:
        table.add_column(header, style="magenta")

    with Session(engine) as session:
        users = session.exec(select(User))
        for user in users:
            table.add_row(user.username, user.email)

    Console().print(table)


@cli.command()
def social_list():
    """Lists all users"""
    table = Table(title="Pamps social")
    fields = ["from_id", "to_id"]
    for header in fields:
        table.add_column(header, style="magenta")

    with Session(engine) as session:
        socials = session.exec(select(Social))
        for social in socials:
            table.add_row(str(social.from_id), str(social.to_id))

    Console().print(table)


@cli.command()
def create_user(email: str, username: str, password: str, user_id=None):
    """Create user"""
    with Session(engine) as session:
        if user_id:
            user = User(id=user_id, email=email, username=username, password=password)
        else:
            user = User(email=email, username=username, password=password)
        session.add(user)
        session.commit()
        session.refresh(user)
        typer.echo(f"created {username} user")
        return user


@cli.command()
def reset_db(
    force: bool = typer.Option(False, "--force", "-f", help="Run with no confirmation")
):
    """Resets the database tables"""
    force = force or typer.confirm("Are you sure?")
    if force:
        SQLModel.metadata.drop_all(engine)
