import connexion
import six

from swagger_server.models.radial import Radial  # noqa: E501
from swagger_server import util


xycurves=[

    {
        "id":"panel_temp_eff",
        "npts":4,
        "xarray":[
            0,
            25,
            75,
            100
        ],
        "yarray":[
            1.2,
            1.0,
            0.8,
            0.6
        ]
    },
    {
        "id":"panel_absorb_eff",
        "npts":4,
        "xarray":[
            0.1,
            0.2,
            0.4,
            1.0
        ],
        "yarray":[
            0.86,
            0.9,
            0.93,
            0.97
        ]
    }

]

loadshapes = [

    {
        "id":"assumed_irrad",
        "npts":24,
        "interval":1,
        "mult":[
            0,
            0,
            0,
            0,
            0,
            0,
            0.1,
            0.2,
            0.3,
            0.5,
            0.8,
            0.9,
            1.0,
            1.0,
            0.99,
            0.9,
            0.7,
            0.4,
            0.1,
            0,
            0,
            0,
            0,
            0
        ]
    }

]

tshapes = [

    {
        "id":"assumed_Temp",
        "npts":24,
        "interval":1,
        "mult":[
            10,
            10,
            10,
            10,
            10,
            10,
            12,
            15,
            20,
            25,
            30,
            30,
            32,
            32,
            30,
            28,
            27,
            26,
            25,
            20,
            18,
            15,
            13,
            12
        ]
    }

]

def add_radial(body):  # noqa: E501
    """Send a single radial to the simulation engine for simulation

     # noqa: E501

    :param body: Radial to be simulated
    :type body: dict | bytes

    :rtype: None
    """

    if connexion.request.is_json:
        logger.debug("Post radial request")
        body = Radial.from_dict(connexion.request.get_json()).to_dict()  # noqa: E501
        logger.info("This is the dictionary: "+ str(body))
        gridController= gControl()
        if "loads" in body.keys() and body["loads"] is not None:
            #body=body.to_dict()
            load=body["loads"]
            gridController.setLoads(load)
        if "transformer" in body.keys() and body["transformer"] is not None:
            transformer=body["transformer"]
            gridController.setTransformers(transformer)
        if "power_lines" in body.keys() and body["power_lines"] is not None \
                and "linecode" in body.keys() and body["linecode"] is not None:
            powerlines = body["power_lines"]
            linecodes =  body["linecode"]
            gridController.setPowerLines(powerlines, linecodes)
        if "photovoltaics" in body.keys() and body["photovoltaics"] is not None:
                """and "xycurves" in body.keys() and body["xycurves"] is not None 
                and "loadshapes" in body.keys() and body["loadshapes"] is not None 
                and "tshapes" in body.keys() and body["tshapes"] is not None: 
                """
            photovoltaics = body["photovoltaics"]
            #xycurves = body["xycurves"]
            #loadshapes = body["loadshapes"]
            #tshapes = body["tshapes"]
            gridController.setPhotovoltaic(photovoltaics, xycurves, loadshapes, tshapes)

        if "storage_units" in body.keys() and body["storage_units"] is not None:
        #body=body.to_dict()
            storage=body["storage_units"]
            gridController.setStorage(storage)
        if "chargingPoints" in body.keys() and body["chargingPoints"] is not None:
        #body=body.to_dict()
            chargingPoints=body["chargingPoints"]
            gridController.setChargingPoints(chargingPoints)
        return "OK"
    else:
        return "Bad JSON Format"


def delete_radial(radialId):  # noqa: E501
    """Delete a radial

     # noqa: E501

    :param radialId: Id of the radial
    :type radialId: str

    :rtype: None
    """
    return 'do some magic!'


def update_radial(radialId, body):  # noqa: E501
    """Update a single radial

     # noqa: E501

    :param radialId: Id of the radial
    :type radialId: str
    :param body: Updated
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Radial.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
