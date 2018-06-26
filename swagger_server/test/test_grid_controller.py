# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.coordinates import Coordinates  # noqa: E501
from swagger_server.models.grid import Grid  # noqa: E501
from swagger_server.test import BaseTestCase


class TestGridController(BaseTestCase):
    """GridController integration test stubs"""

    def test_create_grid(self):
        """Test case for create_grid

        Insert grid components
        """
        body = Grid()
        response = self.client.open(
            '/simulation/grid',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_storage(self):
        """Test case for delete_storage

        Delete storage
        """
        body = Grid()
        response = self.client.open(
            '/simulation/grid/{id}'.format(id=789),
            method='DELETE',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_grid(self):
        """Test case for get_grid

        Get a grid topology
        """
        coordinates = Coordinates()
        response = self.client.open(
            '/simulation/grid/{id}'.format(id=789),
            method='GET',
            data=json.dumps(coordinates),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_storage(self):
        """Test case for update_storage

        Updated storage
        """
        body = Grid()
        response = self.client.open(
            '/simulation/grid/{id}'.format(id=789),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
