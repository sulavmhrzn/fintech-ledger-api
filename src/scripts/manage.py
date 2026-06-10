import asyncio

import typer
from rich import print
from sqlalchemy.future import select

from src.config.database import AsyncSessionLocal
from src.config.security import get_hash
from src.domain.enums import Role
from src.domain.models import User

app = typer.Typer(
    name="Fintech Manage",
    help="CLI management tool for the Fintech Ledger.",
    rich_markup_mode="rich",
)


async def _create_staff_user(email: str, password: str, pin: str, role: Role):
    """The async database logic (Typer commands must be synchronous, so we separate this)."""
    async with AsyncSessionLocal() as session:
        existing_user = await session.execute(select(User).where(User.email == email))
        if existing_user.scalar_one_or_none():
            print(
                f"\n[bold red]✖ Error:[/bold red] User with email [cyan]{email}[/cyan] already exists."
            )
            raise typer.Exit(code=1)

        staff_user = User(
            email=email,
            hashed_password=get_hash(password),
            transaction_pin_hash=get_hash(pin),
            role=role,
            is_active=True,
        )

        session.add(staff_user)
        await session.commit()

        print(
            f"\n[bold green]✔ Success![/bold green] [magenta]{role.value}[/magenta] account for [cyan]{email}[/cyan] created successfully."
        )


@app.command()
def createsuperuser():
    """Interactive CLI to create an ADMIN or COMPLIANCE user."""
    print("\n[bold blue]🚀 Fintech Ledger Staff Provisioning[/bold blue]")
    print("-" * 40)

    email = typer.prompt("📧 Email")

    password = typer.prompt("🔑 Password", hide_input=True, confirmation_prompt=True)
    pin = typer.prompt("🔢 Transaction PIN (4-6 digits)", hide_input=True)

    print("\n[bold yellow]Select Role:[/bold yellow]")
    print("  [1] ADMIN (Full System Access)")
    print("  [2] COMPLIANCE (Wallet Freezing/Auditing)")

    role_choice = typer.prompt("👉 Enter choice", type=int)
    while role_choice not in [1, 2]:
        print("[red]Invalid choice. Please enter 1 or 2.[/red]")
        role_choice = typer.prompt("👉 Enter choice", type=int)

    role = Role.ADMIN if role_choice == 1 else Role.COMPLIANCE

    asyncio.run(_create_staff_user(email, password, pin, role))


@app.command()
def ping():
    """Simple health check to ensure the CLI is working."""
    print("[bold green]Pong![/bold green] CLI is ready to go.")


if __name__ == "__main__":
    app()
