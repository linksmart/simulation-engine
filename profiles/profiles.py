import datetime
import time
import logging
import requests
logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Profiles:
    def __init__(self):
        self.url = ""

    def price_calculator(self, city, country, total_days, type_location="commercial"):

        base_url = "http://10.8.0.50:18081"

        if(not(city) or not(country)):
            logger.error("\nPlease provide both city and country name, currenty we support price calculation for Bolzano,Italy and Fur,Denmark")
            return None

        no_of_years = 0
        extra_days = 0
        if(total_days > 365):
            no_of_years = int(total_days / 365)
            extra_days = total_days % 365
            total_days = 365
        start_date = datetime.datetime.now()+ datetime.timedelta(days = -365)
        end_date = (start_date + datetime.timedelta(days=total_days)).strftime("%Y-%m-%d")
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
                for time_frame in time_series:
                    for point in time_frame["Period"]["Point"]:
                        price = round(float(point["price.amount"])/1000, 5)  # Price calculated per KWh
                        data_list.append(price)

            price_list = data_list.copy()
            for year in range(no_of_years-1):
                price_list.extend(data_list)
            price_list.extend(data_list[0:extra_days*24])
            logger.debug("Price data size = ", len(price_list))
            logger.debug("Price data = ", price_list)
        return price_list


    def pv(self, lat=50.7374, lon=7.0982, days = 365):
        rad_data = []
        logger.info("coord " + str(lat) + ", " + str(lon))
        if lat is not None and lon is not None:
            rad = requests.get("http://re.jrc.ec.europa.eu/pvgis5/seriescalc.php?lat=" +
                               "{:.3f}".format(float(lat)) + "&lon=" + "{:.3f}".format(float(lon)) + "&raddatabase=" +
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
            rad = rad[0:days*24]
            data = []
            for i in range(0, len(rad)):
                date = rad[i][0]
                #timestamp = date.timestamp()
                pv_output = float(rad[i][1])
                data.append( pv_output)
            print("***Data length****", len(data))
            print(data)
            return data


"""if __name__ == "__main__":
    prof = Profiles()
    t_end = time.time() + 60 * 15
    day = 1
    while time.time() < t_end:
        prof.price_calculator("fur","denmark", day, "commercial")
        day = day + 1
        time.sleep(5)"""

prof = Profiles()
prof.pv(days=100)