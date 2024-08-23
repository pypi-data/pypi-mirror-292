from typing import Literal, List

from pydantic import BaseModel, Field, PrivateAttr
from typing_extensions import Annotated


class ProjectVersion(BaseModel):
    major               : Annotated[int, Field(description="The major version of the project")]
    minor               : Annotated[int, Field(description="The minor version of the project")]
    build_ground        : Annotated[int, Field(description="The ground number to subtract from the total amount of commits to calculate the build number")]
    _resulting_version  : Annotated[str, PrivateAttr()] = None
    
    @property
    def resulting_version(self):
        return self._resulting_version

    @resulting_version.setter
    def resulting_version(self, value):
        self._resulting_version = value

class ComponentConfig(BaseModel):
    # discriminator used by pydantic to determine the type of the component at deserialization
    type                : Annotated[Literal[None]   , Field(description="The type of the component")] = None
    name                : Annotated[str             , Field(description="The name of the component", pattern="^[a-zA-Z0-9_\-\.]+$")]
    depends_on          : Annotated[List[str]       , Field(default_factory=list, description="The components this component depends on")]
    _parent_project     : Annotated["ProjectConfig" , PrivateAttr()] = None
    _relative_dir       : Annotated[str             , PrivateAttr()] = None

    @property
    def parent_project(self):
        return self._parent_project
    
    @parent_project.setter
    def parent_project(self, value):
        self._parent_project = value
    
    @property
    def relative_dir(self):
        return self._relative_dir
    
    @relative_dir.setter
    def relative_dir(self, value):
        self._relative_dir = value
        
    @property
    def component_root(self):
        return f"{self._parent_project._project_dir}/{self._relative_dir}"


class ProjectConfig(BaseModel):
    tenant              : Annotated[str                       , Field(description="The tenant of the project. Either the tenant ID or the tenant name (i.e. abc.onmicrosoft.com)")]
    version             : Annotated[ProjectVersion            , Field(description="The version of the project")]
    _components         : Annotated[List[ComponentConfig]     , PrivateAttr(default_factory=list)]
    _project_dir        : Annotated[str                       , PrivateAttr()] = None
    _components_by_name : Annotated[dict[str, ComponentConfig], PrivateAttr()] = None


    @property
    def project_dir(self):
        return self._project_dir
    
    @project_dir.setter
    def project_dir(self, value):
        self._project_dir = value
        
    @property
    def components(self):
        return self._components
    
    @components.setter
    def components(self, value):
        self._components = value
        
    @property
    def components_by_name(self):
        if self._components_by_name is None:
            self._components_by_name = {component.name: component for component in self._components}
        return self._components_by_name
    
    def get_components_by_type(self, typ: str):
        return [component for component in self._components if component.type == typ]

    def get_component_by_name(self, name: str):
        component = self.components_by_name.get(name, None)
        if component is None:
            raise ValueError(f"Component '{name}' not found in the project configuration. Available components: {list(self.components_by_name.keys())}")
        return component
