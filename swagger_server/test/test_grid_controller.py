# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.transformer import Transformer  # noqa: E501
from swagger_server.test import BaseTestCase


class TestGridController(BaseTestCase):
    """GridController integration test stubs"""

    def test_get_grid(self):
        """Test case for get_grid

        Get the full grid topology
        """
        response = self.client.open(
            '/se/grid/{locationName}'.format(locationName='locationName_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
