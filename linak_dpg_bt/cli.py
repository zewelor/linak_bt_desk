import logging
import click
import re

from desk_position import DeskPosition
from linak_device import LinakDesk

pass_desk = click.make_pass_decorator(LinakDesk)


def validate_mac(ctx, param, mac):
    if re.match('^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', mac) is None:
        raise click.BadParameter(mac + ' is no valid mac address')
    return mac


@click.group(invoke_without_command=True)
@click.option('-b', '--bdaddr', required=True, callback=validate_mac)
@click.option('--debug/--normal', default=False)
@click.pass_context
def cli(ctx, bdaddr, debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    desk = LinakDesk(bdaddr)
    desk.read_dpg_data()
    ctx.obj = desk

    if ctx.invoked_subcommand is None:
        ctx.invoke(state)


@cli.command()
@pass_desk
def name(desk):
    click.echo("Desk name: %s" % desk.name)


@cli.command()
@pass_desk
def get_height(desk):
    click.echo("Desk position: %s" % desk.current_height_with_offset.human_cm)


@cli.command()
@click.option('-t', '--target', required=True, type=click.IntRange(1, 200))
@pass_desk
def move_to(desk, target):
  desk.move_to_cm(target)

@cli.command()
@click.pass_context
def state(ctx):
    """ Prints out all available information. """
    desk = ctx.obj
    click.echo(desk)


if __name__ == "__main__":
    cli()
