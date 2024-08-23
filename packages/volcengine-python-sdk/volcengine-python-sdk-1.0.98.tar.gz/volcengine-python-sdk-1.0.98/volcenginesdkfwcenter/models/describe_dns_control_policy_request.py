# coding: utf-8

"""
    fwcenter

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class DescribeDnsControlPolicyRequest(object):
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
        'description': 'str',
        'destination': 'list[str]',
        'page_number': 'int',
        'page_size': 'int',
        'rule_id': 'list[str]',
        'source': 'list[str]',
        'status': 'list[bool]'
    }

    attribute_map = {
        'description': 'Description',
        'destination': 'Destination',
        'page_number': 'PageNumber',
        'page_size': 'PageSize',
        'rule_id': 'RuleId',
        'source': 'Source',
        'status': 'Status'
    }

    def __init__(self, description=None, destination=None, page_number=None, page_size=None, rule_id=None, source=None, status=None, _configuration=None):  # noqa: E501
        """DescribeDnsControlPolicyRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._description = None
        self._destination = None
        self._page_number = None
        self._page_size = None
        self._rule_id = None
        self._source = None
        self._status = None
        self.discriminator = None

        if description is not None:
            self.description = description
        if destination is not None:
            self.destination = destination
        if page_number is not None:
            self.page_number = page_number
        if page_size is not None:
            self.page_size = page_size
        if rule_id is not None:
            self.rule_id = rule_id
        if source is not None:
            self.source = source
        if status is not None:
            self.status = status

    @property
    def description(self):
        """Gets the description of this DescribeDnsControlPolicyRequest.  # noqa: E501


        :return: The description of this DescribeDnsControlPolicyRequest.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this DescribeDnsControlPolicyRequest.


        :param description: The description of this DescribeDnsControlPolicyRequest.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def destination(self):
        """Gets the destination of this DescribeDnsControlPolicyRequest.  # noqa: E501


        :return: The destination of this DescribeDnsControlPolicyRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._destination

    @destination.setter
    def destination(self, destination):
        """Sets the destination of this DescribeDnsControlPolicyRequest.


        :param destination: The destination of this DescribeDnsControlPolicyRequest.  # noqa: E501
        :type: list[str]
        """

        self._destination = destination

    @property
    def page_number(self):
        """Gets the page_number of this DescribeDnsControlPolicyRequest.  # noqa: E501


        :return: The page_number of this DescribeDnsControlPolicyRequest.  # noqa: E501
        :rtype: int
        """
        return self._page_number

    @page_number.setter
    def page_number(self, page_number):
        """Sets the page_number of this DescribeDnsControlPolicyRequest.


        :param page_number: The page_number of this DescribeDnsControlPolicyRequest.  # noqa: E501
        :type: int
        """

        self._page_number = page_number

    @property
    def page_size(self):
        """Gets the page_size of this DescribeDnsControlPolicyRequest.  # noqa: E501


        :return: The page_size of this DescribeDnsControlPolicyRequest.  # noqa: E501
        :rtype: int
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """Sets the page_size of this DescribeDnsControlPolicyRequest.


        :param page_size: The page_size of this DescribeDnsControlPolicyRequest.  # noqa: E501
        :type: int
        """

        self._page_size = page_size

    @property
    def rule_id(self):
        """Gets the rule_id of this DescribeDnsControlPolicyRequest.  # noqa: E501


        :return: The rule_id of this DescribeDnsControlPolicyRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._rule_id

    @rule_id.setter
    def rule_id(self, rule_id):
        """Sets the rule_id of this DescribeDnsControlPolicyRequest.


        :param rule_id: The rule_id of this DescribeDnsControlPolicyRequest.  # noqa: E501
        :type: list[str]
        """

        self._rule_id = rule_id

    @property
    def source(self):
        """Gets the source of this DescribeDnsControlPolicyRequest.  # noqa: E501


        :return: The source of this DescribeDnsControlPolicyRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this DescribeDnsControlPolicyRequest.


        :param source: The source of this DescribeDnsControlPolicyRequest.  # noqa: E501
        :type: list[str]
        """

        self._source = source

    @property
    def status(self):
        """Gets the status of this DescribeDnsControlPolicyRequest.  # noqa: E501


        :return: The status of this DescribeDnsControlPolicyRequest.  # noqa: E501
        :rtype: list[bool]
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this DescribeDnsControlPolicyRequest.


        :param status: The status of this DescribeDnsControlPolicyRequest.  # noqa: E501
        :type: list[bool]
        """

        self._status = status

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
        if issubclass(DescribeDnsControlPolicyRequest, dict):
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
        if not isinstance(other, DescribeDnsControlPolicyRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DescribeDnsControlPolicyRequest):
            return True

        return self.to_dict() != other.to_dict()
