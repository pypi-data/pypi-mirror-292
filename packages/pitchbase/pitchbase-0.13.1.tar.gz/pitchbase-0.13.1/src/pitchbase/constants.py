import pkg_resources
import os

VERSION = pkg_resources.get_distribution("pitchbase").version

DEFAULT_CONFIG_PATH = f"{os.environ.get('HOME')}/.pitchbase"
DEFAULT_CONFIG_PROFILE = "default"
