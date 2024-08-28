import unittest
from argparse import Namespace
from configparser import ConfigParser

from midpoint_cli.prompt.configuration import compute_client_configuration
from midpoint_cli.client import MidpointClientConfiguration

CUSTOM_CONFIG = MidpointClientConfiguration(
    url='https://customdomain.com/midpoint/',
    username='custom-user',
    password='custom-password'
)


class EnvironmentTest(unittest.TestCase):

    def test_default_parameters(self):
        ns = Namespace(url=None, username=None, password=None)
        config = ConfigParser()
        env = [None, None, None]

        cfg = compute_client_configuration(ns, config, env)
        self.assertEqual(cfg, MidpointClientConfiguration())

    def test_command_line_parameters(self):
        ns = Namespace(url=CUSTOM_CONFIG.url, username=CUSTOM_CONFIG.username, password=CUSTOM_CONFIG.password)
        config = ConfigParser()
        env = [None, None, None]

        cfg = compute_client_configuration(ns, config, env)
        self.assertEqual(cfg, CUSTOM_CONFIG)

    def test_environment_variables(self):
        ns = Namespace(url=None, username=None, password=None)
        config = ConfigParser()
        env = [CUSTOM_CONFIG.url, CUSTOM_CONFIG.username, CUSTOM_CONFIG.password]

        cfg = compute_client_configuration(ns, config, env)
        self.assertEqual(cfg, CUSTOM_CONFIG)

    def test_configuration_file(self):
        ns = Namespace(url=None, username=None, password=None)
        config = ConfigParser()
        config.read('midpoint-cli.cfg')
        env = [None, None, None]

        cfg = compute_client_configuration(ns, config, env)
        self.assertEqual(cfg.url, config['Midpoint']['url'])
        self.assertEqual(cfg.username, config['Midpoint']['username'])
        self.assertEqual(cfg.password, config['Midpoint']['password'])


if __name__ == '__main__':
    unittest.main()
