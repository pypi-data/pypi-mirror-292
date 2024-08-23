import configparser
import os
import sys
from functools import partial
from typing import Optional

import typer

PROFILE_ID_KEY = "aws_access_key_id"
DEFAULT_PROFILE_KEY = "default"
DEFAULT_PROFILE_NAME = "<no name>"
eprint = partial(print, file=sys.stderr)


def config_path():
    if "AWS_CONFIG_FILE" in os.environ:
        return os.environ["AWS_CONFIG_FILE"]
    return os.path.expanduser("~/.aws/config")

def credentials_path():
    if "AWS_SHARED_CREDENTIALS_FILE" in os.environ:
        return os.environ["AWS_SHARED_CREDENTIALS_FILE"]
    return os.path.expanduser("~/.aws/credentials")

def parse_aws_config(aws_config_file: str):
    aws_config = configparser.ConfigParser()
    if not aws_config.read(aws_config_file):
        raise RuntimeError("AWS config file not found")
    return aws_config

def parse_aws_credentials(aws_credentials_file: str):
    aws_credentials = configparser.ConfigParser()
    if not aws_credentials.read(aws_credentials_file):
        raise RuntimeError("AWS credentials file not found")
    return aws_credentials

def cli_chooser(options, prompt ="Choose one:", current = None, key_getter = lambda c: c, value_getter = None):
    idx_mapping = dict(enumerate(options))
    for i in range(len(options)):
        option = idx_mapping[i]
        eprint(
            f"{"*" if current == key_getter(option) else " "}{i}) "
            f"{value_getter(option) if value_getter is not None else key_getter(option)}"
        )
    while True:
        try:
            eprint()
            eprint(prompt, end=" ")
            choice = int(input())
        except ValueError:
            continue
        if choice not in idx_mapping:
            continue
        break
    # noinspection PyUnboundLocalVariable
    return key_getter(idx_mapping[choice])


def awscli_profile(
    name: Optional[str] = None,
    chooser = cli_chooser,
):
    aws_config = parse_aws_config(config_path())
    aws_credentials = parse_aws_credentials(credentials_path())

    try:
        profile_mapping = {
            aws_credentials[profile][PROFILE_ID_KEY]: profile
            for profile in aws_credentials.sections()
            if profile != DEFAULT_PROFILE_KEY
        }
    except KeyError as e:
        raise RuntimeError("Malformed AWS credentials file") from e

    if "default" in aws_credentials and PROFILE_ID_KEY in aws_credentials[DEFAULT_PROFILE_KEY]:
        current_id = aws_credentials[DEFAULT_PROFILE_KEY][PROFILE_ID_KEY]
    else:
        current_id = None

    if current_id is not None and current_id not in profile_mapping:
        profile_mapping = {
            current_id: DEFAULT_PROFILE_NAME,
            **profile_mapping
        }

    if name is None:
        mapping_list = list(profile_mapping.keys())
        key = chooser(
            mapping_list,
            prompt="Choose profile",
            current=current_id,
            value_getter=lambda k: f"{profile_mapping[k]} - {k}",
        )
        name = profile_mapping[key]
    if name is DEFAULT_PROFILE_NAME:
        name = DEFAULT_PROFILE_KEY
    config_name = f"profile {name}"

    if name not in aws_credentials:
        raise RuntimeError("Profile not found")

    aws_credentials[DEFAULT_PROFILE_KEY] = aws_credentials[name]
    aws_config[DEFAULT_PROFILE_KEY] = aws_config[config_name] if config_name in aws_config else {}

    with open(config_path(), "w") as f:
        aws_config.write(f)
    with open(credentials_path(), "w") as f:
        aws_credentials.write(f)

    eprint(f"Switched to: {name}")


cli = typer.Typer(add_completion=False)

@cli.command()
def awscli_profile_main(
    name: Optional[str] = typer.Argument(None, help="Name of the profile to use")
):
    awscli_profile(name)


def main():
    cli()
