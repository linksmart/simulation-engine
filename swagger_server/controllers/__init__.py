from swagger_server.controllers.commands_controller import CommandController
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

#variable = CommandController()
logger.debug("Variable instantiated")