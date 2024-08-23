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


class JuiceFSCompTemplateSpec(object):
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
        'enabled': 'bool',
        'env': 'list[V1EnvVar]',
        'network_mode': 'str',
        'node_selector': 'dict(str, str)',
        'options': 'dict(str, str)',
        'pod_metadata': 'PodMetadata',
        'ports': 'list[V1ContainerPort]',
        'replicas': 'int',
        'resources': 'V1ResourceRequirements',
        'volume_mounts': 'list[V1VolumeMount]'
    }

    attribute_map = {
        'enabled': 'enabled',
        'env': 'env',
        'network_mode': 'networkMode',
        'node_selector': 'nodeSelector',
        'options': 'options',
        'pod_metadata': 'podMetadata',
        'ports': 'ports',
        'replicas': 'replicas',
        'resources': 'resources',
        'volume_mounts': 'volumeMounts'
    }

    def __init__(self, enabled=None, env=None, network_mode=None, node_selector=None, options=None, pod_metadata=None, ports=None, replicas=None, resources=None, volume_mounts=None, local_vars_configuration=None):  # noqa: E501
        """JuiceFSCompTemplateSpec - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._enabled = None
        self._env = None
        self._network_mode = None
        self._node_selector = None
        self._options = None
        self._pod_metadata = None
        self._ports = None
        self._replicas = None
        self._resources = None
        self._volume_mounts = None
        self.discriminator = None

        if enabled is not None:
            self.enabled = enabled
        if env is not None:
            self.env = env
        if network_mode is not None:
            self.network_mode = network_mode
        if node_selector is not None:
            self.node_selector = node_selector
        if options is not None:
            self.options = options
        if pod_metadata is not None:
            self.pod_metadata = pod_metadata
        if ports is not None:
            self.ports = ports
        if replicas is not None:
            self.replicas = replicas
        if resources is not None:
            self.resources = resources
        if volume_mounts is not None:
            self.volume_mounts = volume_mounts

    @property
    def enabled(self):
        """Gets the enabled of this JuiceFSCompTemplateSpec.  # noqa: E501

        Enabled or Disabled for the components.  # noqa: E501

        :return: The enabled of this JuiceFSCompTemplateSpec.  # noqa: E501
        :rtype: bool
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        """Sets the enabled of this JuiceFSCompTemplateSpec.

        Enabled or Disabled for the components.  # noqa: E501

        :param enabled: The enabled of this JuiceFSCompTemplateSpec.  # noqa: E501
        :type: bool
        """

        self._enabled = enabled

    @property
    def env(self):
        """Gets the env of this JuiceFSCompTemplateSpec.  # noqa: E501

        Environment variables that will be used by JuiceFS component.  # noqa: E501

        :return: The env of this JuiceFSCompTemplateSpec.  # noqa: E501
        :rtype: list[V1EnvVar]
        """
        return self._env

    @env.setter
    def env(self, env):
        """Sets the env of this JuiceFSCompTemplateSpec.

        Environment variables that will be used by JuiceFS component.  # noqa: E501

        :param env: The env of this JuiceFSCompTemplateSpec.  # noqa: E501
        :type: list[V1EnvVar]
        """

        self._env = env

    @property
    def network_mode(self):
        """Gets the network_mode of this JuiceFSCompTemplateSpec.  # noqa: E501

        Whether to use hostnetwork or not  # noqa: E501

        :return: The network_mode of this JuiceFSCompTemplateSpec.  # noqa: E501
        :rtype: str
        """
        return self._network_mode

    @network_mode.setter
    def network_mode(self, network_mode):
        """Sets the network_mode of this JuiceFSCompTemplateSpec.

        Whether to use hostnetwork or not  # noqa: E501

        :param network_mode: The network_mode of this JuiceFSCompTemplateSpec.  # noqa: E501
        :type: str
        """

        self._network_mode = network_mode

    @property
    def node_selector(self):
        """Gets the node_selector of this JuiceFSCompTemplateSpec.  # noqa: E501

        NodeSelector is a selector  # noqa: E501

        :return: The node_selector of this JuiceFSCompTemplateSpec.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._node_selector

    @node_selector.setter
    def node_selector(self, node_selector):
        """Sets the node_selector of this JuiceFSCompTemplateSpec.

        NodeSelector is a selector  # noqa: E501

        :param node_selector: The node_selector of this JuiceFSCompTemplateSpec.  # noqa: E501
        :type: dict(str, str)
        """

        self._node_selector = node_selector

    @property
    def options(self):
        """Gets the options of this JuiceFSCompTemplateSpec.  # noqa: E501

        Options  # noqa: E501

        :return: The options of this JuiceFSCompTemplateSpec.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._options

    @options.setter
    def options(self, options):
        """Sets the options of this JuiceFSCompTemplateSpec.

        Options  # noqa: E501

        :param options: The options of this JuiceFSCompTemplateSpec.  # noqa: E501
        :type: dict(str, str)
        """

        self._options = options

    @property
    def pod_metadata(self):
        """Gets the pod_metadata of this JuiceFSCompTemplateSpec.  # noqa: E501


        :return: The pod_metadata of this JuiceFSCompTemplateSpec.  # noqa: E501
        :rtype: PodMetadata
        """
        return self._pod_metadata

    @pod_metadata.setter
    def pod_metadata(self, pod_metadata):
        """Sets the pod_metadata of this JuiceFSCompTemplateSpec.


        :param pod_metadata: The pod_metadata of this JuiceFSCompTemplateSpec.  # noqa: E501
        :type: PodMetadata
        """

        self._pod_metadata = pod_metadata

    @property
    def ports(self):
        """Gets the ports of this JuiceFSCompTemplateSpec.  # noqa: E501

        Ports used by JuiceFS  # noqa: E501

        :return: The ports of this JuiceFSCompTemplateSpec.  # noqa: E501
        :rtype: list[V1ContainerPort]
        """
        return self._ports

    @ports.setter
    def ports(self, ports):
        """Sets the ports of this JuiceFSCompTemplateSpec.

        Ports used by JuiceFS  # noqa: E501

        :param ports: The ports of this JuiceFSCompTemplateSpec.  # noqa: E501
        :type: list[V1ContainerPort]
        """

        self._ports = ports

    @property
    def replicas(self):
        """Gets the replicas of this JuiceFSCompTemplateSpec.  # noqa: E501

        Replicas is the desired number of replicas of the given template. If unspecified, defaults to 1. replicas is the min replicas of dataset in the cluster  # noqa: E501

        :return: The replicas of this JuiceFSCompTemplateSpec.  # noqa: E501
        :rtype: int
        """
        return self._replicas

    @replicas.setter
    def replicas(self, replicas):
        """Sets the replicas of this JuiceFSCompTemplateSpec.

        Replicas is the desired number of replicas of the given template. If unspecified, defaults to 1. replicas is the min replicas of dataset in the cluster  # noqa: E501

        :param replicas: The replicas of this JuiceFSCompTemplateSpec.  # noqa: E501
        :type: int
        """

        self._replicas = replicas

    @property
    def resources(self):
        """Gets the resources of this JuiceFSCompTemplateSpec.  # noqa: E501


        :return: The resources of this JuiceFSCompTemplateSpec.  # noqa: E501
        :rtype: V1ResourceRequirements
        """
        return self._resources

    @resources.setter
    def resources(self, resources):
        """Sets the resources of this JuiceFSCompTemplateSpec.


        :param resources: The resources of this JuiceFSCompTemplateSpec.  # noqa: E501
        :type: V1ResourceRequirements
        """

        self._resources = resources

    @property
    def volume_mounts(self):
        """Gets the volume_mounts of this JuiceFSCompTemplateSpec.  # noqa: E501

        VolumeMounts specifies the volumes listed in \".spec.volumes\" to mount into runtime component's filesystem.  # noqa: E501

        :return: The volume_mounts of this JuiceFSCompTemplateSpec.  # noqa: E501
        :rtype: list[V1VolumeMount]
        """
        return self._volume_mounts

    @volume_mounts.setter
    def volume_mounts(self, volume_mounts):
        """Sets the volume_mounts of this JuiceFSCompTemplateSpec.

        VolumeMounts specifies the volumes listed in \".spec.volumes\" to mount into runtime component's filesystem.  # noqa: E501

        :param volume_mounts: The volume_mounts of this JuiceFSCompTemplateSpec.  # noqa: E501
        :type: list[V1VolumeMount]
        """

        self._volume_mounts = volume_mounts

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
        if not isinstance(other, JuiceFSCompTemplateSpec):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, JuiceFSCompTemplateSpec):
            return True

        return self.to_dict() != other.to_dict()
