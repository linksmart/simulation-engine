import logging


logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


class constant:

    linecodes = [
    {
        "id":"underground_95mm",
        "r1":0.193,
        "x1":0.08,
        "c0":0,
        "units": "km"
    },
    {
        "id":"underground_50mm",
        "r1":0.37,
        "x1":0.084,
        "c0":0,
        "units": "km"
    },
    {
        "id":"underground_25mm",
        "r1":0.734,
        "x1":0.070,
        "c0":0,
        "units": "km"
    },
    {
        "id":"underground_16mm",
        "r1":1.16,
        "x1":0.07,
        "c0":0,
        "units": "km"
    },
    {
        "id":"aerial_70mm",
        "r1":0.49,
        "x1":0.271,
        "c0":0,
        "units": "km"
    },
    {
        "id":"aerial_50mm",
        "r1":0.67,
        "x1":0.282,
        "c0":0,
        "units": "km"
    },
    {
        "id":"aerial_35mm",
        "r1":0.949,
        "x1":0.293,
        "c0":0,
        "units": "km"
    }
    ]

    def __init__(self):
        logger.debug("Class Constant instantiated")