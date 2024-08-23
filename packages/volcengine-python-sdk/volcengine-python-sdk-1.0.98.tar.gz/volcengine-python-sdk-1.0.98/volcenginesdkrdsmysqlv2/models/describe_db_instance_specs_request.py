# coding: utf-8

"""
    rds_mysql_v2

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class DescribeDBInstanceSpecsRequest(object):
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
        'db_engine_version': 'str',
        'instance_type': 'str',
        'spec_code': 'str',
        'zone_id': 'str'
    }

    attribute_map = {
        'db_engine_version': 'DBEngineVersion',
        'instance_type': 'InstanceType',
        'spec_code': 'SpecCode',
        'zone_id': 'ZoneId'
    }

    def __init__(self, db_engine_version=None, instance_type=None, spec_code=None, zone_id=None, _configuration=None):  # noqa: E501
        """DescribeDBInstanceSpecsRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._db_engine_version = None
        self._instance_type = None
        self._spec_code = None
        self._zone_id = None
        self.discriminator = None

        if db_engine_version is not None:
            self.db_engine_version = db_engine_version
        if instance_type is not None:
            self.instance_type = instance_type
        if spec_code is not None:
            self.spec_code = spec_code
        if zone_id is not None:
            self.zone_id = zone_id

    @property
    def db_engine_version(self):
        """Gets the db_engine_version of this DescribeDBInstanceSpecsRequest.  # noqa: E501


        :return: The db_engine_version of this DescribeDBInstanceSpecsRequest.  # noqa: E501
        :rtype: str
        """
        return self._db_engine_version

    @db_engine_version.setter
    def db_engine_version(self, db_engine_version):
        """Sets the db_engine_version of this DescribeDBInstanceSpecsRequest.


        :param db_engine_version: The db_engine_version of this DescribeDBInstanceSpecsRequest.  # noqa: E501
        :type: str
        """

        self._db_engine_version = db_engine_version

    @property
    def instance_type(self):
        """Gets the instance_type of this DescribeDBInstanceSpecsRequest.  # noqa: E501


        :return: The instance_type of this DescribeDBInstanceSpecsRequest.  # noqa: E501
        :rtype: str
        """
        return self._instance_type

    @instance_type.setter
    def instance_type(self, instance_type):
        """Sets the instance_type of this DescribeDBInstanceSpecsRequest.


        :param instance_type: The instance_type of this DescribeDBInstanceSpecsRequest.  # noqa: E501
        :type: str
        """

        self._instance_type = instance_type

    @property
    def spec_code(self):
        """Gets the spec_code of this DescribeDBInstanceSpecsRequest.  # noqa: E501


        :return: The spec_code of this DescribeDBInstanceSpecsRequest.  # noqa: E501
        :rtype: str
        """
        return self._spec_code

    @spec_code.setter
    def spec_code(self, spec_code):
        """Sets the spec_code of this DescribeDBInstanceSpecsRequest.


        :param spec_code: The spec_code of this DescribeDBInstanceSpecsRequest.  # noqa: E501
        :type: str
        """

        self._spec_code = spec_code

    @property
    def zone_id(self):
        """Gets the zone_id of this DescribeDBInstanceSpecsRequest.  # noqa: E501


        :return: The zone_id of this DescribeDBInstanceSpecsRequest.  # noqa: E501
        :rtype: str
        """
        return self._zone_id

    @zone_id.setter
    def zone_id(self, zone_id):
        """Sets the zone_id of this DescribeDBInstanceSpecsRequest.


        :param zone_id: The zone_id of this DescribeDBInstanceSpecsRequest.  # noqa: E501
        :type: str
        """

        self._zone_id = zone_id

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
        if issubclass(DescribeDBInstanceSpecsRequest, dict):
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
        if not isinstance(other, DescribeDBInstanceSpecsRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DescribeDBInstanceSpecsRequest):
            return True

        return self.to_dict() != other.to_dict()
