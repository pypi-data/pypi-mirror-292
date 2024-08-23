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


class DatasetStatus(object):
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
        'cache_states': 'dict(str, str)',
        'conditions': 'list[DatasetCondition]',
        'data_backup_ref': 'str',
        'data_load_ref': 'str',
        'dataset_ref': 'list[str]',
        'file_num': 'str',
        'hcfs': 'HCFSStatus',
        'mounts': 'list[Mount]',
        'operation_ref': 'dict(str, str)',
        'phase': 'str',
        'runtimes': 'list[Runtime]',
        'ufs_total': 'str'
    }

    attribute_map = {
        'cache_states': 'cacheStates',
        'conditions': 'conditions',
        'data_backup_ref': 'dataBackupRef',
        'data_load_ref': 'dataLoadRef',
        'dataset_ref': 'datasetRef',
        'file_num': 'fileNum',
        'hcfs': 'hcfs',
        'mounts': 'mounts',
        'operation_ref': 'operationRef',
        'phase': 'phase',
        'runtimes': 'runtimes',
        'ufs_total': 'ufsTotal'
    }

    def __init__(self, cache_states=None, conditions=None, data_backup_ref=None, data_load_ref=None, dataset_ref=None, file_num=None, hcfs=None, mounts=None, operation_ref=None, phase=None, runtimes=None, ufs_total=None, local_vars_configuration=None):  # noqa: E501
        """DatasetStatus - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._cache_states = None
        self._conditions = None
        self._data_backup_ref = None
        self._data_load_ref = None
        self._dataset_ref = None
        self._file_num = None
        self._hcfs = None
        self._mounts = None
        self._operation_ref = None
        self._phase = None
        self._runtimes = None
        self._ufs_total = None
        self.discriminator = None

        if cache_states is not None:
            self.cache_states = cache_states
        self.conditions = conditions
        if data_backup_ref is not None:
            self.data_backup_ref = data_backup_ref
        if data_load_ref is not None:
            self.data_load_ref = data_load_ref
        if dataset_ref is not None:
            self.dataset_ref = dataset_ref
        if file_num is not None:
            self.file_num = file_num
        if hcfs is not None:
            self.hcfs = hcfs
        if mounts is not None:
            self.mounts = mounts
        if operation_ref is not None:
            self.operation_ref = operation_ref
        if phase is not None:
            self.phase = phase
        if runtimes is not None:
            self.runtimes = runtimes
        if ufs_total is not None:
            self.ufs_total = ufs_total

    @property
    def cache_states(self):
        """Gets the cache_states of this DatasetStatus.  # noqa: E501

        CacheStatus represents the total resources of the dataset.  # noqa: E501

        :return: The cache_states of this DatasetStatus.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._cache_states

    @cache_states.setter
    def cache_states(self, cache_states):
        """Sets the cache_states of this DatasetStatus.

        CacheStatus represents the total resources of the dataset.  # noqa: E501

        :param cache_states: The cache_states of this DatasetStatus.  # noqa: E501
        :type: dict(str, str)
        """

        self._cache_states = cache_states

    @property
    def conditions(self):
        """Gets the conditions of this DatasetStatus.  # noqa: E501

        Conditions is an array of current observed conditions.  # noqa: E501

        :return: The conditions of this DatasetStatus.  # noqa: E501
        :rtype: list[DatasetCondition]
        """
        return self._conditions

    @conditions.setter
    def conditions(self, conditions):
        """Sets the conditions of this DatasetStatus.

        Conditions is an array of current observed conditions.  # noqa: E501

        :param conditions: The conditions of this DatasetStatus.  # noqa: E501
        :type: list[DatasetCondition]
        """
        if self.local_vars_configuration.client_side_validation and conditions is None:  # noqa: E501
            raise ValueError("Invalid value for `conditions`, must not be `None`")  # noqa: E501

        self._conditions = conditions

    @property
    def data_backup_ref(self):
        """Gets the data_backup_ref of this DatasetStatus.  # noqa: E501

        DataBackupRef specifies the running Backup job that targets this Dataset. This is mainly used as a lock to prevent concurrent DataBackup jobs. Deprecated, use OperationRef instead  # noqa: E501

        :return: The data_backup_ref of this DatasetStatus.  # noqa: E501
        :rtype: str
        """
        return self._data_backup_ref

    @data_backup_ref.setter
    def data_backup_ref(self, data_backup_ref):
        """Sets the data_backup_ref of this DatasetStatus.

        DataBackupRef specifies the running Backup job that targets this Dataset. This is mainly used as a lock to prevent concurrent DataBackup jobs. Deprecated, use OperationRef instead  # noqa: E501

        :param data_backup_ref: The data_backup_ref of this DatasetStatus.  # noqa: E501
        :type: str
        """

        self._data_backup_ref = data_backup_ref

    @property
    def data_load_ref(self):
        """Gets the data_load_ref of this DatasetStatus.  # noqa: E501

        DataLoadRef specifies the running DataLoad job that targets this Dataset. This is mainly used as a lock to prevent concurrent DataLoad jobs. Deprecated, use OperationRef instead  # noqa: E501

        :return: The data_load_ref of this DatasetStatus.  # noqa: E501
        :rtype: str
        """
        return self._data_load_ref

    @data_load_ref.setter
    def data_load_ref(self, data_load_ref):
        """Sets the data_load_ref of this DatasetStatus.

        DataLoadRef specifies the running DataLoad job that targets this Dataset. This is mainly used as a lock to prevent concurrent DataLoad jobs. Deprecated, use OperationRef instead  # noqa: E501

        :param data_load_ref: The data_load_ref of this DatasetStatus.  # noqa: E501
        :type: str
        """

        self._data_load_ref = data_load_ref

    @property
    def dataset_ref(self):
        """Gets the dataset_ref of this DatasetStatus.  # noqa: E501

        DatasetRef specifies the datasets namespaced name mounting this Dataset.  # noqa: E501

        :return: The dataset_ref of this DatasetStatus.  # noqa: E501
        :rtype: list[str]
        """
        return self._dataset_ref

    @dataset_ref.setter
    def dataset_ref(self, dataset_ref):
        """Sets the dataset_ref of this DatasetStatus.

        DatasetRef specifies the datasets namespaced name mounting this Dataset.  # noqa: E501

        :param dataset_ref: The dataset_ref of this DatasetStatus.  # noqa: E501
        :type: list[str]
        """

        self._dataset_ref = dataset_ref

    @property
    def file_num(self):
        """Gets the file_num of this DatasetStatus.  # noqa: E501

        FileNum represents the file numbers of the dataset  # noqa: E501

        :return: The file_num of this DatasetStatus.  # noqa: E501
        :rtype: str
        """
        return self._file_num

    @file_num.setter
    def file_num(self, file_num):
        """Sets the file_num of this DatasetStatus.

        FileNum represents the file numbers of the dataset  # noqa: E501

        :param file_num: The file_num of this DatasetStatus.  # noqa: E501
        :type: str
        """

        self._file_num = file_num

    @property
    def hcfs(self):
        """Gets the hcfs of this DatasetStatus.  # noqa: E501


        :return: The hcfs of this DatasetStatus.  # noqa: E501
        :rtype: HCFSStatus
        """
        return self._hcfs

    @hcfs.setter
    def hcfs(self, hcfs):
        """Sets the hcfs of this DatasetStatus.


        :param hcfs: The hcfs of this DatasetStatus.  # noqa: E501
        :type: HCFSStatus
        """

        self._hcfs = hcfs

    @property
    def mounts(self):
        """Gets the mounts of this DatasetStatus.  # noqa: E501

        the info of mount points have been mounted  # noqa: E501

        :return: The mounts of this DatasetStatus.  # noqa: E501
        :rtype: list[Mount]
        """
        return self._mounts

    @mounts.setter
    def mounts(self, mounts):
        """Sets the mounts of this DatasetStatus.

        the info of mount points have been mounted  # noqa: E501

        :param mounts: The mounts of this DatasetStatus.  # noqa: E501
        :type: list[Mount]
        """

        self._mounts = mounts

    @property
    def operation_ref(self):
        """Gets the operation_ref of this DatasetStatus.  # noqa: E501

        OperationRef specifies the Operation that targets this Dataset. This is mainly used as a lock to prevent concurrent same Operation jobs.  # noqa: E501

        :return: The operation_ref of this DatasetStatus.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._operation_ref

    @operation_ref.setter
    def operation_ref(self, operation_ref):
        """Sets the operation_ref of this DatasetStatus.

        OperationRef specifies the Operation that targets this Dataset. This is mainly used as a lock to prevent concurrent same Operation jobs.  # noqa: E501

        :param operation_ref: The operation_ref of this DatasetStatus.  # noqa: E501
        :type: dict(str, str)
        """

        self._operation_ref = operation_ref

    @property
    def phase(self):
        """Gets the phase of this DatasetStatus.  # noqa: E501

        Dataset Phase. One of the four phases: `Pending`, `Bound`, `NotBound` and `Failed`  # noqa: E501

        :return: The phase of this DatasetStatus.  # noqa: E501
        :rtype: str
        """
        return self._phase

    @phase.setter
    def phase(self, phase):
        """Sets the phase of this DatasetStatus.

        Dataset Phase. One of the four phases: `Pending`, `Bound`, `NotBound` and `Failed`  # noqa: E501

        :param phase: The phase of this DatasetStatus.  # noqa: E501
        :type: str
        """

        self._phase = phase

    @property
    def runtimes(self):
        """Gets the runtimes of this DatasetStatus.  # noqa: E501

        Runtimes for supporting dataset  # noqa: E501

        :return: The runtimes of this DatasetStatus.  # noqa: E501
        :rtype: list[Runtime]
        """
        return self._runtimes

    @runtimes.setter
    def runtimes(self, runtimes):
        """Sets the runtimes of this DatasetStatus.

        Runtimes for supporting dataset  # noqa: E501

        :param runtimes: The runtimes of this DatasetStatus.  # noqa: E501
        :type: list[Runtime]
        """

        self._runtimes = runtimes

    @property
    def ufs_total(self):
        """Gets the ufs_total of this DatasetStatus.  # noqa: E501

        Total in GB of dataset in the cluster  # noqa: E501

        :return: The ufs_total of this DatasetStatus.  # noqa: E501
        :rtype: str
        """
        return self._ufs_total

    @ufs_total.setter
    def ufs_total(self, ufs_total):
        """Sets the ufs_total of this DatasetStatus.

        Total in GB of dataset in the cluster  # noqa: E501

        :param ufs_total: The ufs_total of this DatasetStatus.  # noqa: E501
        :type: str
        """

        self._ufs_total = ufs_total

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
        if not isinstance(other, DatasetStatus):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DatasetStatus):
            return True

        return self.to_dict() != other.to_dict()
