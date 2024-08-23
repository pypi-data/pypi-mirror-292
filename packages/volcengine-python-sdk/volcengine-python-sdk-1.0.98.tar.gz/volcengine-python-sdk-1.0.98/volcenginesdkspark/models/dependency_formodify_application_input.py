# coding: utf-8

"""
    spark

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: common-version
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from volcenginesdkcore.configuration import Configuration


class DependencyFormodifyApplicationInput(object):
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
        'archives': 'list[str]',
        'files': 'list[str]',
        'jars': 'list[str]',
        'py_files': 'list[str]'
    }

    attribute_map = {
        'archives': 'Archives',
        'files': 'Files',
        'jars': 'Jars',
        'py_files': 'PyFiles'
    }

    def __init__(self, archives=None, files=None, jars=None, py_files=None, _configuration=None):  # noqa: E501
        """DependencyFormodifyApplicationInput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._archives = None
        self._files = None
        self._jars = None
        self._py_files = None
        self.discriminator = None

        if archives is not None:
            self.archives = archives
        if files is not None:
            self.files = files
        if jars is not None:
            self.jars = jars
        if py_files is not None:
            self.py_files = py_files

    @property
    def archives(self):
        """Gets the archives of this DependencyFormodifyApplicationInput.  # noqa: E501


        :return: The archives of this DependencyFormodifyApplicationInput.  # noqa: E501
        :rtype: list[str]
        """
        return self._archives

    @archives.setter
    def archives(self, archives):
        """Sets the archives of this DependencyFormodifyApplicationInput.


        :param archives: The archives of this DependencyFormodifyApplicationInput.  # noqa: E501
        :type: list[str]
        """

        self._archives = archives

    @property
    def files(self):
        """Gets the files of this DependencyFormodifyApplicationInput.  # noqa: E501


        :return: The files of this DependencyFormodifyApplicationInput.  # noqa: E501
        :rtype: list[str]
        """
        return self._files

    @files.setter
    def files(self, files):
        """Sets the files of this DependencyFormodifyApplicationInput.


        :param files: The files of this DependencyFormodifyApplicationInput.  # noqa: E501
        :type: list[str]
        """

        self._files = files

    @property
    def jars(self):
        """Gets the jars of this DependencyFormodifyApplicationInput.  # noqa: E501


        :return: The jars of this DependencyFormodifyApplicationInput.  # noqa: E501
        :rtype: list[str]
        """
        return self._jars

    @jars.setter
    def jars(self, jars):
        """Sets the jars of this DependencyFormodifyApplicationInput.


        :param jars: The jars of this DependencyFormodifyApplicationInput.  # noqa: E501
        :type: list[str]
        """

        self._jars = jars

    @property
    def py_files(self):
        """Gets the py_files of this DependencyFormodifyApplicationInput.  # noqa: E501


        :return: The py_files of this DependencyFormodifyApplicationInput.  # noqa: E501
        :rtype: list[str]
        """
        return self._py_files

    @py_files.setter
    def py_files(self, py_files):
        """Sets the py_files of this DependencyFormodifyApplicationInput.


        :param py_files: The py_files of this DependencyFormodifyApplicationInput.  # noqa: E501
        :type: list[str]
        """

        self._py_files = py_files

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
        if issubclass(DependencyFormodifyApplicationInput, dict):
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
        if not isinstance(other, DependencyFormodifyApplicationInput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DependencyFormodifyApplicationInput):
            return True

        return self.to_dict() != other.to_dict()
