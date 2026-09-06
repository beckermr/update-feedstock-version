import logging
import subprocess
import sys
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def main(task, feedstock_name, new_version):
    # these imports are guarded here in this function since the
    # conda_forge_tick package will hide sensitive env vars
    import conda_forge_tick.update_recipe
    from conda_forge_feedstock_ops.rerender import rerender as cf_feedstock_ops_rerender
    from conda_forge_tick.update_recipe import v1_recipe
    from conda_forge_tick.update_recipe.version import update_version_feedstock_dir
    from conda_forge_tick.utils import setup_logging

    setup_logging()

    if task == "update-version":
        try:
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

        try:
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

    elif task == "rerender":
        try:
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
    else:
        raise RuntimeError(f"Task {task} not recognized!")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
