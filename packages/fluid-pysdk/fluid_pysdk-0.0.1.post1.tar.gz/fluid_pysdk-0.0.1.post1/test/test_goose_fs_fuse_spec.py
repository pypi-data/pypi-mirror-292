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
from fluid.models.goose_fs_fuse_spec import GooseFSFuseSpec  # noqa: E501
from fluid.rest import ApiException

class TestGooseFSFuseSpec(unittest.TestCase):
    """GooseFSFuseSpec unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test GooseFSFuseSpec
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = fluid.models.goose_fs_fuse_spec.GooseFSFuseSpec()  # noqa: E501
        if include_optional :
            return GooseFSFuseSpec(
                annotations = {
                    'key' : '0'
                    }, 
                args = [
                    '0'
                    ], 
                clean_policy = '0', 
                env = {
                    'key' : '0'
                    }, 
                _global = True, 
                image = '0', 
                image_pull_policy = '0', 
                image_tag = '0', 
                jvm_options = [
                    '0'
                    ], 
                node_selector = {
                    'key' : '0'
                    }, 
                properties = {
                    'key' : '0'
                    }, 
                resources = None
            )
        else :
            return GooseFSFuseSpec(
        )

    def testGooseFSFuseSpec(self):
        """Test GooseFSFuseSpec"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
