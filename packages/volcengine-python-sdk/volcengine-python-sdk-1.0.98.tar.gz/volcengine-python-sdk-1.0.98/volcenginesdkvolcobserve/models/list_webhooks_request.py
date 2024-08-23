# coding: utf-8

"""
    volc_observe

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class ListWebhooksRequest(object):
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
        'asc': 'bool',
        'event_rule_id': 'str',
        'name': 'str',
        'order_by': 'str',
        'page_number': 'int',
        'page_size': 'int',
        'rule_id': 'str',
        'total_count': 'int',
        'type': 'str',
        'url': 'str'
    }

    attribute_map = {
        'asc': 'Asc',
        'event_rule_id': 'EventRuleId',
        'name': 'Name',
        'order_by': 'OrderBy',
        'page_number': 'PageNumber',
        'page_size': 'PageSize',
        'rule_id': 'RuleId',
        'total_count': 'TotalCount',
        'type': 'Type',
        'url': 'Url'
    }

    def __init__(self, asc=None, event_rule_id=None, name=None, order_by=None, page_number=None, page_size=None, rule_id=None, total_count=None, type=None, url=None, _configuration=None):  # noqa: E501
        """ListWebhooksRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._asc = None
        self._event_rule_id = None
        self._name = None
        self._order_by = None
        self._page_number = None
        self._page_size = None
        self._rule_id = None
        self._total_count = None
        self._type = None
        self._url = None
        self.discriminator = None

        if asc is not None:
            self.asc = asc
        if event_rule_id is not None:
            self.event_rule_id = event_rule_id
        if name is not None:
            self.name = name
        if order_by is not None:
            self.order_by = order_by
        if page_number is not None:
            self.page_number = page_number
        if page_size is not None:
            self.page_size = page_size
        if rule_id is not None:
            self.rule_id = rule_id
        if total_count is not None:
            self.total_count = total_count
        if type is not None:
            self.type = type
        if url is not None:
            self.url = url

    @property
    def asc(self):
        """Gets the asc of this ListWebhooksRequest.  # noqa: E501


        :return: The asc of this ListWebhooksRequest.  # noqa: E501
        :rtype: bool
        """
        return self._asc

    @asc.setter
    def asc(self, asc):
        """Sets the asc of this ListWebhooksRequest.


        :param asc: The asc of this ListWebhooksRequest.  # noqa: E501
        :type: bool
        """

        self._asc = asc

    @property
    def event_rule_id(self):
        """Gets the event_rule_id of this ListWebhooksRequest.  # noqa: E501


        :return: The event_rule_id of this ListWebhooksRequest.  # noqa: E501
        :rtype: str
        """
        return self._event_rule_id

    @event_rule_id.setter
    def event_rule_id(self, event_rule_id):
        """Sets the event_rule_id of this ListWebhooksRequest.


        :param event_rule_id: The event_rule_id of this ListWebhooksRequest.  # noqa: E501
        :type: str
        """

        self._event_rule_id = event_rule_id

    @property
    def name(self):
        """Gets the name of this ListWebhooksRequest.  # noqa: E501


        :return: The name of this ListWebhooksRequest.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this ListWebhooksRequest.


        :param name: The name of this ListWebhooksRequest.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def order_by(self):
        """Gets the order_by of this ListWebhooksRequest.  # noqa: E501


        :return: The order_by of this ListWebhooksRequest.  # noqa: E501
        :rtype: str
        """
        return self._order_by

    @order_by.setter
    def order_by(self, order_by):
        """Sets the order_by of this ListWebhooksRequest.


        :param order_by: The order_by of this ListWebhooksRequest.  # noqa: E501
        :type: str
        """

        self._order_by = order_by

    @property
    def page_number(self):
        """Gets the page_number of this ListWebhooksRequest.  # noqa: E501


        :return: The page_number of this ListWebhooksRequest.  # noqa: E501
        :rtype: int
        """
        return self._page_number

    @page_number.setter
    def page_number(self, page_number):
        """Sets the page_number of this ListWebhooksRequest.


        :param page_number: The page_number of this ListWebhooksRequest.  # noqa: E501
        :type: int
        """

        self._page_number = page_number

    @property
    def page_size(self):
        """Gets the page_size of this ListWebhooksRequest.  # noqa: E501


        :return: The page_size of this ListWebhooksRequest.  # noqa: E501
        :rtype: int
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """Sets the page_size of this ListWebhooksRequest.


        :param page_size: The page_size of this ListWebhooksRequest.  # noqa: E501
        :type: int
        """

        self._page_size = page_size

    @property
    def rule_id(self):
        """Gets the rule_id of this ListWebhooksRequest.  # noqa: E501


        :return: The rule_id of this ListWebhooksRequest.  # noqa: E501
        :rtype: str
        """
        return self._rule_id

    @rule_id.setter
    def rule_id(self, rule_id):
        """Sets the rule_id of this ListWebhooksRequest.


        :param rule_id: The rule_id of this ListWebhooksRequest.  # noqa: E501
        :type: str
        """

        self._rule_id = rule_id

    @property
    def total_count(self):
        """Gets the total_count of this ListWebhooksRequest.  # noqa: E501


        :return: The total_count of this ListWebhooksRequest.  # noqa: E501
        :rtype: int
        """
        return self._total_count

    @total_count.setter
    def total_count(self, total_count):
        """Sets the total_count of this ListWebhooksRequest.


        :param total_count: The total_count of this ListWebhooksRequest.  # noqa: E501
        :type: int
        """

        self._total_count = total_count

    @property
    def type(self):
        """Gets the type of this ListWebhooksRequest.  # noqa: E501


        :return: The type of this ListWebhooksRequest.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this ListWebhooksRequest.


        :param type: The type of this ListWebhooksRequest.  # noqa: E501
        :type: str
        """

        self._type = type

    @property
    def url(self):
        """Gets the url of this ListWebhooksRequest.  # noqa: E501


        :return: The url of this ListWebhooksRequest.  # noqa: E501
        :rtype: str
        """
        return self._url

    @url.setter
    def url(self, url):
        """Sets the url of this ListWebhooksRequest.


        :param url: The url of this ListWebhooksRequest.  # noqa: E501
        :type: str
        """

        self._url = url

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
        if issubclass(ListWebhooksRequest, dict):
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
        if not isinstance(other, ListWebhooksRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ListWebhooksRequest):
            return True

        return self.to_dict() != other.to_dict()
