# %%
from enum import Enum
import inspect
import json
import logging
import os
import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel
import typer
from typing_extensions import Annotated
import yaml
import tabulate

import powercicd.powerbi.powerbi_utils as powerbi_utils
from powercicd.config import get_project_config
from powercicd.powerbi.config import PowerBiComponentConfig
from powercicd.powerbi.powerbi_client import PowerBiWebClient
from powercicd.shared.config import ProjectConfig

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class OutputFormat(Enum):
    table: Literal["table"] = "table"
    json : Literal["json" ] = "json"
    yaml : Literal["yaml" ] = "yaml"


DEFAULT_OUTPUT_FMT = "yaml"


main_cli = typer.Typer()
powerbi_cli = typer.Typer()
main_cli.add_typer(powerbi_cli, name="powerbi")


def get_tmp_dir(project_dir, suffix):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    tmp_dir = f"{project_dir}/temp/{timestamp}-{suffix}"
    os.makedirs(tmp_dir, exist_ok=True)
    return tmp_dir


def prepare_output(data, ctx_meta):
    if isinstance(data, list):
        return [prepare_output(d, ctx_meta) for d in data]
    if isinstance(data, dict):
        return {k: prepare_output(v, ctx_meta) for k, v in data.items()}
    elif isinstance(data, BaseModel):
        fields = data.model_dump()
        # add all field values which are annotated by @property too
        getters = { f"({k})": getattr(data, k) for k, member in inspect.getmembers(data.__class__) if isinstance(member, property) and not k.startswith("_") }        
        # avoids recursion in the output: keep only simple types
        getters = {k: v for k, v in getters.items() if isinstance(v, (str, int, float, bool, list, dict))}
        all_relevant_fields = {**fields, **getters}
        return {k: prepare_output(v, ctx_meta) for k, v in all_relevant_fields.items()}
    elif isinstance(data, Enum):
        return data.value
    elif isinstance(data, (datetime, date)):
        return data.isoformat()
    else:
        return data
        

def get_result_echo(result, ctx_meta):
    output_fmt = ctx_meta.get("output_fmt", DEFAULT_OUTPUT_FMT)
    result = prepare_output(result, ctx_meta)
    if output_fmt == "json":
        return json.dumps(result, indent=2)
    elif output_fmt == "yaml":
        return yaml.dump(result, default_flow_style=False)
    else:
        return tabulate.tabulate(result, headers="keys", tablefmt="pretty")
    

def echo_result(result, ctx_meta):
    result_echo = get_result_echo(result, ctx_meta)
    typer.echo(result_echo)
    

@main_cli.callback(no_args_is_help=True)
def shared_to_all_commands(
    ctx: typer.Context,
    stage : Annotated[str, typer.Option(
        show_default=False,
        help="The cloud stage to use. this env designation will be used as suffix to find the project and component configuration files"
    )],
    project_dir : Annotated[str, typer.Option(
        help="The project directory to work on. If not defined, then the current directory is used as lookup start point towards file system root",
        prompt=False
    )] = None,
    output_fmt : Annotated[str, typer.Option(
        help="The output format to use for the command",
        prompt=False,
        envvar="OUTPUT_FMT"
    )] = DEFAULT_OUTPUT_FMT,
):
    ctx.obj = get_project_config(stage, lookup_path=project_dir)
    ctx.ensure_object(ProjectConfig)
    ctx.meta["output_fmt"] = output_fmt


@main_cli.command("list", short_help="List all components")
def list_(
    ctx: typer.Context
):
    project_config: ProjectConfig = ctx.obj
    echo_result(project_config.components, ctx.meta)


# ------------------------------


@powerbi_cli.command("list", short_help="List all powerbi components")
def list_(
    ctx: typer.Context
):
    project_config: ProjectConfig = ctx.obj
    echo_result(project_config.get_components_by_type("powerbi"), ctx.meta)


@powerbi_cli.command(short_help="Login to PowerBI")
def login(
    ctx: typer.Context,
    keep_browser_open: Annotated[bool, typer.Option(
        help="Keep the browser open after deployment (for debugging purposes)",
        prompt=False,
        envvar="KEEP_BROWSER_OPEN"
    )]
):
    project_config: ProjectConfig = ctx.obj
    pbi = PowerBiWebClient(tenant=project_config.tenant, keep_browser_open=keep_browser_open)
    pbi.login_for_selenium()
    pbi.close_browser()


@powerbi_cli.command(short_help="Deploy PowerBI components")
def deploy(
    ctx: typer.Context,
    components: Annotated[list[str], typer.Argument(
        help="The component to deploy"
    )] = None,
    deploy_report: Annotated[bool, typer.Option(
        prompt=False, help="Deploy the report",
    )] = True,
    deploy_app: Annotated[bool, typer.Option(
        prompt=False, help="Deploy the app",
    )] = True,
    keep_browser_open: Annotated[bool, typer.Option(
        help="Keep the browser open after deployment (for debugging purposes)",
        prompt=False, envvar="KEEP_BROWSER_OPEN"
    )] = False
):
    if not deploy_report and not deploy_app:
        log.error("Nothing to deploy: neither report nor app is selected. Exiting...")
        return

    project_config: ProjectConfig = ctx.obj
    tmp_folder = get_tmp_dir(project_config.project_dir, "deploy")

    if components is None:
        component_configs = project_config.get_components_by_type("powerbi")
        components = [c.name for c in component_configs]
        msg = f"Do you want to deploy all powerbi components ({', '.join(components)})? (y/n)"
        if not typer.confirm(msg):
            return
    else:
        component_configs = [project_config.get_component_by_name(component_name) for component_name in components]

    pbi = PowerBiWebClient(tenant=project_config.tenant, keep_browser_open=keep_browser_open)

    # first the app login, because it is definitively the most expensive with the browser, and
    # it ensures that the correct browser is active for the api login, where the user has already logged in
    if deploy_app:
        pbi.login_for_selenium()
    pbi.login_for_powerbi_api()

    if deploy_report:
        component_config: PowerBiComponentConfig
        for component_config in component_configs:
            group = pbi.get_group_by_name(component_config.group_name)
            upload_report_name = f"{component_config.report_name} {project_config.version.resulting_version}"

            src_code_folder = f"{component_config.component_root}/src"
            pbix_filepath = f"{tmp_folder}/{upload_report_name}.pbix"

            dataset_parameters = component_config.dataset_parameters.copy()
            dataset_parameters["DATASET_VERSION"] = project_config.version.resulting_version

            # convert src code to pbix
            powerbi_utils.convert_src_code_to_pbix(
                src_code_folder         = src_code_folder,
                pbix_filepath           = pbix_filepath,
                tmp_folder              = tmp_folder,
                powerapps_id_by_name    = component_config.powerapps_id_by_name,
                page_visibility_actions = component_config.page_visibility_actions,
                version                 = project_config.version.resulting_version,
            )

            # deploy report
            log.info(f"Deploying report '{upload_report_name}' to group '{group['name']}'")
            pbi.deploy_report(
                group_id           = group["id"],
                upload_report_name = upload_report_name,
                final_report_name  = component_config.report_name,
                pbix_file_path     = pbix_filepath,
                dataset_parameters = dataset_parameters,
                refresh_schedule   = component_config.refresh_schedule,
                cleanup_regex      = rf"{re.escape(upload_report_name)}.+"
            )

    if deploy_app:
        group_names = sorted(set(component_config.group_name for component_config in component_configs))
        for group_name in group_names:
            group = pbi.get_group_by_name(group_name)
            log_dir = f"{tmp_folder}/deploy_app/logs"
            os.makedirs(log_dir, exist_ok=True)
            log.info(f"Deploying app for group '{group_name}' (log_dir={log_dir})")
            pbi.deploy_app(group["id"], log_dir=log_dir)
        log.info("All apps deployed")
        pbi.close_browser()


@powerbi_cli.command(short_help="Retrieve PowerBI components from the cloud")
def retrieve(
    ctx: typer.Context,
    components: Annotated[list[str], typer.Argument(
        help="The component(s) to retrieve"
    )] = None,
):
    project_config: ProjectConfig = ctx.obj
    tmp_folder = get_tmp_dir(project_config.project_dir, "retrieve")

    if components is None:
        component_configs = project_config.get_components_by_type("powerbi")
        components = [c.name for c in component_configs]
        msg = f"Do you want to retrieve all powerbi components ({', '.join(components)})? (y/n)"
        if not typer.confirm(msg):
            return
    else:
        component_configs = [project_config.get_component_by_name(component_name) for component_name in components]

    pbi = PowerBiWebClient(tenant=project_config.tenant, keep_browser_open=False)
    pbi.login_for_powerbi_api()

    component_config: PowerBiComponentConfig
    for component_config in component_configs:
        group = pbi.get_group_by_name(component_config.group_name)
        download_report_name = f"{component_config.report_name} - downloaded"
        src_code_folder = f"{component_config.component_root}/src"
        pbix_filepath = f"{tmp_folder}/{download_report_name}.pbix"

        # get report id
        report = pbi.get_report_by_name(group["id"], component_config.report_name)
        
        # retrieve report
        log.info(f"Retrieving report '{download_report_name}' to group '{group['name']}'")
        pbi.retrieve_report(
            group_id      = group["id"],
            report_id     = report["id"],
            pbix_filepath = pbix_filepath,
        )

        # convert pbix to src code
        powerbi_utils.convert_pbix_to_src_code(pbix_filepath, src_code_folder, tmp_folder)


@powerbi_cli.command("import", short_help="Import PowerBI components from pbix file to src code")
def import_from_pbix(
    ctx: typer.Context,
    pbix_file: Annotated[str, typer.Option(...,
        help="The pbix file to import from"
    )],
    component: Annotated[str, typer.Argument(...,
        help="The component to import to"
    )],
):
    project_config   : ProjectConfig = ctx.obj
    component_config = project_config.get_component_by_name(component)
    src_code_folder  = f"{component_config.component_root}/src"
    tmp_folder       = get_tmp_dir(project_config.project_dir, "import_from_pbix")
    powerbi_utils.convert_pbix_to_src_code(pbix_file, src_code_folder, tmp_folder)


@powerbi_cli.command("export", short_help="Export PowerBI components from src code to pbix file")
def export_to_pbix(
    ctx: typer.Context,
    pbix_file: Annotated[str, typer.Option(...,
        help="The pbix file to export to"
    )],
    component: Annotated[str, typer.Argument(...,
        help="The component to import to"
    )],
):
    project_config   : ProjectConfig = ctx.obj
    component_config = project_config.get_component_by_name(component)
    src_code_folder  = f"{component_config.component_root}/src"
    tmp_folder       = get_tmp_dir(project_config.project_dir, "export_to_pbix")

    powerbi_utils.convert_src_code_to_pbix(
        src_code_folder         = src_code_folder,
        pbix_filepath           = pbix_file,
        tmp_folder              = tmp_folder,
        powerapps_id_by_name    = component_config.powerapps_id_by_name,
        page_visibility_actions = component_config.page_visibility_actions,
        version                 = project_config.version.resulting_version
    )


if __name__ == '__main__':
    try:
        main_cli()
    except typer.BadParameter as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)
