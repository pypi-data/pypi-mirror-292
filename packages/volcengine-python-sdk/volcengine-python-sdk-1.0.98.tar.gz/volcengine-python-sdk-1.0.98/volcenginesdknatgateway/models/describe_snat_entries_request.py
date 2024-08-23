# coding: utf-8

"""
    natgateway

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class DescribeSnatEntriesRequest(object):
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
        'eip_id': 'str',
        'nat_gateway_id': 'str',
        'page_number': 'int',
        'page_size': 'int',
        'snat_entry_ids': 'list[str]',
        'snat_entry_name': 'str',
        'source_cidr': 'str',
        'subnet_id': 'str'
    }

    attribute_map = {
        'eip_id': 'EipId',
        'nat_gateway_id': 'NatGatewayId',
        'page_number': 'PageNumber',
        'page_size': 'PageSize',
        'snat_entry_ids': 'SnatEntryIds',
        'snat_entry_name': 'SnatEntryName',
        'source_cidr': 'SourceCidr',
        'subnet_id': 'SubnetId'
    }

    def __init__(self, eip_id=None, nat_gateway_id=None, page_number=None, page_size=None, snat_entry_ids=None, snat_entry_name=None, source_cidr=None, subnet_id=None, _configuration=None):  # noqa: E501
        """DescribeSnatEntriesRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._eip_id = None
        self._nat_gateway_id = None
        self._page_number = None
        self._page_size = None
        self._snat_entry_ids = None
        self._snat_entry_name = None
        self._source_cidr = None
        self._subnet_id = None
        self.discriminator = None

        if eip_id is not None:
            self.eip_id = eip_id
        if nat_gateway_id is not None:
            self.nat_gateway_id = nat_gateway_id
        if page_number is not None:
            self.page_number = page_number
        if page_size is not None:
            self.page_size = page_size
        if snat_entry_ids is not None:
            self.snat_entry_ids = snat_entry_ids
        if snat_entry_name is not None:
            self.snat_entry_name = snat_entry_name
        if source_cidr is not None:
            self.source_cidr = source_cidr
        if subnet_id is not None:
            self.subnet_id = subnet_id

    @property
    def eip_id(self):
        """Gets the eip_id of this DescribeSnatEntriesRequest.  # noqa: E501


        :return: The eip_id of this DescribeSnatEntriesRequest.  # noqa: E501
        :rtype: str
        """
        return self._eip_id

    @eip_id.setter
    def eip_id(self, eip_id):
        """Sets the eip_id of this DescribeSnatEntriesRequest.


        :param eip_id: The eip_id of this DescribeSnatEntriesRequest.  # noqa: E501
        :type: str
        """

        self._eip_id = eip_id

    @property
    def nat_gateway_id(self):
        """Gets the nat_gateway_id of this DescribeSnatEntriesRequest.  # noqa: E501


        :return: The nat_gateway_id of this DescribeSnatEntriesRequest.  # noqa: E501
        :rtype: str
        """
        return self._nat_gateway_id

    @nat_gateway_id.setter
    def nat_gateway_id(self, nat_gateway_id):
        """Sets the nat_gateway_id of this DescribeSnatEntriesRequest.


        :param nat_gateway_id: The nat_gateway_id of this DescribeSnatEntriesRequest.  # noqa: E501
        :type: str
        """

        self._nat_gateway_id = nat_gateway_id

    @property
    def page_number(self):
        """Gets the page_number of this DescribeSnatEntriesRequest.  # noqa: E501


        :return: The page_number of this DescribeSnatEntriesRequest.  # noqa: E501
        :rtype: int
        """
        return self._page_number

    @page_number.setter
    def page_number(self, page_number):
        """Sets the page_number of this DescribeSnatEntriesRequest.


        :param page_number: The page_number of this DescribeSnatEntriesRequest.  # noqa: E501
        :type: int
        """

        self._page_number = page_number

    @property
    def page_size(self):
        """Gets the page_size of this DescribeSnatEntriesRequest.  # noqa: E501


        :return: The page_size of this DescribeSnatEntriesRequest.  # noqa: E501
        :rtype: int
        """
        return self._page_size

    @page_size.setter
    def page_size(self, page_size):
        """Sets the page_size of this DescribeSnatEntriesRequest.


        :param page_size: The page_size of this DescribeSnatEntriesRequest.  # noqa: E501
        :type: int
        """
        if (self._configuration.client_side_validation and
                page_size is not None and page_size > 100):  # noqa: E501
            raise ValueError("Invalid value for `page_size`, must be a value less than or equal to `100`")  # noqa: E501

        self._page_size = page_size

    @property
    def snat_entry_ids(self):
        """Gets the snat_entry_ids of this DescribeSnatEntriesRequest.  # noqa: E501


        :return: The snat_entry_ids of this DescribeSnatEntriesRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._snat_entry_ids

    @snat_entry_ids.setter
    def snat_entry_ids(self, snat_entry_ids):
        """Sets the snat_entry_ids of this DescribeSnatEntriesRequest.


        :param snat_entry_ids: The snat_entry_ids of this DescribeSnatEntriesRequest.  # noqa: E501
        :type: list[str]
        """

        self._snat_entry_ids = snat_entry_ids

    @property
    def snat_entry_name(self):
        """Gets the snat_entry_name of this DescribeSnatEntriesRequest.  # noqa: E501


        :return: The snat_entry_name of this DescribeSnatEntriesRequest.  # noqa: E501
        :rtype: str
        """
        return self._snat_entry_name

    @snat_entry_name.setter
    def snat_entry_name(self, snat_entry_name):
        """Sets the snat_entry_name of this DescribeSnatEntriesRequest.


        :param snat_entry_name: The snat_entry_name of this DescribeSnatEntriesRequest.  # noqa: E501
        :type: str
        """

        self._snat_entry_name = snat_entry_name

    @property
    def source_cidr(self):
        """Gets the source_cidr of this DescribeSnatEntriesRequest.  # noqa: E501


        :return: The source_cidr of this DescribeSnatEntriesRequest.  # noqa: E501
        :rtype: str
        """
        return self._source_cidr

    @source_cidr.setter
    def source_cidr(self, source_cidr):
        """Sets the source_cidr of this DescribeSnatEntriesRequest.


        :param source_cidr: The source_cidr of this DescribeSnatEntriesRequest.  # noqa: E501
        :type: str
        """

        self._source_cidr = source_cidr

    @property
    def subnet_id(self):
        """Gets the subnet_id of this DescribeSnatEntriesRequest.  # noqa: E501


        :return: The subnet_id of this DescribeSnatEntriesRequest.  # noqa: E501
        :rtype: str
        """
        return self._subnet_id

    @subnet_id.setter
    def subnet_id(self, subnet_id):
        """Sets the subnet_id of this DescribeSnatEntriesRequest.


        :param subnet_id: The subnet_id of this DescribeSnatEntriesRequest.  # noqa: E501
        :type: str
        """

        self._subnet_id = subnet_id

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
        if issubclass(DescribeSnatEntriesRequest, dict):
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
        if not isinstance(other, DescribeSnatEntriesRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DescribeSnatEntriesRequest):
            return True

        return self.to_dict() != other.to_dict()
