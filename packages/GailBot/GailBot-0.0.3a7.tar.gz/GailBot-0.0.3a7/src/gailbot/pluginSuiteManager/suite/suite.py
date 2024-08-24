# -*- coding: utf-8 -*-
# @Author: Vivian Li
# @Date:   2024-01-29 13:26:17
# @Last Modified by:   Vivian Li
# @Last Modified time: 2024-04-06 23:58:52
# @Description: A plugin suite contains multiple plugins. A PluginSuite
# object stores every information about a suite, including the dependencies between
# each plugins, suite metadata , suite documentation path, suite format markdown path.
# When itself is called, it execute procedure to run the suite.
import sys
import os
from typing import Dict, List, Any, Tuple, Optional
from gailbot.shared.exception.serviceException import FailPluginSuiteRegister
from gailbot.pluginSuiteManager.error.errorMessage import SUITE_REGISTER_MSG
from gailbot.pluginSuiteManager.suite.gbPluginMethod import GBPluginMethods
from gailbot.configs import PLUGIN_CONFIG
from gailbot.pluginSuiteManager.suite.pluginData import MetaData, ConfModel
from gailbot.shared.pipeline import (
    Pipeline,
)
from gailbot.shared.utils.general import get_name

import importlib

from gailbot.pluginSuiteManager.suite.pluginComponent import PluginComponent
from gailbot.shared.utils.logger import makelogger

logger = makelogger("plugin suite")


class PluginSuite:
    """
    Manages a suite of plugins and responsible for loading, queries, and
    execution.
    Needs to store the details of each plugin (source file etc.)
    """

    def __init__(self, conf_model: ConfModel, root: str):
        """a dictionary of the dependency map  -> transcriptionPipeline argument"""
        self.suite_name = conf_model.suite_name
        self.conf_model = conf_model
        self.source_path = root
        self.optional_plugins: List[str] = []
        self.required_plugins: List[str] = []
        # metadata and document_path will be loaded in _load_from_config
        self.metadata = conf_model.metadata
        self.document_path = os.path.join(root, self.suite_name, PLUGIN_CONFIG.DOCUMENT)
        self.formatmd_path = os.path.join(root, self.suite_name, PLUGIN_CONFIG.FORMAT)
        self.dependency_map, self.plugins = self._load_from_config(conf_model, root)

        # Add vars here from conf.
        self._is_ready = True
        self.is_official = False

    @property
    def name(self) -> str:
        return self.suite_name

    @property
    def is_ready(self):
        return self._is_ready

    def set_to_official_suite(self):
        """set the plugin to official plugin"""
        self.is_official = True

    def __repr__(self):
        return (
            f"Plugin Suite: {self.name}\n" f"Dependency map: {self.dependency_graph()}"
        )

    def __call__(
        self,
        base_input: Any,
        methods: GBPluginMethods,
        selected_plugins: Optional[Dict[str, List[str]] | List[str]] = None,
    ) -> Dict:
        """
        Apply the specified plugins when possible and return the results
        summary
        """
        if isinstance(selected_plugins, list):
            selected_plugins = self.sub_dependency_graph(selected_plugins)
        elif not selected_plugins:
            selected_plugins = self.dependency_map

        components = {
            k: PluginComponent(self.plugins[k]()) for k in selected_plugins.keys()
        }

        pipeline = Pipeline(
            dependency_map=selected_plugins,
            components=components,
            num_threads=PLUGIN_CONFIG.THREAD_NUM,  # read from config
        )

        result = pipeline(
            base_input=base_input, additional_component_kwargs={"methods": methods}
        )
        return result

    def is_plugin(self, plugin_name: str) -> bool:
        """given a name , return true if the plugin is in the plugin suite"""
        return plugin_name in self.plugins

    def plugin_names(self) -> List[str]:
        """Get names of all plugins"""
        return list(self.plugins.keys())

    def dependency_graph(self) -> Dict:
        """Return the entire dependency graph as a dictionary"""
        return self.dependency_map

    def get_meta_data(self) -> MetaData:
        """get the metadata about this plugin"""
        return self.metadata

    ##########
    # PRIVATE
    ##########
    def _load_from_config(
        self, conf_model: ConfModel, root: str
    ) -> Tuple[Dict[str, List[str]], Dict[str, type]] | None:
        """
        load the plugin suite, the information about each plugin name,
        and its path is stored in the dict_config, all path information
        is relative to the abs_path

        Parameters
        ----------
        conf_model: stores the plugin suite data for suite registration
        root: the path to the root folder of the plugin suite source code

        """
        suite_name = self.suite_name
        dependency_map: Dict[str, List] = dict()
        plugins: Dict[str, type] = dict()
        for conf in conf_model.plugins:
            module_name = get_name(conf.rel_path)
            module_full_name = f"{suite_name}.{module_name}"
            path = os.path.join(root, suite_name, conf.rel_path)
            clazz_name = conf.plugin_name
            try:
                spec = importlib.util.spec_from_file_location(module_full_name, path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_full_name] = module
                spec.loader.exec_module(module)
                clazz = getattr(module, clazz_name)
            except Exception as e:
                logger.error(e, exc_info=True)
                raise FailPluginSuiteRegister(suite_name, str(e))
            dependency_map[clazz_name] = conf.dependencies
            plugins[clazz_name] = clazz
            if conf.hidden:
                self.required_plugins.append(clazz_name)
            else:
                self.optional_plugins.append(clazz_name)
        self.__check_dependency(dependency_map)
        return (
            dependency_map,
            plugins,
        )  # used to generate transcriptionPipeline

    def sub_dependency_graph(
        self, selected: List[str]
    ) -> Optional[Dict[str, List[str]]]:
        """
        given a selected list of plugins, return a subgraph of the dependency graph that
        include only the required plugin and the list of selected plugin

        Parameters
        ----------
        selected

        Returns
        -------

        """
        selected.extend(self.required_plugins)
        selected = set(selected)
        new_dependency = dict()
        for key, dependency in self.dependency_map.items():
            if key in selected:
                new_dependency[key] = list(
                    filter(lambda elt: elt in selected, dependency)
                )
        if not self.__check_dependency(new_dependency):
            logger.error(f"cannot resolve dependency for graph {new_dependency}")
        return new_dependency

    def __check_dependency(self, graph: Dict[Any, List[Any]]):
        """

        Parameters
        ----------
        graph

        Returns None
        -------

        Raises
        -------
        FailPluginSuiteRegister

        """
        visited = {k: 0 for k in graph.keys()}

        def check_circle(node: Any):
            visited[node] = -1
            for dependency in graph[node]:
                if visited[dependency] == -1:
                    raise FailPluginSuiteRegister(
                        self.suite_name,
                        SUITE_REGISTER_MSG.FAIL_LOAD_PLUGIN.format(
                            plugin=node,
                            cause=f" cannot resolve dependency {dependency} for plugin {node}",
                        ),
                    )
                elif visited[dependency] == 0:
                    if check_circle(dependency):
                        raise FailPluginSuiteRegister(
                            self.suite_name,
                            SUITE_REGISTER_MSG.FAIL_LOAD_PLUGIN.format(
                                plugin=node,
                                cause=f" cannot resolve dependency {dependency} for plugin {node}",
                            ),
                        )
            visited[node] = 1

        for node in graph.keys():
            check_circle(node)

        return True
