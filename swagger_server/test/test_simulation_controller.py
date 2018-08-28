# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.grid import Grid  # noqa: E501
from swagger_server.test import BaseTestCase


class TestSimulationController(BaseTestCase):
    """SimulationController integration test stubs"""

    def test_create_simulation(self):
        """Test case for create_simulation

        Send grid data to simulation engine in order to create a new simulation
        """
        body = Grid()
        response = self.client.open(
            '/se/simulation',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_simulation(self):
        """Test case for delete_simulation

        Delete a simulation and its data
        """
        response = self.client.open(
            '/se/simulation/{id}'.format(id='id_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_simulation(self):
        """Test case for update_simulation

        Send new data to an existing simulation
        """
        body = Grid()
        response = self.client.open(
            '/se/simulation/{id}'.format(id='id_example'),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
