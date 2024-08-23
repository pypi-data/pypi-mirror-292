# coding: utf-8

"""
    mcdn

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class DataForListAlertStrategiesOutput(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'alert_rule': 'AlertRuleForListAlertStrategiesOutput',
        'domains': 'list[DomainForListAlertStrategiesOutput]',
        'id': 'str',
        'name': 'str',
        'probe_tasks': 'list[ProbeTaskForListAlertStrategiesOutput]',
        'resource_scope': 'str',
        'resource_types': 'list[str]',
        'status': 'str',
        'subscribe_rule': 'SubscribeRuleForListAlertStrategiesOutput',
        'trigger_type': 'str'
    }

    attribute_map = {
        'alert_rule': 'AlertRule',
        'domains': 'Domains',
        'id': 'Id',
        'name': 'Name',
        'probe_tasks': 'ProbeTasks',
        'resource_scope': 'ResourceScope',
        'resource_types': 'ResourceTypes',
        'status': 'Status',
        'subscribe_rule': 'SubscribeRule',
        'trigger_type': 'TriggerType'
    }

    def __init__(self, alert_rule=None, domains=None, id=None, name=None, probe_tasks=None, resource_scope=None, resource_types=None, status=None, subscribe_rule=None, trigger_type=None, _configuration=None):  # noqa: E501
        """DataForListAlertStrategiesOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._alert_rule = None
        self._domains = None
        self._id = None
        self._name = None
        self._probe_tasks = None
        self._resource_scope = None
        self._resource_types = None
        self._status = None
        self._subscribe_rule = None
        self._trigger_type = None
        self.discriminator = None

        if alert_rule is not None:
            self.alert_rule = alert_rule
        if domains is not None:
            self.domains = domains
        if id is not None:
            self.id = id
        if name is not None:
            self.name = name
        if probe_tasks is not None:
            self.probe_tasks = probe_tasks
        if resource_scope is not None:
            self.resource_scope = resource_scope
        if resource_types is not None:
            self.resource_types = resource_types
        if status is not None:
            self.status = status
        if subscribe_rule is not None:
            self.subscribe_rule = subscribe_rule
        if trigger_type is not None:
            self.trigger_type = trigger_type

    @property
    def alert_rule(self):
        """Gets the alert_rule of this DataForListAlertStrategiesOutput.  # noqa: E501


        :return: The alert_rule of this DataForListAlertStrategiesOutput.  # noqa: E501
        :rtype: AlertRuleForListAlertStrategiesOutput
        """
        return self._alert_rule

    @alert_rule.setter
    def alert_rule(self, alert_rule):
        """Sets the alert_rule of this DataForListAlertStrategiesOutput.


        :param alert_rule: The alert_rule of this DataForListAlertStrategiesOutput.  # noqa: E501
        :type: AlertRuleForListAlertStrategiesOutput
        """

        self._alert_rule = alert_rule

    @property
    def domains(self):
        """Gets the domains of this DataForListAlertStrategiesOutput.  # noqa: E501


        :return: The domains of this DataForListAlertStrategiesOutput.  # noqa: E501
        :rtype: list[DomainForListAlertStrategiesOutput]
        """
        return self._domains

    @domains.setter
    def domains(self, domains):
        """Sets the domains of this DataForListAlertStrategiesOutput.


        :param domains: The domains of this DataForListAlertStrategiesOutput.  # noqa: E501
        :type: list[DomainForListAlertStrategiesOutput]
        """

        self._domains = domains

    @property
    def id(self):
        """Gets the id of this DataForListAlertStrategiesOutput.  # noqa: E501


        :return: The id of this DataForListAlertStrategiesOutput.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this DataForListAlertStrategiesOutput.


        :param id: The id of this DataForListAlertStrategiesOutput.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def name(self):
        """Gets the name of this DataForListAlertStrategiesOutput.  # noqa: E501


        :return: The name of this DataForListAlertStrategiesOutput.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this DataForListAlertStrategiesOutput.


        :param name: The name of this DataForListAlertStrategiesOutput.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def probe_tasks(self):
        """Gets the probe_tasks of this DataForListAlertStrategiesOutput.  # noqa: E501


        :return: The probe_tasks of this DataForListAlertStrategiesOutput.  # noqa: E501
        :rtype: list[ProbeTaskForListAlertStrategiesOutput]
        """
        return self._probe_tasks

    @probe_tasks.setter
    def probe_tasks(self, probe_tasks):
        """Sets the probe_tasks of this DataForListAlertStrategiesOutput.


        :param probe_tasks: The probe_tasks of this DataForListAlertStrategiesOutput.  # noqa: E501
        :type: list[ProbeTaskForListAlertStrategiesOutput]
        """

        self._probe_tasks = probe_tasks

    @property
    def resource_scope(self):
        """Gets the resource_scope of this DataForListAlertStrategiesOutput.  # noqa: E501


        :return: The resource_scope of this DataForListAlertStrategiesOutput.  # noqa: E501
        :rtype: str
        """
        return self._resource_scope

    @resource_scope.setter
    def resource_scope(self, resource_scope):
        """Sets the resource_scope of this DataForListAlertStrategiesOutput.


        :param resource_scope: The resource_scope of this DataForListAlertStrategiesOutput.  # noqa: E501
        :type: str
        """

        self._resource_scope = resource_scope

    @property
    def resource_types(self):
        """Gets the resource_types of this DataForListAlertStrategiesOutput.  # noqa: E501


        :return: The resource_types of this DataForListAlertStrategiesOutput.  # noqa: E501
        :rtype: list[str]
        """
        return self._resource_types

    @resource_types.setter
    def resource_types(self, resource_types):
        """Sets the resource_types of this DataForListAlertStrategiesOutput.


        :param resource_types: The resource_types of this DataForListAlertStrategiesOutput.  # noqa: E501
        :type: list[str]
        """

        self._resource_types = resource_types

    @property
    def status(self):
        """Gets the status of this DataForListAlertStrategiesOutput.  # noqa: E501


        :return: The status of this DataForListAlertStrategiesOutput.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this DataForListAlertStrategiesOutput.


        :param status: The status of this DataForListAlertStrategiesOutput.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def subscribe_rule(self):
        """Gets the subscribe_rule of this DataForListAlertStrategiesOutput.  # noqa: E501


        :return: The subscribe_rule of this DataForListAlertStrategiesOutput.  # noqa: E501
        :rtype: SubscribeRuleForListAlertStrategiesOutput
        """
        return self._subscribe_rule

    @subscribe_rule.setter
    def subscribe_rule(self, subscribe_rule):
        """Sets the subscribe_rule of this DataForListAlertStrategiesOutput.


        :param subscribe_rule: The subscribe_rule of this DataForListAlertStrategiesOutput.  # noqa: E501
        :type: SubscribeRuleForListAlertStrategiesOutput
        """

        self._subscribe_rule = subscribe_rule

    @property
    def trigger_type(self):
        """Gets the trigger_type of this DataForListAlertStrategiesOutput.  # noqa: E501


        :return: The trigger_type of this DataForListAlertStrategiesOutput.  # noqa: E501
        :rtype: str
        """
        return self._trigger_type

    @trigger_type.setter
    def trigger_type(self, trigger_type):
        """Sets the trigger_type of this DataForListAlertStrategiesOutput.


        :param trigger_type: The trigger_type of this DataForListAlertStrategiesOutput.  # noqa: E501
        :type: str
        """

        self._trigger_type = trigger_type

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(DataForListAlertStrategiesOutput, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, DataForListAlertStrategiesOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DataForListAlertStrategiesOutput):
            return True

        return self.to_dict() != other.to_dict()
