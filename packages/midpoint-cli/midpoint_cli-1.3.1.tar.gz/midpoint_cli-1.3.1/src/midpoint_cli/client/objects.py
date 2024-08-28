import itertools
import re
from collections import OrderedDict
from textwrap import dedent
from typing import Optional, List
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import tabulate
from unidecode import unidecode

namespaces = {
    'c': 'http://midpoint.evolveum.com/xml/ns/public/common/common-3',
}


class MidpointObject(OrderedDict):
    def get_oid(self) -> Optional[str]:
        return self['OID']

    def get_name(self) -> Optional[str]:
        return self['Name']


class MidpointObjectList(List[MidpointObject]):

    def find_object(self, search_reference) -> Optional[MidpointObject]:
        for mp_obj in self:
            if search_reference in [mp_obj.get_oid(), mp_obj.get_name()]:
                return mp_obj

        return None

    def filter(self, queryterms: List[str]):
        selected_users = MidpointObjectList()

        for user in self:
            selected = False

            for uservalue in user.values():
                if uservalue is not None:
                    for term in queryterms:
                        if unidecode(term).casefold() in unidecode(uservalue).casefold():
                            selected = True

            if selected:
                selected_users.append(user)

        return selected_users


class MidpointTask(MidpointObject):

    def __init__(self, xml_entity: Element):
        super().__init__()
        self['OID'] = xml_entity.attrib['oid']
        self['Name'] = xml_entity.find('c:name', namespaces).text

        execution_status_entity = xml_entity.find('c:executionStatus', namespaces)

        # Execution status is renamed executionState since Midpoint 4.4
        if execution_status_entity is None:
            execution_status_entity = xml_entity.find('c:executionState', namespaces)

        self['Execution Status'] = execution_status_entity.text if execution_status_entity is not None else 'n/a'

        # Midpoint before version 4.2

        rs = xml_entity.find('c:resultStatus', namespaces)

        # As of Midpoint 4.2, the result has moved

        if rs is None:
            rs = xml_entity.find('c:operationExecution/c:status', namespaces)

        self['Result Status'] = rs.text if rs is not None else ''
        progress = xml_entity.find('c:progress', namespaces)
        self['Progress'] = progress.text if progress is not None else ''
        total = xml_entity.find('c:expectedTotal', namespaces)
        self['Expected Total'] = total.text if total is not None else ''

        # Collect execution statistics

        self._transitions = []
        self._actions = []

        statistics = xml_entity.find('c:activityState/c:activity/c:statistics', namespaces)

        if statistics is not None:
            synchronization = statistics.find('c:synchronization', namespaces)

            for transition in synchronization or []:
                if transition.find('c:onSynchronizationStart', namespaces) is not None:
                    state_start = transition.find('c:onSynchronizationStart', namespaces).text
                    state_end = transition.find('c:onSynchronizationEnd', namespaces).text
                    count = int(transition.find('c:counter/c:count', namespaces).text)
                    self._transitions.append((state_start, state_end, count))

                if transition.find('c:exclusionReason', namespaces) is not None:
                    reason = transition.find('c:exclusionReason', namespaces).text
                    count = int(transition.find('c:counter/c:count', namespaces).text)
                    self._transitions.append((reason, '', count))

            actions_executed = statistics.find('c:actionsExecuted', namespaces)

            for object_actions_entry in actions_executed or []:
                object_type = object_actions_entry.find('c:objectType', namespaces).text
                operation = object_actions_entry.find('c:operation', namespaces).text
                count_success = int(object_actions_entry.find('c:totalSuccessCount', namespaces).text)
                count_failure = int(object_actions_entry.find('c:totalFailureCount', namespaces).text)

                self._actions.append((object_type, operation, count_success, count_failure))

    def get_transitions(self):
        return self._transitions

    def get_actions(self):
        return self._actions

    def get_full_description(self):
        text = dedent("""\
            {}
            
            Transitions
            {}
                               
            Actions
            {} 
        """).format(tabulate.tabulate(self.items()),
                    tabulate.tabulate(self.get_transitions(),
                                      headers=['From State', 'To State', 'Count']),
                    tabulate.tabulate(self.get_actions(),
                                      headers=['Type', 'Action', 'Count Success', 'Count Failure'])
                    )

        return text


class MidpointResource(MidpointObject):

    def __init__(self, xml_entity: Element):
        super().__init__()
        self['OID'] = xml_entity.attrib['oid']
        self['Name'] = xml_entity.find('c:name', namespaces).text
        self['Availability Status'] = optional_text(
            xml_entity.find('c:operationalState/c:lastAvailabilityStatus', namespaces))
        self['connectorRef'] = xml_entity.find('c:connectorRef', namespaces).attrib['oid']


class MidpointConnector(MidpointObject):

    def __init__(self, xml_entity: Element):
        super().__init__()
        self['OID'] = xml_entity.attrib['oid']
        self['Connector type'] = xml_entity.find('c:connectorType', namespaces).text
        self['Version'] = xml_entity.find('c:connectorVersion', namespaces).text


class MidpointUser(MidpointObject):

    @staticmethod
    def strip_namespace(tag: str) -> str:
        return re.sub(r'{.*}', '', tag)

    def __init__(self, xml_entity: Element):
        super().__init__()
        self['OID'] = xml_entity.attrib['oid']
        self['Name'] = xml_entity.find('c:name', namespaces).text
        self['Title'] = optional_text(xml_entity.find('c:title', namespaces))
        self['FullName'] = optional_text(xml_entity.find('c:fullName', namespaces))
        self['Status'] = xml_entity.find('c:activation/c:effectiveStatus', namespaces).text
        self['EmpNo'] = optional_text(xml_entity.find('c:employeeNumber', namespaces))
        self['Email'] = optional_text(xml_entity.find('c:emailAddress', namespaces))
        self['OU'] = optional_text(xml_entity.find('c:organizationalUnit', namespaces))

        activation = xml_entity.find('c:activation', namespaces)
        extfields = xml_entity.find('c:extension', namespaces)

        self._all_attributes = []

        for child in itertools.chain(xml_entity, activation, extfields or []):
            # Check if the child has no children and contains non-empty text
            if len(child) == 0 and (child.text is not None and child.text.strip()):
                self._all_attributes.append((self.strip_namespace(child.tag), child.text))

    def get_all_attributes(self):
        return self._all_attributes


class MidpointOrganization(MidpointObject):

    def __init__(self, xml_entity: Element):
        super().__init__()
        self['OID'] = xml_entity.attrib['oid']
        self['Name'] = xml_entity.find('c:name', namespaces).text
        self['DisplayName'] = xml_entity.find('c:displayName', namespaces).text
        self['Status'] = xml_entity.find('c:activation/c:effectiveStatus', namespaces).text
        parentorg = xml_entity.find('c:parentOrgRef', namespaces)
        self['Parent'] = None if parentorg is None else parentorg.attrib['oid']


endpoints = {
    "ConnectorType": "connectors",
    "ConnectorHostType": "connectorHosts",
    "GenericObjectType": "genericObjects",
    "ResourceType": "resources",
    "UserType": "users",
    "ObjectTemplateType": "objectTemplates",
    "SystemConfigurationType": "systemConfigurations",
    "TaskType": "tasks",
    "ShadowType": "shadows",
    "RoleType": "roles",
    "ValuePolicyType": "valuePolicies",
    "OrgType": "orgs",
    "FunctionLibraryType": "functionLibraries"
}


def optional_text(node: ElementTree):
    return node.text if node is not None else None
