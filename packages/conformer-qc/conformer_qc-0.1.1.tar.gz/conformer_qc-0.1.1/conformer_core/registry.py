#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
"""
We are using TOML files to handle configuration storage between projects

This is code for bootstrapping the applications and handles:
- Collecting database models
- Creating the database
- Loading user settings
- Synchronising settings between apps
"""
import re
from functools import partial
from typing import Any, Dict, List, Set, Tuple, Type, Union

import networkx as nx
import pydantic
import yaml
from yaml import dump as _dump_yaml
from yaml import load as _load_yaml

try:
    from yaml import Dumper as YAMLDumper
    from yaml import Loader as YAMLLoader
except ImportError:
    from yaml import CDumper as YAMLDumper
    from yaml import CLoader as YAMLLoader


from importlib import import_module
from importlib.resources import files

# PyYAML can't handle trailing whitespace (see comments of the github issue)
TR = re.compile(r" +\n")


# This is an ongoing issue. Should be fixed in PyYAML 7: https://github.com/yaml/pyyaml/issues/240
def str_presenter(dumper, data):
    """configures yaml for dumping multiline strings
    Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data"""
    # print(data)
    # print(dumper)
    # import pdb; pdb.set_trace()
    if data.count("\n") > 0:  # check for multiline string
        data = re.sub(
            TR, r"\n", data
        )  # Not "round-trip" save but good enough for our purposes
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(str, str_presenter)
yaml.representer.Representer.add_representer(str, str_presenter)
# yaml.representer.BaseRepresenter.add_representer(str, str_presenter)

load_yaml = partial(_load_yaml, Loader=YAMLLoader)
dump_yaml = partial(_dump_yaml, Dumper=YAMLDumper)

REGISTRY_FILENAME = "registry.yaml"
REQUIRED_FIELDS = ("requires", "database", "stages", "settings")


class ComponentSection(pydantic.BaseModel):
    provides: Set[str] = pydantic.Field(default_factory=set)


class Config(pydantic.BaseModel):
    requires: List[str] = pydantic.Field(default_factory=list)
    database: ComponentSection = pydantic.Field(default_factory=ComponentSection)
    stages: ComponentSection = pydantic.Field(default_factory=ComponentSection)
    settings: Dict["str", Any] = pydantic.Field(default_factory=dict)
    environment_vars: Dict["str", "str"] = pydantic.Field(default_factory=dict)


def load_app(pkg_or_config: Union[str, Dict, Config]):
    if isinstance(pkg_or_config, Config):
        name = "main"
        main = pkg_or_config
    elif isinstance(pkg_or_config, dict):
        name = "main"
        main = Config(**pkg_or_config)
    else:
        name = pkg_or_config
        main = load_registry(pkg_or_config)

    return load_config(name, main)


def load_registry(pkg_name: str, config_stack=None) -> Config:
    main_conf = files(pkg_name).joinpath("registry.yaml")
    if not main_conf.exists():
        raise ValueError(f"Package {pkg_name} does not have a 'registry.yaml' file.")
    # Is this worth getting into the weeds with PyDantic?
    with main_conf.open("r") as f:
        return Config(**load_yaml(f))


def load_config(
    name: str,
    reg: Config,
    deps: nx.DiGraph | None = None,
    configs: Dict[str, Config] | None = None,
) -> None | Config:
    is_root = not deps and not configs

    if deps is None:
        deps = nx.DiGraph()
    if configs is None:
        configs = {name: reg}

    for req in reg.requires:
        if req not in configs:
            configs[req] = load_registry(req)
            deps.add_edge(name, req)
            load_config(req, configs[req], deps=deps, configs=configs)

    # Now update settings
    if is_root:
        load_order = [name] + [v for u, v in nx.bfs_edges(deps, name)]
        agg_config = Config()
        for conf_name in reversed(load_order):
            update_config(configs[conf_name], agg_config)
        if name != "main" and name not in agg_config.requires:
            agg_config.requires.insert(0, name)
        return agg_config


def update_config(reg: Config, accumulator: Config | None = None) -> Config:
    if accumulator is None:
        accumulator = Config()

    for field in reg.model_fields:
        val = getattr(reg, field)
        if isinstance(val, pydantic.BaseModel):
            update_config(val, getattr(accumulator, field))
        elif isinstance(val, (Dict, Set)):
            getattr(accumulator, field).update(val)
        else:
            setattr(accumulator, field, val)
    return accumulator


def load_models(config: Config):
    """Retrieves all PeeWee models specified in the registries"""
    return set(load_classes(config.database.provides).values())


def load_stages(config: Config):
    """Load stages into a dictionary"""
    return load_classes(config.stages.provides)


def load_class(model_str: str) -> Tuple["str", Type]:
    """Loads a single model"""
    module_path, class_name = model_str.rsplit(".", maxsplit=1)
    mod = import_module(module_path)
    return class_name, getattr(mod, class_name)


def load_classes(cls_strs: List[str]) -> Dict["str", Type]:
    classes = {}
    for cls_str in cls_strs:
        n, c = load_class(cls_str)
        classes[n] = c
    return classes
