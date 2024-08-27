import json
import os
import sys

import click

from . import constants
from .auth import Auth
from .client import Client


class Mash(object):
    pass


@click.group(invoke_without_command=True)
@click.option("--debug/--no-debug", default=False, help="enable debug logging")
@click.option(
    "--config", "-c", default=constants.DEFAULT_CONFIG_PATH, help="config path"
)
@click.option(
    "--profile", "-p", default=constants.DEFAULT_CONFIG_PROFILE, help="config path"
)
@click.option(
    "--version/--no-version", "-v", default=False, help="show version. (default: False)"
)
@click.pass_context
def cli(ctx, debug, config, profile, version):
    ctx.obj = Mash()
    auth = Auth(
        config_path=config,
        config_profile=profile,
    )
    ctx.obj.api = Client(auth=auth)
    if version:
        print(constants.VERSION)
        sys.exit()

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command(help="get access token")
@click.pass_context
def token(ctx):
    token = ctx.obj.api.auth.get_access_token()
    print(token)


@cli.command(help="Get game-schedule and output json.")
@click.option("--filter", help="filter param")
@click.pass_context
def game_schedule(ctx, filter):
    game_schedule = ctx.obj.api.get_game_schedule(filter)
    print(json.dumps(game_schedule))


@cli.command(help="Get pitch data and output json.")
@click.option("--filter", help="filter param")
@click.option("--limit", type=int, help="limit param")
@click.pass_context
def pitch_data(ctx, filter, limit):
    pitch_data = ctx.obj.api.get_pitch_data(filter, limit)
    print(json.dumps(pitch_data))


@cli.command(help="Get movie-angle-upload and output json.")
@click.option("--filter", help="filter param")
@click.option("--limit", type=int, help="limit param")
@click.pass_context
def movie_angle_upload(ctx, filter, limit):
    result = ctx.obj.api.get_movie_angle_upload(filter, limit)
    print(json.dumps(result))


@cli.command(help="Get movie-angle and output json.")
@click.option("--filter", help="filter param")
@click.pass_context
def movie_angle(ctx, filter):
    result = ctx.obj.api.get_movie_angle(filter)
    print(json.dumps(result))


@cli.command(help="download file by url.")
@click.option("--url", required=True, help="pitchbase file download url.")
@click.option("--download_dir", required=True, help="download directory.")
@click.pass_context
def download(ctx, url, download_dir):
    ctx.obj.api.download(f"{download_dir}/{os.path.basename(url)}", url)


@cli.command(help="download movie from movie-angle.")
@click.option("--filter", help="filter param")
@click.option("--download_dir", required=True, help="download directory.")
@click.pass_context
def download_movie_angle_upload_movie_file_path(ctx, filter, download_dir):
    ctx.obj.api.download_movie_angle_upload_movie_file_path(filter, download_dir)


@cli.command(help="download play-list-file from pitch-data.")
@click.option("--filter", help="filter param")
@click.option("--download_dir", required=True, help="download directory.")
@click.pass_context
def download_pitch_data_playlist_file_path(ctx, filter, download_dir):
    ctx.obj.api.download_pitch_data_playlist_file_path(filter, download_dir)


@cli.command(help="download ts files from m3u8.")
@click.option("--m3u8_url", required=True, help="m3u8 url on pitchbase.")
@click.option("--download_dir", required=True, help="download directory.")
@click.pass_context
def download_ts_from_m3u8(ctx, m3u8_url, download_dir):
    ctx.obj.api.download_ts_from_m3u8(m3u8_url, download_dir)


@cli.command(help="Get player-master and output json.")
@click.option("--filter", help="filter param")
@click.pass_context
def player_master(ctx, filter):
    result = ctx.obj.api.get_player_master(filter)
    print(json.dumps(result))


@cli.command(help="Get team-master and output json.")
@click.option("--filter", help="filter param")
@click.pass_context
def team_master(ctx, filter):
    result = ctx.obj.api.get_team_master(filter)
    print(json.dumps(result))


@cli.command(help="Get umpire-master and output json.")
@click.option("--filter", help="filter param")
@click.option("--limit", type=int, help="limit param")
@click.pass_context
def umpire_master(ctx, filter, limit):
    result = ctx.obj.api.get_umpire_master(filter, limit)
    print(json.dumps(result))


@cli.command(help="Get stadium-master and output json.")
@click.option("--filter", help="filter param")
@click.option("--limit", type=int, help="limit param")
@click.pass_context
def stadium_master(ctx, filter, limit):
    result = ctx.obj.api.get_stadium_master(filter, limit)
    print(json.dumps(result))


@cli.command(help="Get trackman_record and output json.")
@click.option("--filter", help="filter param")
@click.option("--limit", type=int, help="limit param")
@click.pass_context
def trackman_record(ctx, filter, limit):
    result = ctx.obj.api.get_trackman_record(filter, limit)
    print(json.dumps(result))


@cli.command(help="Get charlyze_record and output json.")
@click.option("--resource-name", "-r", help="resource name")
@click.option("--filter", help="filter param")
@click.pass_context
def charlyze_record(ctx, resource_name, filter):
    result = ctx.obj.api.get_charlyze_record(resource_name, filter)
    print(json.dumps(result))


@cli.command(help="Get event_info and output json.")
@click.option("--filter", help="filter param")
@click.option("--limit", type=int, help="limit param")
@click.pass_context
def event_info(ctx, filter, limit):
    result = ctx.obj.api.get_event_info(filter, limit)
    print(json.dumps(result))


@cli.command(help="Get batter_record and output json.")
@click.option("--filter", help="filter param")
@click.option("--limit", type=int, help="limit param")
@click.pass_context
def batter_record(ctx, filter, limit):
    result = ctx.obj.api.get_batter_record(filter, limit)
    print(json.dumps(result))


def main():
    cli(obj={})
