import glob
from typing_extensions import Annotated
import yaml
import os
from typing import Any, List, Union
import logging

from pydantic import BaseModel, Discriminator, Field, Tag, root_validator, ValidationError
from typing import List, Union, Type

from powercicd.json_utils import apply_selection_recursively
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


PROJECT_CONFIG_FILENAME   : str = "power-project.yaml"
COMPONENT_CONFIG_FILENAME : str = "power-component.yaml"


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
    def deserialize_file(cls, component_config_file: Any, stage: str) -> List[AnyComponent]:
        log.info(f"Reading component config from '{component_config_file}'")
        with open(component_config_file, 'r', encoding='utf-8') as f:
            components_config_json = list(yaml.safe_load_all(f))
            
        components_config_json = apply_selection_recursively(components_config_json, "~>stage", "~fallback", "~common", stage)
        containing_config_json = {"component": components_config_json}
        validated_component = cls.model_validate(containing_config_json).component
        if isinstance(components_config_json, list):
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


def get_project_config(stage: str, lookup_path: str | None = None) -> ProjectConfig:
    if lookup_path is None:
        lookup_path = os.getcwd()

    # Determine project root and project_config.json
    project_dir = find_parent_dir_where_exists_file(lookup_path, PROJECT_CONFIG_FILENAME)
    log.info(f"Project root: {project_dir}")

    # Load project_config.json
    with open(os.path.join(project_dir, PROJECT_CONFIG_FILENAME), 'r', encoding='utf-8') as f:
        project_json_config = yaml.safe_load(f)

    project_json_config = apply_selection_recursively(project_json_config, "~>stage", "~fallback", "~common", stage)
    
    project_config = ProjectConfig(**project_json_config)

    # Enrich project_config
    project_config._project_dir = project_dir
    project_config.version.resulting_version = get_current_version(project_dir, project_config)

    # load component configs
    project_config._components = []
    component_config_files = [f for f in glob.glob(f"{project_dir}/*/{COMPONENT_CONFIG_FILENAME}")]
    
    if len(component_config_files) == 0:
        raise FileNotFoundError(f"No '{COMPONENT_CONFIG_FILENAME}' files found in '{project_dir}'")
    
    for component_config_file in component_config_files:
        # name of parent directory is the name of the component
        component_name = os.path.basename(os.path.dirname(component_config_file))

        log.info(f"Reading component '{component_name}' config from '{component_config_file}'")
        component_config_list = ComponentConfigFileModel.deserialize_file(component_config_file, stage=stage)
        for component_config in component_config_list:
            component_config.parent_project = project_config
            component_config.relative_dir = component_name
            project_config._components.append(component_config)

    return project_config
