"""Console script for verification_digit_pty."""

import click


@click.command()
def main() -> None:
    """Main entrypoint."""
    click.echo("verification-digit-pty")
    click.echo("=" * len("verification-digit-pty"))
    click.echo("Library to calculate the verification digit from RUC and cedulas in Panama.")


if __name__ == "__main__":
    main()  # pragma: no cover
