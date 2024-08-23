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


class RecordForlistApplicationOutput(object):
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
        'alert': 'bool',
        'application_name': 'str',
        'application_trn': 'str',
        'application_type': 'str',
        'args': 'str',
        'conf': 'dict(str, str)',
        'dependency': 'DependencyForlistApplicationOutput',
        'deploy_request': 'DeployRequestForlistApplicationOutput',
        'engine_version': 'str',
        'image': 'str',
        'is_latest_version': 'bool',
        'jar': 'str',
        'latest_version': 'str',
        'main_class': 'str',
        'project_id': 'str',
        'rest_url': 'str',
        'sql_text': 'str',
        'state': 'str',
        'user_id': 'str',
        'version_name': 'str'
    }

    attribute_map = {
        'alert': 'Alert',
        'application_name': 'ApplicationName',
        'application_trn': 'ApplicationTrn',
        'application_type': 'ApplicationType',
        'args': 'Args',
        'conf': 'Conf',
        'dependency': 'Dependency',
        'deploy_request': 'DeployRequest',
        'engine_version': 'EngineVersion',
        'image': 'Image',
        'is_latest_version': 'IsLatestVersion',
        'jar': 'Jar',
        'latest_version': 'LatestVersion',
        'main_class': 'MainClass',
        'project_id': 'ProjectId',
        'rest_url': 'RestUrl',
        'sql_text': 'SqlText',
        'state': 'State',
        'user_id': 'UserId',
        'version_name': 'VersionName'
    }

    def __init__(self, alert=None, application_name=None, application_trn=None, application_type=None, args=None, conf=None, dependency=None, deploy_request=None, engine_version=None, image=None, is_latest_version=None, jar=None, latest_version=None, main_class=None, project_id=None, rest_url=None, sql_text=None, state=None, user_id=None, version_name=None, _configuration=None):  # noqa: E501
        """RecordForlistApplicationOutput - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._alert = None
        self._application_name = None
        self._application_trn = None
        self._application_type = None
        self._args = None
        self._conf = None
        self._dependency = None
        self._deploy_request = None
        self._engine_version = None
        self._image = None
        self._is_latest_version = None
        self._jar = None
        self._latest_version = None
        self._main_class = None
        self._project_id = None
        self._rest_url = None
        self._sql_text = None
        self._state = None
        self._user_id = None
        self._version_name = None
        self.discriminator = None

        if alert is not None:
            self.alert = alert
        if application_name is not None:
            self.application_name = application_name
        if application_trn is not None:
            self.application_trn = application_trn
        if application_type is not None:
            self.application_type = application_type
        if args is not None:
            self.args = args
        if conf is not None:
            self.conf = conf
        if dependency is not None:
            self.dependency = dependency
        if deploy_request is not None:
            self.deploy_request = deploy_request
        if engine_version is not None:
            self.engine_version = engine_version
        if image is not None:
            self.image = image
        if is_latest_version is not None:
            self.is_latest_version = is_latest_version
        if jar is not None:
            self.jar = jar
        if latest_version is not None:
            self.latest_version = latest_version
        if main_class is not None:
            self.main_class = main_class
        if project_id is not None:
            self.project_id = project_id
        if rest_url is not None:
            self.rest_url = rest_url
        if sql_text is not None:
            self.sql_text = sql_text
        if state is not None:
            self.state = state
        if user_id is not None:
            self.user_id = user_id
        if version_name is not None:
            self.version_name = version_name

    @property
    def alert(self):
        """Gets the alert of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The alert of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: bool
        """
        return self._alert

    @alert.setter
    def alert(self, alert):
        """Sets the alert of this RecordForlistApplicationOutput.


        :param alert: The alert of this RecordForlistApplicationOutput.  # noqa: E501
        :type: bool
        """

        self._alert = alert

    @property
    def application_name(self):
        """Gets the application_name of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The application_name of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: str
        """
        return self._application_name

    @application_name.setter
    def application_name(self, application_name):
        """Sets the application_name of this RecordForlistApplicationOutput.


        :param application_name: The application_name of this RecordForlistApplicationOutput.  # noqa: E501
        :type: str
        """

        self._application_name = application_name

    @property
    def application_trn(self):
        """Gets the application_trn of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The application_trn of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: str
        """
        return self._application_trn

    @application_trn.setter
    def application_trn(self, application_trn):
        """Sets the application_trn of this RecordForlistApplicationOutput.


        :param application_trn: The application_trn of this RecordForlistApplicationOutput.  # noqa: E501
        :type: str
        """

        self._application_trn = application_trn

    @property
    def application_type(self):
        """Gets the application_type of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The application_type of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: str
        """
        return self._application_type

    @application_type.setter
    def application_type(self, application_type):
        """Sets the application_type of this RecordForlistApplicationOutput.


        :param application_type: The application_type of this RecordForlistApplicationOutput.  # noqa: E501
        :type: str
        """

        self._application_type = application_type

    @property
    def args(self):
        """Gets the args of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The args of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: str
        """
        return self._args

    @args.setter
    def args(self, args):
        """Sets the args of this RecordForlistApplicationOutput.


        :param args: The args of this RecordForlistApplicationOutput.  # noqa: E501
        :type: str
        """

        self._args = args

    @property
    def conf(self):
        """Gets the conf of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The conf of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._conf

    @conf.setter
    def conf(self, conf):
        """Sets the conf of this RecordForlistApplicationOutput.


        :param conf: The conf of this RecordForlistApplicationOutput.  # noqa: E501
        :type: dict(str, str)
        """

        self._conf = conf

    @property
    def dependency(self):
        """Gets the dependency of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The dependency of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: DependencyForlistApplicationOutput
        """
        return self._dependency

    @dependency.setter
    def dependency(self, dependency):
        """Sets the dependency of this RecordForlistApplicationOutput.


        :param dependency: The dependency of this RecordForlistApplicationOutput.  # noqa: E501
        :type: DependencyForlistApplicationOutput
        """

        self._dependency = dependency

    @property
    def deploy_request(self):
        """Gets the deploy_request of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The deploy_request of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: DeployRequestForlistApplicationOutput
        """
        return self._deploy_request

    @deploy_request.setter
    def deploy_request(self, deploy_request):
        """Sets the deploy_request of this RecordForlistApplicationOutput.


        :param deploy_request: The deploy_request of this RecordForlistApplicationOutput.  # noqa: E501
        :type: DeployRequestForlistApplicationOutput
        """

        self._deploy_request = deploy_request

    @property
    def engine_version(self):
        """Gets the engine_version of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The engine_version of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: str
        """
        return self._engine_version

    @engine_version.setter
    def engine_version(self, engine_version):
        """Sets the engine_version of this RecordForlistApplicationOutput.


        :param engine_version: The engine_version of this RecordForlistApplicationOutput.  # noqa: E501
        :type: str
        """

        self._engine_version = engine_version

    @property
    def image(self):
        """Gets the image of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The image of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: str
        """
        return self._image

    @image.setter
    def image(self, image):
        """Sets the image of this RecordForlistApplicationOutput.


        :param image: The image of this RecordForlistApplicationOutput.  # noqa: E501
        :type: str
        """

        self._image = image

    @property
    def is_latest_version(self):
        """Gets the is_latest_version of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The is_latest_version of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: bool
        """
        return self._is_latest_version

    @is_latest_version.setter
    def is_latest_version(self, is_latest_version):
        """Sets the is_latest_version of this RecordForlistApplicationOutput.


        :param is_latest_version: The is_latest_version of this RecordForlistApplicationOutput.  # noqa: E501
        :type: bool
        """

        self._is_latest_version = is_latest_version

    @property
    def jar(self):
        """Gets the jar of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The jar of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: str
        """
        return self._jar

    @jar.setter
    def jar(self, jar):
        """Sets the jar of this RecordForlistApplicationOutput.


        :param jar: The jar of this RecordForlistApplicationOutput.  # noqa: E501
        :type: str
        """

        self._jar = jar

    @property
    def latest_version(self):
        """Gets the latest_version of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The latest_version of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: str
        """
        return self._latest_version

    @latest_version.setter
    def latest_version(self, latest_version):
        """Sets the latest_version of this RecordForlistApplicationOutput.


        :param latest_version: The latest_version of this RecordForlistApplicationOutput.  # noqa: E501
        :type: str
        """

        self._latest_version = latest_version

    @property
    def main_class(self):
        """Gets the main_class of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The main_class of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: str
        """
        return self._main_class

    @main_class.setter
    def main_class(self, main_class):
        """Sets the main_class of this RecordForlistApplicationOutput.


        :param main_class: The main_class of this RecordForlistApplicationOutput.  # noqa: E501
        :type: str
        """

        self._main_class = main_class

    @property
    def project_id(self):
        """Gets the project_id of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The project_id of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: str
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        """Sets the project_id of this RecordForlistApplicationOutput.


        :param project_id: The project_id of this RecordForlistApplicationOutput.  # noqa: E501
        :type: str
        """

        self._project_id = project_id

    @property
    def rest_url(self):
        """Gets the rest_url of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The rest_url of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: str
        """
        return self._rest_url

    @rest_url.setter
    def rest_url(self, rest_url):
        """Sets the rest_url of this RecordForlistApplicationOutput.


        :param rest_url: The rest_url of this RecordForlistApplicationOutput.  # noqa: E501
        :type: str
        """

        self._rest_url = rest_url

    @property
    def sql_text(self):
        """Gets the sql_text of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The sql_text of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: str
        """
        return self._sql_text

    @sql_text.setter
    def sql_text(self, sql_text):
        """Sets the sql_text of this RecordForlistApplicationOutput.


        :param sql_text: The sql_text of this RecordForlistApplicationOutput.  # noqa: E501
        :type: str
        """

        self._sql_text = sql_text

    @property
    def state(self):
        """Gets the state of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The state of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this RecordForlistApplicationOutput.


        :param state: The state of this RecordForlistApplicationOutput.  # noqa: E501
        :type: str
        """

        self._state = state

    @property
    def user_id(self):
        """Gets the user_id of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The user_id of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: str
        """
        return self._user_id

    @user_id.setter
    def user_id(self, user_id):
        """Sets the user_id of this RecordForlistApplicationOutput.


        :param user_id: The user_id of this RecordForlistApplicationOutput.  # noqa: E501
        :type: str
        """

        self._user_id = user_id

    @property
    def version_name(self):
        """Gets the version_name of this RecordForlistApplicationOutput.  # noqa: E501


        :return: The version_name of this RecordForlistApplicationOutput.  # noqa: E501
        :rtype: str
        """
        return self._version_name

    @version_name.setter
    def version_name(self, version_name):
        """Sets the version_name of this RecordForlistApplicationOutput.


        :param version_name: The version_name of this RecordForlistApplicationOutput.  # noqa: E501
        :type: str
        """

        self._version_name = version_name

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
        if issubclass(RecordForlistApplicationOutput, dict):
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
        if not isinstance(other, RecordForlistApplicationOutput):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, RecordForlistApplicationOutput):
            return True

        return self.to_dict() != other.to_dict()
