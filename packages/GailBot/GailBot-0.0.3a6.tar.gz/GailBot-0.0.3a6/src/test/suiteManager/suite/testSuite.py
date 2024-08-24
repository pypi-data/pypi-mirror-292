import os.path
import unittest

from gailbot import FailPluginSuiteRegister
from gailbot.pluginSuiteManager.suite.pluginData import ConfModel
from gailbot.pluginSuiteManager.suite.suite import PluginSuite
from gailbot.shared.utils.general import read_toml
from test.suiteManager import SUITE_TEST_SRC_PATH, SUITE_TEST_WORKSPACE_PATH


class PluginSuiteTest(unittest.TestCase):
    root = SUITE_TEST_SRC_PATH

    def test_create_legal_suite(self):
        conf_model = ConfModel(**read_toml(os.path.join(SUITE_TEST_SRC_PATH, "DummyTestSuite/config.toml")))
        suite = PluginSuite(conf_model, self.root)
        print(suite.required_plugins)
        assert suite.suite_name == "DummyTestSuite"

    def test_fail_due_to_plugin_not_exist(self):
        conf_model = ConfModel(**read_toml(os.path.join(SUITE_TEST_SRC_PATH, "NameNotFound/config.toml")))
        try:
            PluginSuite(conf_model, self.root)
            assert False
        except Exception as e:
            print(e.__class__)
            assert isinstance(e, FailPluginSuiteRegister)

    def test_fail_due_to_unresolved_dependency(self):
        conf_model = ConfModel(**read_toml(os.path.join(SUITE_TEST_SRC_PATH, "UnresolvedDependency/config.toml")))
        try:
            PluginSuite(conf_model, self.root)
            assert False
        except Exception as e:
            print(e.__class__)
            assert isinstance(e, FailPluginSuiteRegister)


if __name__ == '__main__':
    unittest.main()
