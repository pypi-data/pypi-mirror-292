# coding: utf-8

"""
    fluid

    client for fluid  # noqa: E501

    The version of the OpenAPI document: v0.1
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import datetime

import fluid
from fluid.models.juice_fs_runtime import JuiceFSRuntime  # noqa: E501
from fluid.rest import ApiException

class TestJuiceFSRuntime(unittest.TestCase):
    """JuiceFSRuntime unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test JuiceFSRuntime
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = fluid.models.juice_fs_runtime.JuiceFSRuntime()  # noqa: E501
        if include_optional :
            return JuiceFSRuntime(
                api_version = '0', 
                kind = '0', 
                metadata = None, 
                spec = fluid.models./juice_fs_runtime_spec..JuiceFSRuntimeSpec(
                    clean_cache_policy = fluid.models./clean_cache_policy..CleanCachePolicy(
                        grace_period_seconds = 56, 
                        max_retry_attempts = 56, ), 
                    configs = [
                        '0'
                        ], 
                    disable_prometheus = True, 
                    fuse = fluid.models./juice_fs_fuse_spec..JuiceFSFuseSpec(
                        clean_policy = '0', 
                        env = [
                            None
                            ], 
                        global = True, 
                        image = '0', 
                        image_pull_policy = '0', 
                        image_tag = '0', 
                        network_mode = '0', 
                        node_selector = {
                            'key' : '0'
                            }, 
                        options = {
                            'key' : '0'
                            }, 
                        pod_metadata = fluid.models./pod_metadata..PodMetadata(
                            annotations = {
                                'key' : '0'
                                }, 
                            labels = {
                                'key' : '0'
                                }, ), 
                        resources = None, 
                        volume_mounts = [
                            None
                            ], ), 
                    init_users = fluid.models./init_users_spec..InitUsersSpec(
                        image = '0', 
                        image_pull_policy = '0', 
                        image_tag = '0', 
                        resources = None, ), 
                    job_worker = fluid.models./juice_fs_comp_template_spec..JuiceFSCompTemplateSpec(
                        enabled = True, 
                        network_mode = '0', 
                        ports = [
                            None
                            ], 
                        replicas = 56, 
                        resources = None, ), 
                    juicefs_version = fluid.models./version_spec..VersionSpec(
                        image = '0', 
                        image_pull_policy = '0', 
                        image_tag = '0', ), 
                    master = fluid.models./juice_fs_comp_template_spec..JuiceFSCompTemplateSpec(
                        enabled = True, 
                        network_mode = '0', 
                        replicas = 56, 
                        resources = None, ), 
                    pod_metadata = fluid.models./pod_metadata..PodMetadata(), 
                    replicas = 56, 
                    run_as = fluid.models./user..User(
                        gid = 56, 
                        group = '0', 
                        uid = 56, 
                        user = '0', ), 
                    tieredstore = fluid.models./tiered_store..TieredStore(
                        levels = [
                            fluid.models./level..Level(
                                high = '0', 
                                low = '0', 
                                mediumtype = '0', 
                                path = '0', 
                                quota = None, 
                                quota_list = '0', 
                                volume_source = fluid.models./volume_source..VolumeSource(
                                    aws_elastic_block_store = None, 
                                    azure_disk = None, 
                                    azure_file = None, 
                                    cephfs = None, 
                                    cinder = None, 
                                    config_map = None, 
                                    csi = None, 
                                    downward_api = None, 
                                    empty_dir = None, 
                                    ephemeral = None, 
                                    fc = None, 
                                    flex_volume = None, 
                                    flocker = None, 
                                    gce_persistent_disk = None, 
                                    git_repo = None, 
                                    glusterfs = None, 
                                    host_path = None, 
                                    iscsi = None, 
                                    nfs = None, 
                                    persistent_volume_claim = None, 
                                    photon_persistent_disk = None, 
                                    portworx_volume = None, 
                                    projected = None, 
                                    quobyte = None, 
                                    rbd = None, 
                                    scale_io = None, 
                                    secret = None, 
                                    storageos = None, 
                                    vsphere_volume = None, ), 
                                volume_type = '0', )
                            ], ), 
                    volumes = [
                        None
                        ], 
                    worker = fluid.models./juice_fs_comp_template_spec..JuiceFSCompTemplateSpec(
                        enabled = True, 
                        network_mode = '0', 
                        replicas = 56, 
                        resources = None, ), ), 
                status = fluid.models./runtime_status..RuntimeStatus(
                    api_gateway = fluid.models./api_gateway_status..APIGatewayStatus(
                        endpoint = '0', ), 
                    cache_affinity = None, 
                    cache_states = {
                        'key' : '0'
                        }, 
                    conditions = [
                        fluid.models./runtime_condition..RuntimeCondition(
                            last_probe_time = None, 
                            last_transition_time = None, 
                            message = '0', 
                            reason = '0', 
                            status = '0', 
                            type = '0', )
                        ], 
                    current_fuse_number_scheduled = 56, 
                    current_master_number_scheduled = 56, 
                    current_worker_number_scheduled = 56, 
                    desired_fuse_number_scheduled = 56, 
                    desired_master_number_scheduled = 56, 
                    desired_worker_number_scheduled = 56, 
                    fuse_number_available = 56, 
                    fuse_number_ready = 56, 
                    fuse_number_unavailable = 56, 
                    fuse_phase = '0', 
                    fuse_reason = '0', 
                    master_number_ready = 56, 
                    master_phase = '0', 
                    master_reason = '0', 
                    mount_time = None, 
                    mounts = [
                        fluid.models./mount..Mount(
                            encrypt_options = [
                                fluid.models./encrypt_option..EncryptOption(
                                    name = '0', 
                                    value_from = fluid.models./encrypt_option_source..EncryptOptionSource(
                                        secret_key_ref = fluid.models./secret_key_selector..SecretKeySelector(
                                            key = '0', 
                                            name = '0', ), ), )
                                ], 
                            mount_point = '0', 
                            name = '0', 
                            options = {
                                'key' : '0'
                                }, 
                            path = '0', 
                            read_only = True, 
                            shared = True, )
                        ], 
                    selector = '0', 
                    setup_duration = '0', 
                    value_file = '0', 
                    worker_number_available = 56, 
                    worker_number_ready = 56, 
                    worker_number_unavailable = 56, 
                    worker_phase = '0', 
                    worker_reason = '0', )
            )
        else :
            return JuiceFSRuntime(
        )

    def testJuiceFSRuntime(self):
        """Test JuiceFSRuntime"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
