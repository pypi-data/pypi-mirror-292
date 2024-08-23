# coding: utf-8

"""
    fluid

    client for fluid  # noqa: E501

    The version of the OpenAPI document: v0.1
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from fluid.configuration import Configuration


class DatasetSpec(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'access_modes': 'list[str]',
        'data_restore_location': 'DataRestoreLocation',
        'mounts': 'list[Mount]',
        'node_affinity': 'CacheableNodeAffinity',
        'owner': 'User',
        'placement': 'str',
        'runtimes': 'list[Runtime]',
        'shared_encrypt_options': 'list[EncryptOption]',
        'shared_options': 'dict(str, str)',
        'tolerations': 'list[V1Toleration]'
    }

    attribute_map = {
        'access_modes': 'accessModes',
        'data_restore_location': 'dataRestoreLocation',
        'mounts': 'mounts',
        'node_affinity': 'nodeAffinity',
        'owner': 'owner',
        'placement': 'placement',
        'runtimes': 'runtimes',
        'shared_encrypt_options': 'sharedEncryptOptions',
        'shared_options': 'sharedOptions',
        'tolerations': 'tolerations'
    }

    def __init__(self, access_modes=None, data_restore_location=None, mounts=None, node_affinity=None, owner=None, placement=None, runtimes=None, shared_encrypt_options=None, shared_options=None, tolerations=None, local_vars_configuration=None):  # noqa: E501
        """DatasetSpec - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._access_modes = None
        self._data_restore_location = None
        self._mounts = None
        self._node_affinity = None
        self._owner = None
        self._placement = None
        self._runtimes = None
        self._shared_encrypt_options = None
        self._shared_options = None
        self._tolerations = None
        self.discriminator = None

        if access_modes is not None:
            self.access_modes = access_modes
        if data_restore_location is not None:
            self.data_restore_location = data_restore_location
        if mounts is not None:
            self.mounts = mounts
        if node_affinity is not None:
            self.node_affinity = node_affinity
        if owner is not None:
            self.owner = owner
        if placement is not None:
            self.placement = placement
        if runtimes is not None:
            self.runtimes = runtimes
        if shared_encrypt_options is not None:
            self.shared_encrypt_options = shared_encrypt_options
        if shared_options is not None:
            self.shared_options = shared_options
        if tolerations is not None:
            self.tolerations = tolerations

    @property
    def access_modes(self):
        """Gets the access_modes of this DatasetSpec.  # noqa: E501

        AccessModes contains all ways the volume backing the PVC can be mounted  # noqa: E501

        :return: The access_modes of this DatasetSpec.  # noqa: E501
        :rtype: list[str]
        """
        return self._access_modes

    @access_modes.setter
    def access_modes(self, access_modes):
        """Sets the access_modes of this DatasetSpec.

        AccessModes contains all ways the volume backing the PVC can be mounted  # noqa: E501

        :param access_modes: The access_modes of this DatasetSpec.  # noqa: E501
        :type: list[str]
        """

        self._access_modes = access_modes

    @property
    def data_restore_location(self):
        """Gets the data_restore_location of this DatasetSpec.  # noqa: E501


        :return: The data_restore_location of this DatasetSpec.  # noqa: E501
        :rtype: DataRestoreLocation
        """
        return self._data_restore_location

    @data_restore_location.setter
    def data_restore_location(self, data_restore_location):
        """Sets the data_restore_location of this DatasetSpec.


        :param data_restore_location: The data_restore_location of this DatasetSpec.  # noqa: E501
        :type: DataRestoreLocation
        """

        self._data_restore_location = data_restore_location

    @property
    def mounts(self):
        """Gets the mounts of this DatasetSpec.  # noqa: E501

        Mount Points to be mounted on cache runtime. <br> This field can be empty because some runtimes don't need to mount external storage (e.g. <a href=\"https://v6d.io/\">Vineyard</a>).  # noqa: E501

        :return: The mounts of this DatasetSpec.  # noqa: E501
        :rtype: list[Mount]
        """
        return self._mounts

    @mounts.setter
    def mounts(self, mounts):
        """Sets the mounts of this DatasetSpec.

        Mount Points to be mounted on cache runtime. <br> This field can be empty because some runtimes don't need to mount external storage (e.g. <a href=\"https://v6d.io/\">Vineyard</a>).  # noqa: E501

        :param mounts: The mounts of this DatasetSpec.  # noqa: E501
        :type: list[Mount]
        """

        self._mounts = mounts

    @property
    def node_affinity(self):
        """Gets the node_affinity of this DatasetSpec.  # noqa: E501


        :return: The node_affinity of this DatasetSpec.  # noqa: E501
        :rtype: CacheableNodeAffinity
        """
        return self._node_affinity

    @node_affinity.setter
    def node_affinity(self, node_affinity):
        """Sets the node_affinity of this DatasetSpec.


        :param node_affinity: The node_affinity of this DatasetSpec.  # noqa: E501
        :type: CacheableNodeAffinity
        """

        self._node_affinity = node_affinity

    @property
    def owner(self):
        """Gets the owner of this DatasetSpec.  # noqa: E501


        :return: The owner of this DatasetSpec.  # noqa: E501
        :rtype: User
        """
        return self._owner

    @owner.setter
    def owner(self, owner):
        """Sets the owner of this DatasetSpec.


        :param owner: The owner of this DatasetSpec.  # noqa: E501
        :type: User
        """

        self._owner = owner

    @property
    def placement(self):
        """Gets the placement of this DatasetSpec.  # noqa: E501

        Manage switch for opening Multiple datasets single node deployment or not  # noqa: E501

        :return: The placement of this DatasetSpec.  # noqa: E501
        :rtype: str
        """
        return self._placement

    @placement.setter
    def placement(self, placement):
        """Sets the placement of this DatasetSpec.

        Manage switch for opening Multiple datasets single node deployment or not  # noqa: E501

        :param placement: The placement of this DatasetSpec.  # noqa: E501
        :type: str
        """

        self._placement = placement

    @property
    def runtimes(self):
        """Gets the runtimes of this DatasetSpec.  # noqa: E501

        Runtimes for supporting dataset (e.g. AlluxioRuntime)  # noqa: E501

        :return: The runtimes of this DatasetSpec.  # noqa: E501
        :rtype: list[Runtime]
        """
        return self._runtimes

    @runtimes.setter
    def runtimes(self, runtimes):
        """Sets the runtimes of this DatasetSpec.

        Runtimes for supporting dataset (e.g. AlluxioRuntime)  # noqa: E501

        :param runtimes: The runtimes of this DatasetSpec.  # noqa: E501
        :type: list[Runtime]
        """

        self._runtimes = runtimes

    @property
    def shared_encrypt_options(self):
        """Gets the shared_encrypt_options of this DatasetSpec.  # noqa: E501

        SharedEncryptOptions is the encryptOption to all mount  # noqa: E501

        :return: The shared_encrypt_options of this DatasetSpec.  # noqa: E501
        :rtype: list[EncryptOption]
        """
        return self._shared_encrypt_options

    @shared_encrypt_options.setter
    def shared_encrypt_options(self, shared_encrypt_options):
        """Sets the shared_encrypt_options of this DatasetSpec.

        SharedEncryptOptions is the encryptOption to all mount  # noqa: E501

        :param shared_encrypt_options: The shared_encrypt_options of this DatasetSpec.  # noqa: E501
        :type: list[EncryptOption]
        """

        self._shared_encrypt_options = shared_encrypt_options

    @property
    def shared_options(self):
        """Gets the shared_options of this DatasetSpec.  # noqa: E501

        SharedOptions is the options to all mount  # noqa: E501

        :return: The shared_options of this DatasetSpec.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._shared_options

    @shared_options.setter
    def shared_options(self, shared_options):
        """Sets the shared_options of this DatasetSpec.

        SharedOptions is the options to all mount  # noqa: E501

        :param shared_options: The shared_options of this DatasetSpec.  # noqa: E501
        :type: dict(str, str)
        """

        self._shared_options = shared_options

    @property
    def tolerations(self):
        """Gets the tolerations of this DatasetSpec.  # noqa: E501

        If specified, the pod's tolerations.  # noqa: E501

        :return: The tolerations of this DatasetSpec.  # noqa: E501
        :rtype: list[V1Toleration]
        """
        return self._tolerations

    @tolerations.setter
    def tolerations(self, tolerations):
        """Sets the tolerations of this DatasetSpec.

        If specified, the pod's tolerations.  # noqa: E501

        :param tolerations: The tolerations of this DatasetSpec.  # noqa: E501
        :type: list[V1Toleration]
        """

        self._tolerations = tolerations

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
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

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, DatasetSpec):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DatasetSpec):
            return True

        return self.to_dict() != other.to_dict()
