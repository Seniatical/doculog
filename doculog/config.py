"""
Parse user config
"""
import os
from pip._vendor.tomli import load
from pathlib import Path
from typing import Dict
import logging

from dotenv import load_dotenv

from doculog.requests import validate_key

logger = logging.getLogger(__name__)
ALLOWED_CATEGORY_CONFIGS = (
    "create_section"
)

def set_env_vars(vars):
    for k, v in vars.items():
        os.environ[k] = v


def configure(project_root: Path) -> Dict:
    load_dotenv(project_root / ".env")
    config = parse_config(project_root)
    configure_api(config["local"])

    return config


def configure_api(local):
    if (not local) and (not validate_key()):
        if "DOCUMATIC_API_KEY" in os.environ:
            del os.environ["DOCUMATIC_API_KEY"]

        if "DOCULOG_API_KEY" in os.environ:
            del os.environ["DOCULOG_API_KEY"]


def parse_config(project_root: Path) -> Dict:
    logger.info(f"Reading environment variables from {project_root / '.env.'}")
    load_dotenv(project_root / ".env")

    DEFAULT_VARS = {
        "DOCULOG_PROJECT_NAME": project_root.stem,
        "DOCULOG_RUN_LOCALLY": "false",
    }

    DEFAULT_CONFIG = {
        "changelog_name": "CHANGELOG.md",
        "local": False,
        "categories": dict(),
        "category_options": list(),
    }

    config_file = project_root / "pyproject.toml"

    if not config_file.exists():
        set_env_vars(DEFAULT_VARS)
        return DEFAULT_CONFIG

    with open(config_file) as fp:
        config = load(fp)

    if not "doculog" in config.get("tool", {}):
        set_env_vars(DEFAULT_VARS)
        return DEFAULT_CONFIG

    if "categories" in config["tool"]["doculog"]:
        categories = config["tool"]["doculog"]["categories"]
        for key, value in categories.items():
            if key not in ALLOWED_CATEGORY_CONFIGS:
                DEFAULT_CONFIG["categories"].update({key: value})
            else:
                if value is True:
                    DEFAULT_CONFIG["category_options"].append(key)

    # Environment variables
    project_name = config["tool"]["doculog"].get("project", "")
    local = config["tool"]["doculog"].get("local", False)

    if "DOCUMATIC_API_KEY" not in os.environ and "DOCULOG_API_KEY" not in os.environ:
        logger.warning(
            "Environment variable DOCUMATIC_API_KEY not set. Advanced features disabled."
        )

    if "DOCULOG_API_KEY" in os.environ:
        logger.warn(
            "DOCULOG_API_KEY is deprecated and will be removed in v0.2.0. Use DOCUMATIC_API_KEY environment variable to set your api key instead."
        )

    os.environ["DOCULOG_PROJECT_NAME"] = project_name
    os.environ["DOCULOG_RUN_LOCALLY"] = str(local)

    # Config values
    changelog_name = config["tool"]["doculog"].get("changelog", DEFAULT_CONFIG["changelog_name"])

    if not changelog_name.endswith(".md"):
        changelog_name += ".md"

    DEFAULT_CONFIG["changelog_name"] = changelog_name
    DEFAULT_CONFIG["local"] = local

    return DEFAULT_CONFIG