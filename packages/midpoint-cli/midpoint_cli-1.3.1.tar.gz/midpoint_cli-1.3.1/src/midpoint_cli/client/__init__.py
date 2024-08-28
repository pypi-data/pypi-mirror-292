import time
from dataclasses import dataclass
from typing import List, Optional, Tuple, Type
from urllib.parse import urljoin
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import requests

from midpoint_cli.client.objects import (namespaces, MidpointObjectList, MidpointTask, MidpointResource,
                                         MidpointConnector, MidpointUser, MidpointOrganization, endpoints)
from midpoint_cli.client.observer import MidpointCommunicationObserver
from midpoint_cli.client.patch import patch_from_file
from midpoint_cli.client.progress import AsciiProgressMonitor
from midpoint_cli.client.session import CustomRetryManager, CustomHTTPAdapter


class MidpointServerError(Exception):
    pass


class MidpointUnsupportedOperation(Exception):
    pass


@dataclass
class MidpointClientConfiguration:
    url: str = "http://localhost:8080/midpoint/"
    username: str = "administrator"
    password: str = "5ecr3t"


class RestApiClient:
    def __init__(self, client_configuration: MidpointClientConfiguration,
                 observer: MidpointCommunicationObserver = None):
        self.configuration = client_configuration

        if observer is None:
            # No-op observer implementation
            observer = MidpointCommunicationObserver()

        session = requests.Session()

        adapter = CustomHTTPAdapter(max_retries=CustomRetryManager(connect=1000, total=1000, observer=observer),
                                    observer=observer)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        self.requests_session = session

    def resolve_rest_type(self, type) -> Optional[str]:
        for end_class, end_rest in endpoints.items():
            if end_class.lower().startswith(type.lower()):
                return end_rest

        raise AttributeError("Can't find REST type for class " + type)

    def get_element(self, element_class: str, element_oid: str) -> Optional[str]:
        rest_type = self.resolve_rest_type(element_class)

        response = self.requests_session.get(
            url=urljoin(self.configuration.url, 'ws/rest/' + rest_type + '/' + element_oid),
            auth=(self.configuration.username, self.configuration.password))

        return response.content.decode()

    def delete(self, element_class: str, element_oid: str) -> str:
        rest_type = self.resolve_rest_type(element_class)

        response = self.requests_session.delete(
            url=urljoin(self.configuration.url, 'ws/rest/' + rest_type + '/' + element_oid),
            auth=(self.configuration.username, self.configuration.password))

        return response.content.decode()

    def get_elements(self, element_class: str) -> Element:
        rest_type = self.resolve_rest_type(element_class)

        url = urljoin(self.configuration.url, 'ws/rest/' + rest_type)
        response = self.requests_session.get(url=url, auth=(self.configuration.username, self.configuration.password))
        if response.status_code >= 300:
            raise MidpointServerError('Server responded with status code %d on %s' % (response.status_code, url))

        tree = ElementTree.fromstring(response.content)
        return tree

    def execute_action(self, element_class: str, element_oid: str, action: str) -> bytes:
        rest_type = self.resolve_rest_type(element_class)

        response = self.requests_session.post(
            url=urljoin(self.configuration.url, 'ws/rest/' + rest_type + '/' + element_oid + '/' + action),
            auth=(self.configuration.username, self.configuration.password))

        return response.content

    def put_element(self, xml_filename: str, patch_file: str, patch_write: bool) -> Tuple[str, str]:
        tree_root = self._load_xml(xml_filename)

        object_class = tree_root.tag.split('}', 1)[1] if '}' in tree_root.tag else tree_root.tag  # strip namespace

        if object_class == 'objects':
            raise MidpointUnsupportedOperation('Upload of objects collection is not supported through REST API')

        rest_type = self.resolve_rest_type(object_class)
        object_oid = tree_root.attrib['oid']

        with open(xml_filename, 'r') as xml_file:
            xml_body = xml_file.read()

            if patch_file is not None:
                xml_body = patch_from_file(xml_body, patch_file, patch_write)

            target_url = urljoin(self.configuration.url, 'ws/rest/' + rest_type + '/' + object_oid)
            res = self.requests_session.put(
                url=target_url,
                data=xml_body,
                headers={'Content-Type': 'application/xml'},
                auth=(self.configuration.username, self.configuration.password))

            if res.status_code >= 300:
                raise MidpointServerError(f'Error {res.status_code} received from server at {target_url}')

            return object_class, object_oid

    @staticmethod
    def _load_xml(xml_file: str) -> (Element, dict):
        tree_root = ElementTree.parse(xml_file).getroot()
        return tree_root


class TaskExecutionFailure(Exception):
    def __init__(self, message: str):
        super(TaskExecutionFailure).__init__()
        self.message = message

    def __repr__(self):
        return self.message


class MidpointClient:

    def __init__(self, client_configuration: MidpointClientConfiguration = None, api_client: RestApiClient = None,
                 observer: MidpointCommunicationObserver = None):
        if client_configuration is not None:
            self.api_client = RestApiClient(client_configuration, observer=observer)

        if api_client is not None:
            self.api_client = api_client

    def __get_object(self, midpoint_type: str, oid: str) -> Element:
        response = self.api_client.get_element(midpoint_type, oid)
        tree = ElementTree.fromstring(response)

        status = tree.find('c:status', namespaces)

        if status is not None and status.text == 'fatal_error':
            message = tree.find('c:partialResults/c:message', namespaces).text
            raise MidpointServerError(message)

        return tree

    def __get_collection(self, mp_class: str, local_class: Type) -> MidpointObjectList:
        tree = self.api_client.get_elements(mp_class)
        return MidpointObjectList([local_class(entity) for entity in tree])

    def get_tasks(self) -> MidpointObjectList:
        return self.__get_collection('task', MidpointTask)

    def get_resources(self) -> MidpointObjectList:
        return self.__get_collection('resource', MidpointResource)

    def get_connectors(self) -> MidpointObjectList:
        return self.__get_collection('connector', MidpointConnector)

    def get_user(self, oid: str) -> Optional[MidpointUser]:
        user_root = self.__get_object('user', oid)
        user = MidpointUser(user_root)
        return user

    def get_users(self) -> MidpointObjectList:
        return self.__get_collection('user', MidpointUser)

    def get_orgs(self) -> MidpointObjectList:
        return self.__get_collection('org', MidpointOrganization)

    def search_orgs(self, queryterms: List[str]) -> MidpointObjectList:
        orgs = self.get_orgs()
        selected_orgs = self._filter(queryterms, orgs)
        return selected_orgs

    def task_action(self, task_oid: str, task_action: str) -> Optional[MidpointTask]:
        self.api_client.execute_action('task', task_oid, task_action)

        if task_action == 'run':
            return self.task_wait(task_oid)

    def task_wait(self, task_oid: str) -> MidpointTask:
        with AsciiProgressMonitor() as progress:
            while True:
                time.sleep(2)
                task_root = self.__get_object('task', task_oid)
                task = MidpointTask(task_root)

                progress.update(int(task['Progress'] or '0'))

                rstatus = task['Result Status']

                if rstatus != 'in_progress':
                    print()
                    if rstatus != 'success':
                        raise TaskExecutionFailure('Failed execution of task ' + task_oid + ' with status ' + rstatus)

                    return task

    def test_resource(self, resource_oid: str) -> None:
        response = self.api_client.execute_action('resource', resource_oid, 'test')
        tree = ElementTree.fromstring(response)
        status = tree.find('c:status', namespaces).text
        return status

    def get_xml(self, midpoint_type: str, oid: str) -> Optional[str]:
        return self.api_client.get_element(midpoint_type, oid)

    def put_xml(self, xml_file: str, patch_file: str = None, patch_write: bool = False) -> Tuple[str, str]:
        return self.api_client.put_element(xml_file, patch_file, patch_write)

    def delete(self, midpoint_type: str, oid: str) -> str:
        return self.api_client.delete(midpoint_type, oid)
