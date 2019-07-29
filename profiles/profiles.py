"""
Created by Saba khan: July 16 2019
"""

import datetime
import logging
import requests
import time
logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


class Profiles:

    def __init__(self):
        self.url = ""

    def price_profile(self, city, country, days=365):
        """
        Returns the price profile for the given number of days for bolzano, Italy or fur, Denmark.
        Args:
            city(String): variable to enter a city.
            country(String): variable to enter a country.
            days(int): number of days.

        Returns:
            list: length of list = number of days * 24
        """
        base_url = "http://10.8.0.50:18081"
        if(not(city) or not(country)):
            logger.error("\nPlease provide both city and country name, currenty we support price calculation for Bolzano,Italy and Fur,Denmark")
            return None
        no_of_years = 0
        extra_days = 0
        if(days > 365):
            no_of_years = int(days / 365)
            extra_days = days % 365
            days = 365
        start_date = datetime.datetime.now()+ datetime.timedelta(days = -365)
        end_date = (start_date + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        start_date = start_date.strftime("%Y-%m-%d")

        if(city.lower() in ["bolzano", "fur"] and country.lower() in ["italy","denmark"]):
            if(city.lower() == "bolzano" and country.lower() == "italy"):
                latitude = "46.12"
                longitude = "11.12"
                self.url = base_url + "/" + latitude + "," + longitude + "/prices/" + start_date + "/" + end_date
            elif (city.lower() == "fur" and country.lower() == "denmark"):
                latitude = "56.82"
                longitude = "9.00"
                self.url = base_url + "/" + latitude + "," + longitude + "/prices/" + start_date + "/" + end_date
        else:
            logger.error("Currenty we support price calculation for Bolzano,Italy and Fur,Denmark")
            return None
        try:
            logger.debug(self.url)
            data = requests.get(self.url)
            if data:
                data = data.json()
            else:
                return None
        except Exception as e:
            logger.error(str(e))
            return None

        price_list = []
        if data is not None:
            data_list = []
            time_series = data["Publication_MarketDocument"]["TimeSeries"]
            if isinstance(time_series, list):
                for time_frame in range(len(time_series) - 1):
                    for point in time_series[time_frame]["Period"]["Point"]:
                        price = float(point["price.amount"]) / 1000  # Price calculated per KWh
                        data_list.append(price)

            price_list = data_list.copy()
            for year in range(no_of_years-1):
                price_list.extend(data_list)
            price_list.extend(data_list[0:extra_days*24])
            logger.info("Price data = %s: ", price_list)
        return price_list

    def pv_profile(self, city, country, days = 365):
        """
        Returns the pv profile for the given number of days
        Args:
            city(String): variable to enter a city.
            country(String): variable to enter a country.
            days(int): number of days.

        Returns:
            list: Number of elements = number of days * 24
        """

        if (not (city) or not (country)):
            logger.error(
                "\nPlease provide both city and country name, currenty we support price calculation for Bolzano,Italy and Fur,Denmark")
            return None
        lat =0
        lon =0
        if (city.lower() == "bolzano" and country.lower() == "italy"):
            lat = "46.12"
            lon = "11.12"

        elif (city.lower() == "fur" and country.lower() == "denmark"):
            lat = "56.82"
            lon = "9.00"
        logger.info("coord " + str(lat) + ", " + str(lon))
        try:
            if lat is not None and lon is not None:
                rad = requests.get("http://re.jrc.ec.europa.eu/pvgis5/seriescalc.php?lat=" +
                                   "{:.3f}".format(float(lat)) + "&lon=" + "{:.3f}".format(
                    float(lon)) + "&raddatabase=" +
                                   "PVGIS-CMSAF&usehorizon=1&startyear=2016&endyear=2016&mountingplace=free&" +
                                   "optimalinclination=0&optimalangles=1&hourlyoptimalangles=1&PVcalculation=1&" +
                                   "pvtechchoice=crystSi&peakpower=" + str(1) + "&loss=14&components=1")
                red_arr = str(rad.content).split("\\n")
                for x in range(11):
                    del red_arr[0]
                rad = []
                for x in range(0, red_arr.__len__()):
                    w = red_arr[x][:-2].split(",")
                    if w.__len__() != 9:
                        break

                    rad.append(w)

                rad = rad[0:365 * 24]
                no_of_years = 0
                if (days > 365):
                    no_of_years = int(days / 365)
                    days = days % 365
                data = []
                for i in range(0, len(rad)):
                    pv_output = float(rad[i][1])
                    data.append(pv_output)
                pv_list = []
                for i in range(no_of_years):
                    pv_list.extend(data)
                pv_list.extend(data[0:days * 24])
                logger.info("PV data = %s: ", pv_list)
                return pv_list
        except Exception as e:
            logger.error(str(e))


    def load_profile(self, type= "commercial", randint=0,  days=365):
        """
        Returns the load profile for the number of days given
        Note: Need residential and/or commercial files stored in load_profiles folder.
        Args:
            type(String): either commercial or residential.
            randint(int): Range: 0 to 50. To chose the residential profiles file. e.g: 2 for profiles_2.txt
            days(int): number of days.

        Returns:
            list: Number of elements = number of days * 24
        """
        if(randint > 50 or randint < 0):
            logger.debug("Please provide randint values between 0-50")
            return

        if(type == "residential"):
            file_path = "load_profiles/residential/profiles_" + str(randint) + ".txt"
            with open(file_path, "r") as file:
                data = file.readlines()
                data_list = [float(i)for i in data]
        else:
            with open("load_profiles/commercial/commercial_general.txt", "r") as file:
                data = file.readlines()
                data_list = [float(i) for i in data]
                data_list.extend(data_list[-24:])

        no_of_years = 0
        if (days > 365):
            no_of_years = int(days / 365)
            days = days % 365
        load_list = []
        for i in range(no_of_years):
            load_list.extend(data_list)
        load_list.extend(data_list[0:days * 24])
        logger.info("Load data = %s: ",load_list)
        return load_list

if __name__ == "__main__":
    prof = Profiles()
    pv_profile_data = prof.pv_profile("bolzano", "italy", days=365)
    load_profile_data = prof.load_profile(type="commercial", randint=0, days=365)
    t_end = time.time() + 60
    days = 1
    while time.time() < t_end:
        prof.price_profile("fur","denmark", days)
        days = days + 1
        time.sleep(5)
