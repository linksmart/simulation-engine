import connexion
import six

from swagger_server.models.simulation import Simulation  # noqa: E501
from swagger_server.models.simulation_result import SimulationResult  # noqa: E501
from swagger_server import util


def abort_simulation(id):  # noqa: E501
    """Aborts a running simulation

    If the user of the professional GUI decides to abort a running simulation this call will be triggered # noqa: E501

    :param id: ID of the simulation that should be aborted
    :type id: str

    :rtype: None
    """
    return 'do some magic!'


def run_simulation(id, body):  # noqa: E501
    """Runs a simulation

    Runs a simulation # noqa: E501

    :param id: ID of the simulation that should be started
    :type id: str
    :param body: Configuration data for the simulation e.g. duration
    :type body: dict | bytes

    :rtype: List[SimulationResult]
    """
    if connexion.request.is_json:
        body = Simulation.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
