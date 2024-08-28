import click
from gish.profiles import add_profile_ssh, check_status, switch_profile_ssh, load_profiles

@click.group()
def cli():
    """CLI to manage GitHub profiles using SSH."""
    pass

@click.command()
@click.argument("name")
@click.argument("email")
def add(name, email):
    """Adds a new GitHub profile with SSH, generating and configuring the key."""
    try:
        add_profile_ssh(name, email)
        click.echo(f"Profile '{name}' added successfully.")
    except ValueError as e:
        click.echo(str(e))

@click.command()
@click.argument("name")
def switch(name):
    """Switches to a specific GitHub profile using SSH."""
    try:
        active = switch_profile_ssh(name)
        click.echo(f"Active profile: {active}")
    except ValueError as e:
        click.echo(str(e))

@click.command()
def list():
    """Lists all GitHub profiles configured with SSH."""
    profiles = load_profiles()
    if not profiles:
        click.echo("No profiles configured.")
        return

    click.echo("Available profiles:")
    for idx, name in enumerate(profiles.keys(), 1):
        click.echo(f"{idx}. {name}")

@click.command()
def status():
    """Checks the status of the GitHub profile configuration and shows which account is active."""
    status_message = check_status()
    click.echo(status_message)

cli.add_command(add)
cli.add_command(switch)
cli.add_command(list)
cli.add_command(status)

if __name__ == "__main__":
    cli()
