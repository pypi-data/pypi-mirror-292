import json
from pathlib import Path
import re
import shlex
import subprocess
from typing import List, Optional

import click

from hashboard.utils.hbproject import DBT_ROOT_KEY, read_hashboard_project_value


def _get_selected_model_info(
    dbt_root, dbt_select_string: Optional[str], dbt_state: Optional[str]
) -> List[dict]:
    ls_options = " --resource-type model"
    if dbt_select_string:
        ls_options += f" --select {dbt_select_string}"
        if dbt_state:
            ls_options += f" --state {dbt_state}"

    click.echo("Running `dbt ls` to identify selected dbt models")

    ls_command = f"dbt ls{ls_options} --output json --output-keys 'unique_id name'"

    ls_out = _run_dbt_command(ls_command, dbt_root)

    inclusion_list = []
    for line in ls_out.split("\n"):
        try:
            # Remove anything before the start of a potential json object
            cleaned_output = re.sub(r"^.*?(?=\{)", "", line)
            model_info = json.loads(cleaned_output)
            inclusion_list.append(model_info)
        except:
            # Ignore non-json lines
            pass
    return inclusion_list


def _get_compiled_schema_mapping(
    dbt_root,
    model_names_and_ids: List[dict],
    force_prod: bool,
    dbt_state: Optional[str],
) -> Optional[dict]:
    compile_query = (
        "$$$"
        + "\n".join(
            [
                f'{m["unique_id"]}:{{{{ ref("{m["name"]}") }}}}'
                for m in model_names_and_ids
            ]
        )
        + "$$$"
    )

    compile_options = ""
    if force_prod:
        compile_options = f" --favor-state"
    if dbt_state:
        compile_options += f" --state {dbt_state} --defer"

    click.echo("Running `dbt compile` to identify selected schemas")

    compile_command = f"dbt compile --inline '{compile_query}'{compile_options}"

    stdout = _run_dbt_command(compile_command, dbt_root)

    # Parses substring that matches this pattern: ###model_id:`db`.`schema`.`name`\nmodel_id2:`db`.`schema`.`name`###
    pattern = r"\${3}(.*?)\${3}"
    match = re.search(pattern, stdout, re.DOTALL)

    if match:
        extracted_text = match.group(1).strip()
        lines = extracted_text.split("\n")
        result = {
            key: value.replace("`", "").split(".")[-2]
            for line in lines
            for key, value in [line.split(":")]
            if ":" in line
        }
        return result
    else:
        return None


def _run_dbt_command(invocation_string: str, dbt_root: str):
    process = subprocess.Popen(
        shlex.split(invocation_string),
        cwd=dbt_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, _ = process.communicate()
    ret_code = process.wait()

    if ret_code != 0:
        raise click.ClickException(f"dbt returned nonzero exit code ({ret_code})")

    return stdout


def _validate_manifest_path(target_dir: Path) -> Path:
    manifest_path = target_dir / "manifest.json"
    if not manifest_path.is_file():
        raise click.ClickException(
            f"⚠️ manifest file does not exist in target directory {target_dir}."
        )

    click.echo()
    click.echo(f"✅ Using dbt artifacts at {target_dir}\n")

    return manifest_path


def handle_dbt_args(
    dbt_artifacts_path: Optional[str],
    skip_dbt: bool,
    dbt_select_string: Optional[str],
    dbt_state: Optional[str],
    dbt_force_prod: bool,
):
    """Convenience wrapper for running `dbt parse` before `hb preview` or `hb deploy`.
    Must be run from your Hashboard project directory.
    """

    # Find dbt root
    dbt_root = read_hashboard_project_value(DBT_ROOT_KEY)
    # If explicit or implicit skip return early
    if skip_dbt or (dbt_root is None and dbt_artifacts_path is None):
        return None, None

    # Get provided manifest path or run parse at dbt root
    if dbt_artifacts_path is not None:
        # TODO: Fix this path because we shouldn't be running compile logic here
        # user specified --dbt-manifest explicitly
        target_dir = Path(dbt_artifacts_path)

        return _validate_manifest_path(target_dir), None

    # Using dbt root allows more complex operations
    target_dir = Path(dbt_root) / "target"

    click.echo("🐇 Running `dbt parse` to generate a manifest file.")

    _run_dbt_command("dbt parse", dbt_root)

    manifest_path = _validate_manifest_path(target_dir)

    # Run dbt ls to get list of selected models
    model_names_and_ids = _get_selected_model_info(
        dbt_root, dbt_select_string, dbt_state
    )
    # Compile a dbt-SQL string that references all the models above
    model_schema_info = _get_compiled_schema_mapping(
        dbt_root, model_names_and_ids, dbt_force_prod, dbt_state
    )

    click.echo(f"\n✅ dbt metadata collected successfully.\n")

    return manifest_path, {"dbtCompiledSchemaDict": model_schema_info}
