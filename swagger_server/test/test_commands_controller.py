# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.simulation import Simulation  # noqa: E501
from swagger_server.models.simulation_result import SimulationResult  # noqa: E501
from swagger_server.test import BaseTestCase


class TestCommandsController(BaseTestCase):
    """CommandsController integration test stubs"""

    def test_abort_simulation(self):
        """Test case for abort_simulation

        Aborts a running simulation
        """
        response = self.client.open(
            '/se/commands/abort/{id}'.format(id='id_example'),
            method='POST')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_run_simulation(self):
        """Test case for run_simulation

        Runs a simulation
        """
        body = Simulation()
        response = self.client.open(
            '/se/commands/run/{id}'.format(id='id_example'),
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
