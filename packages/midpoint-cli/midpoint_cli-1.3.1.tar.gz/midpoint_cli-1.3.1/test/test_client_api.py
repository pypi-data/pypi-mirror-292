import unittest

from midpoint_cli.client import RestApiClient, MidpointClient, MidpointClientConfiguration

test_configuration = MidpointClientConfiguration(
    url='cli-url',
    username='cli-usr',
    password='cli-pwd'
)


class ClientApiTest(unittest.TestCase):
    def test_url_sanitization(self):
        client = RestApiClient(test_configuration)
        self.assertEqual(client.configuration, test_configuration)

    def test_rest_types(self):
        client = RestApiClient(test_configuration)
        self.assertEqual(client.resolve_rest_type('task'), 'tasks')

        try:
            client.resolve_rest_type('bogus')
            self.fail()
        except AttributeError:
            pass

    def test_client_from_namespace(self):
        client = MidpointClient(test_configuration)
        self.assertEqual(test_configuration, client.api_client.configuration)

    def test_client_from_object(self):
        api_client = RestApiClient(test_configuration)
        client = MidpointClient(api_client=api_client)
        self.assertEqual(api_client, client.api_client)

    def test_client_from_priority(self):
        api_client = RestApiClient(test_configuration)
        client = MidpointClient(api_client=api_client, client_configuration=test_configuration)
        self.assertEqual(api_client, client.api_client)


if __name__ == '__main__':
    unittest.main()
