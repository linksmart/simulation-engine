# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.radial import Radial  # noqa: E501
from swagger_server.test import BaseTestCase


class TestRadialController(BaseTestCase):
    """RadialController integration test stubs"""

    def test_add_radial(self):
        """Test case for add_radial

        Send a single radial to the simulation engine for simulation
        """
        body = Radial()
        response = self.client.open(
            '/se/radial',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_radial(self):
        """Test case for delete_radial

        Delete a radial
        """
        response = self.client.open(
            '/se/radial/{radialId}'.format(radialId='radialId_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_radial(self):
        """Test case for update_radial

        Update a single radial
        """
        body = Radial()
        response = self.client.open(
            '/se/radial/{radialId}'.format(radialId='radialId_example'),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
