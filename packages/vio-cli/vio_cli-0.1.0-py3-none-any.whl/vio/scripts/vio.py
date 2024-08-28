import logging

import click

from vio.deployment import Deployment

logging.basicConfig(level=logging.INFO)


@click.group()
def cli():
    pass


@click.command()
@click.argument("theme")
@click.option(
    "--template_dir",
    default=None,
    help="path to the directory containing all the templates.",
)
@click.option(
    "--static_dir",
    default=None,
    help="path to the directory containing all the static files.",
)
@click.option(
    "--custom_css", default=None, help="path to the file containing custom CSS."
)
@click.option(
    "--custom_js", default=None, help="path to the file containing custom JavaScript."
)
@click.option("--api-key", default=None, help="API key of a Vio instance.")
@click.option(
    "--version",
    default=None,
    help="version to be set after a successful deployment of a theme.",
)
def deploy(theme, template_dir, static_dir, custom_css, custom_js, api_key, version):
    """Deploy a theme to a Vio instance."""
    deployment = Deployment(
        theme,
        template_dir=template_dir,
        static_dir=static_dir,
        custom_css=custom_css,
        custom_js=custom_js,
        api_key=api_key,
        version=version,
    )
    deployment.run()


cli.add_command(deploy)


if __name__ == "__main__":
    cli()
