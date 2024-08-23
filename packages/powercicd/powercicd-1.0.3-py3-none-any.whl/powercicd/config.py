import glob
from typing_extensions import Annotated
import yaml
import os
from typing import Any, List, Union
import logging

from pydantic import BaseModel, Discriminator, Field, Tag, root_validator, ValidationError
from typing import List, Union, Type

from powercicd.powerbi.config import PowerBiComponentConfig
from powercicd.powerbi.file_utils import find_parent_dir_where_exists_file
from powercicd.shared.config import ProjectConfig, ComponentConfig
from powercicd.sharepoint.config import SharepointComponentConfig
from powercicd.powerapps.config import PowerAppsComponentConfig


AnyComponent = Union[
    Annotated[PowerBiComponentConfig   , Tag('powerbi'   )],
    Annotated[PowerAppsComponentConfig , Tag('powerapps' )],
    Annotated[SharepointComponentConfig, Tag('sharepoint')],
]


PROJECT_CONFIG_FILENAME_FMT   : str = "power-project-{env}.yaml"
COMPONENT_CONFIG_FILENAME_FMT : str = "power-component-{env}.yaml"


log = logging.getLogger(__name__)


def get_discriminator_value(values: dict):
    """ Custom discriminator function to handle both single and list components dynamically """
    if isinstance(values, list):
        return "listComponent"
    else:
        return values["type"]


class ComponentConfigFileModel(BaseModel):
    component: Annotated[
        Union[
            AnyComponent,
            Annotated[List[AnyComponent], Tag('listComponent')]
        ], 
        Discriminator(get_discriminator_value)
    ]
    @classmethod
    def deserialize_file(cls, component_config_file: Any) -> List[AnyComponent]:
        log.info(f"Reading component config from '{component_config_file}'")
        with open(component_config_file, 'r', encoding='utf-8') as f:
            component_config_json = yaml.safe_load(f)
        containing_config_json = {"component": component_config_json}
        validated_component = cls.model_validate(containing_config_json).component
        if isinstance(component_config_json, list):
            return validated_component
        else:
            return [validated_component]
        

def get_current_version(project_dir: str, project_config: ProjectConfig):
    major_version = project_config.version.major
    minor_version = project_config.version.minor
    build_ground  = project_config.version.build_ground

    # Case 1: project folder is outside git work tree
    cmd = f"git -C {project_dir} rev-parse --is-inside-work-tree"
    log.info(f"Executing command: {cmd}")
    response = os.popen(cmd).read()
    log.info(f"Response: '{response}'")
    if response.strip() != "true":
        log.info(f"Project folder is outside git work tree, then keep version '{major_version}.{minor_version}.{build_ground}' unchanged")
        return f"{major_version}.{minor_version}.{build_ground}"
    
    # Case 2: project folder is inside git work tree but no commits at all (not even HEAD)
    cmd = f"git -C {project_dir} rev-list --all"
    log.info(f"Executing command: {cmd}")
    response = os.popen(cmd).read()
    log.info(f"Response: '{response}'")
    if response.strip() == "":
        log.info(f"No commits found in '{project_dir}', then keep version '{major_version}.{minor_version}.{build_ground}' unchanged")
        return f"{major_version}.{minor_version}.{build_ground}"

    # Case 3: project folder is inside git work tree and there are commits
    cmd = f"git -C {project_dir} rev-list HEAD --count"
    log.info(f"Executing command: {cmd}")
    response = os.popen(cmd).read()
    log.info(f"Response: '{response}'")
    count_commits = int(response.strip())
    build_number = count_commits - build_ground
    
    cmd = f"git -C {project_dir} status --porcelain"
    log.info(f"Executing command: {cmd}")
    response = os.popen(cmd).read()
    log.info(f"Response: '{response}'")
    modified_flag = "M" if response.strip() != "" else ""
    version = f"{major_version}.{minor_version}.{build_number}{modified_flag}"
    log.info(f"Version: {version}")
    return version


def get_project_config(stage: str, lookup_path: str = None) -> ProjectConfig:
    project_config_filename = PROJECT_CONFIG_FILENAME_FMT.format(env=stage)
    component_config_all_stage_filename_blob = COMPONENT_CONFIG_FILENAME_FMT.format(env="*")
    component_config_stage_filename = COMPONENT_CONFIG_FILENAME_FMT.format(env=stage)

    if lookup_path is None:
        lookup_path = os.getcwd()

    # Determine project root and project_config.json
    project_dir = find_parent_dir_where_exists_file(lookup_path, project_config_filename)
    log.info(f"Project root: {project_dir}")

    # Load project_config.json
    with open(os.path.join(project_dir, project_config_filename), 'r', encoding='utf-8') as f:
        project_json_config = yaml.safe_load(f)

    project_config = ProjectConfig(**project_json_config)

    # Enrich project_config
    project_config._project_dir = project_dir
    project_config.version.resulting_version = get_current_version(project_dir, project_config)

    # load component configs
    project_config._components = []
    component_config_files = [f for f in glob.glob(f"{project_dir}/*/{component_config_stage_filename}")]
    for component_config_file in component_config_files:
        # name of parent directory is the name of the component
        component_name = os.path.basename(os.path.dirname(component_config_file))

        log.info(f"Reading component '{component_name}' config from '{component_config_file}'")
        component_config_list = ComponentConfigFileModel.deserialize_file(component_config_file)
        for component_config in component_config_list:
            component_config.parent_project = project_config
            component_config.relative_dir = component_name
            project_config._components.append(component_config)

    return project_config


def get_component_config(stage: str, lookup_path: str = None) -> ComponentConfig:
    project_config_filename = PROJECT_CONFIG_FILENAME_FMT.format(env=stage)
    component_config_filename = COMPONENT_CONFIG_FILENAME_FMT.format(env=stage)

    if lookup_path is None:
        lookup_path = os.getcwd()

    component_dir = find_parent_dir_where_exists_file(lookup_path, component_config_filename)
    project_dir   = os.path.dirname(component_dir)
    # verify if PROJECT_CONFIG_FILENAME exists in the same folder
    if not os.path.exists(f"{project_dir}/{project_config_filename}"):
        raise ValueError(f"{project_config_filename} not found in the folder '{project_dir}' (parent directory of component folder '{component_dir}')")
    name = os.path.relpath(component_dir, project_dir)
    project_config = get_project_config(component_dir)
    return project_config.get_component_by_name(name)
