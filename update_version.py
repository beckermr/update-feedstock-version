import contextlib
import logging
import os
import pprint
import subprocess
import sys
from pathlib import Path

LOGGER = logging.getLogger(__name__)
LOG_LINES_FOLDED = False


@contextlib.contextmanager
def fold_log_lines(title):
    global LOG_LINES_FOLDED
    try:
        sys.stdout.flush()
        sys.stderr.flush()
        if os.environ.get("GITHUB_ACTIONS", "false") == "true" and not LOG_LINES_FOLDED:
            LOG_LINES_FOLDED = True
            print(f"::group::{title}", flush=True)
        else:
            print("=" * 80, flush=True)
            print("=" * 80, flush=True)
            print("> " + title, flush=True)
        sys.stdout.flush()
        sys.stderr.flush()
        yield
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        if os.environ.get("GITHUB_ACTIONS", "false") == "true":
            LOG_LINES_FOLDED = False
            print("::endgroup::", flush=True)
            sys.stdout.flush()
            sys.stderr.flush()


def main(feedstock_name, new_version):
    # these imports are guarded here in this function since the
    # conda_forge_tick package will hide sensitive env vars
    import conda_forge_tick.update_recipe
    from conda_forge_feedstock_ops.rerender import rerender as cf_feedstock_ops_rerender
    from conda_forge_tick.feedstock_parser import load_feedstock
    from conda_forge_tick.update_recipe import v1_recipe
    from conda_forge_tick.update_recipe.version import update_version_feedstock_dir
    from conda_forge_tick.utils import setup_logging

    # TODO: remove once bug is fixed upstream
    # https://github.com/conda-forge/conda-forge-bot/pull/6661
    os.environ["CF_FEEDSTOCK_OPS_IN_CONTAINER"] = "true"

    setup_logging()

    with fold_log_lines("computing feedstock attributes"):
        name = feedstock_name.rsplit("-", 1)[0]
        LOGGER.info("using feedstock name %s", name)

        try:
            LOGGER.info("computing feedstock attributes")
            attrs = load_feedstock(name, {}, use_container=False)
            LOGGER.info("feedstock attrs:\n%s\n", pprint.pformat(attrs))
        except Exception:
            LOGGER.exception("error while computing feedstock attributes!")
            sys.exit(1)

    with fold_log_lines(
        f"updating version {attrs.get('version', 'null')} -> {new_version}"
    ):
        try:
            LOGGER.info(
                "updating version %s -> %s",
                attrs.get("version", "null"),
                new_version,
            )
            updated, errors = update_version_feedstock_dir(
                feedstock_name,
                str(new_version),
                use_container=False,
            )
            if errors or (not updated):
                raise RuntimeError(f"Error updating the recipe version:\n{errors!r}")
        except Exception:
            LOGGER.exception("error while updating the recipe version!")
            sys.exit(1)

    with fold_log_lines("resetting the build number"):
        try:
            LOGGER.info(
                "resetting the build number",
            )
            workdir = Path(feedstock_name)
            meta_yaml_path = workdir.joinpath("recipe", "meta.yaml")
            recipe_yaml_path = workdir.joinpath("recipe", "recipe.yaml")
            if meta_yaml_path.exists():
                new_meta_yaml = meta_yaml_path.read_text()
                new_meta_yaml = conda_forge_tick.update_recipe.update_build_number(
                    new_meta_yaml,
                    0,
                )
                meta_yaml_path.write_text(new_meta_yaml)
            elif recipe_yaml_path.exists():
                new_recipe_yaml = v1_recipe.update_build_number(
                    recipe_yaml_path,
                    0,
                )
                recipe_yaml_path.write_text(new_recipe_yaml)
            else:
                raise FileNotFoundError("Could not find meta.yaml or recipe.yaml!")
        except Exception:
            LOGGER.exception("error while resetting the recipe build number!")
            sys.exit(1)

    with fold_log_lines("rerendering the feedstock"):
        try:
            LOGGER.info(
                "rerendering",
            )
            msg = cf_feedstock_ops_rerender(
                feedstock_name,
                timeout=None,
                use_container=False,
            )
            if msg is not None:
                msg = (
                    "chore: update version to {new_version} & " + msg[len("chore: ") :]
                )
            subprocess.run(
                f'echo "commit-message={msg}" >> "$GITHUB_OUTPUT"',
                shell=True,
                check=True,
            )

        except Exception:
            LOGGER.exception("error while rerendering!")
            sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
