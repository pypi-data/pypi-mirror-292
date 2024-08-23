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


class WeightInfoForDescribeDnsScheduleOutput(object):
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
        'country': 'str',
        'is_failover': 'bool',
        'isp': 'str',
        'province': 'str',
        'related_strategy_id': 'str',
        'strategy': 'str',
        'weight_failover_infos': 'list[WeightFailoverInfoForDescribeDnsScheduleOutput]',
        'weight_info_items': 'list[WeightInfoItemForDescribeDnsScheduleOutput]'
    }

    attribute_map = {
        'country': 'Country',
        'is_failover': 'IsFailover',
        'isp': 'Isp',
        'province': 'Province',
        'related_strategy_id': 'RelatedStrategyId',
        'strategy': 'Strategy',
        'weight_failover_infos': 'WeightFailoverInfos',
        'weight_info_items': 'WeightInfoItems'
    }

    def __init__(self, country=None, is_failover=None, isp=None, province=None, related_strategy_id=None, strategy=None, weight_failover_infos=None, weight_info_items=None, _configuration=None):  # noqa: E501
        """WeightInfoForDescribeDnsScheduleOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._country = None
        self._is_failover = None
        self._isp = None
        self._province = None
        self._related_strategy_id = None
        self._strategy = None
        self._weight_failover_infos = None
        self._weight_info_items = None
        self.discriminator = None

        if country is not None:
            self.country = country
        if is_failover is not None:
            self.is_failover = is_failover
        if isp is not None:
            self.isp = isp
        if province is not None:
            self.province = province
        if related_strategy_id is not None:
            self.related_strategy_id = related_strategy_id
        if strategy is not None:
            self.strategy = strategy
        if weight_failover_infos is not None:
            self.weight_failover_infos = weight_failover_infos
        if weight_info_items is not None:
            self.weight_info_items = weight_info_items

    @property
    def country(self):
        """Gets the country of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501


        :return: The country of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501
        :rtype: str
        """
        return self._country

    @country.setter
    def country(self, country):
        """Sets the country of this WeightInfoForDescribeDnsScheduleOutput.


        :param country: The country of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501
        :type: str
        """

        self._country = country

    @property
    def is_failover(self):
        """Gets the is_failover of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501


        :return: The is_failover of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501
        :rtype: bool
        """
        return self._is_failover

    @is_failover.setter
    def is_failover(self, is_failover):
        """Sets the is_failover of this WeightInfoForDescribeDnsScheduleOutput.


        :param is_failover: The is_failover of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501
        :type: bool
        """

        self._is_failover = is_failover

    @property
    def isp(self):
        """Gets the isp of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501


        :return: The isp of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501
        :rtype: str
        """
        return self._isp

    @isp.setter
    def isp(self, isp):
        """Sets the isp of this WeightInfoForDescribeDnsScheduleOutput.


        :param isp: The isp of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501
        :type: str
        """

        self._isp = isp

    @property
    def province(self):
        """Gets the province of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501


        :return: The province of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501
        :rtype: str
        """
        return self._province

    @province.setter
    def province(self, province):
        """Sets the province of this WeightInfoForDescribeDnsScheduleOutput.


        :param province: The province of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501
        :type: str
        """

        self._province = province

    @property
    def related_strategy_id(self):
        """Gets the related_strategy_id of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501


        :return: The related_strategy_id of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501
        :rtype: str
        """
        return self._related_strategy_id

    @related_strategy_id.setter
    def related_strategy_id(self, related_strategy_id):
        """Sets the related_strategy_id of this WeightInfoForDescribeDnsScheduleOutput.


        :param related_strategy_id: The related_strategy_id of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501
        :type: str
        """

        self._related_strategy_id = related_strategy_id

    @property
    def strategy(self):
        """Gets the strategy of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501


        :return: The strategy of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501
        :rtype: str
        """
        return self._strategy

    @strategy.setter
    def strategy(self, strategy):
        """Sets the strategy of this WeightInfoForDescribeDnsScheduleOutput.


        :param strategy: The strategy of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501
        :type: str
        """

        self._strategy = strategy

    @property
    def weight_failover_infos(self):
        """Gets the weight_failover_infos of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501


        :return: The weight_failover_infos of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501
        :rtype: list[WeightFailoverInfoForDescribeDnsScheduleOutput]
        """
        return self._weight_failover_infos

    @weight_failover_infos.setter
    def weight_failover_infos(self, weight_failover_infos):
        """Sets the weight_failover_infos of this WeightInfoForDescribeDnsScheduleOutput.


        :param weight_failover_infos: The weight_failover_infos of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501
        :type: list[WeightFailoverInfoForDescribeDnsScheduleOutput]
        """

        self._weight_failover_infos = weight_failover_infos

    @property
    def weight_info_items(self):
        """Gets the weight_info_items of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501


        :return: The weight_info_items of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501
        :rtype: list[WeightInfoItemForDescribeDnsScheduleOutput]
        """
        return self._weight_info_items

    @weight_info_items.setter
    def weight_info_items(self, weight_info_items):
        """Sets the weight_info_items of this WeightInfoForDescribeDnsScheduleOutput.


        :param weight_info_items: The weight_info_items of this WeightInfoForDescribeDnsScheduleOutput.  # noqa: E501
        :type: list[WeightInfoItemForDescribeDnsScheduleOutput]
        """

        self._weight_info_items = weight_info_items

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
        if issubclass(WeightInfoForDescribeDnsScheduleOutput, dict):
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
        if not isinstance(other, WeightInfoForDescribeDnsScheduleOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, WeightInfoForDescribeDnsScheduleOutput):
            return True

        return self.to_dict() != other.to_dict()
