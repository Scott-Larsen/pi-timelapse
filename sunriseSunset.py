#! usr/bin/python3

import os
import sys
import requests
import yaml
from datetime import datetime, timedelta, date
from pytz import timezone, utc
from timezonefinder import TimezoneFinder
import time
from config import GPS_LOCATION  # , API_KEY


config = yaml.safe_load(open(os.path.join(sys.path[0], "config.yml")))

latitude, longitude = GPS_LOCATION


def getSunriseSunsetDateTimes():
    sunrise_sunsetRequest = (
        "https://api.sunrise-sunset.org/json?lat="
        + str(latitude)
        + "&lng="
        + str(longitude)
        + "&formatted=0"
    )

    response = requests.get(sunrise_sunsetRequest)

    sunriseSunset = response.json()["results"]

    sunrise = sunriseSunset["sunrise"]
    sunset = sunriseSunset["sunset"]

    sunriseDateTime = datetime.fromisoformat(sunrise)
    sunsetDateTime = datetime.fromisoformat(sunset)

    return sunriseDateTime, sunsetDateTime


def get_utc_offset():
    """
    returns a location's time zone offset from UTC in minutes.
    """

    tf = TimezoneFinder()
    today = datetime.now()
    tz_target = timezone(tf.certain_timezone_at(lng=longitude, lat=latitude))
    today_target = tz_target.localize(today)
    today_utc = utc.localize(today)
    return (today_utc - today_target).total_seconds() / 60


def calculateStartTimeAndEndTimes():
    """
    returns the more constrained of sunrise and workingStart and sunset and workingFinish
    """

    utcOffset = get_utc_offset()
    workingStart = config["workingStart"]
    workingFinish = config["workingFinish"]
    utc_now = utc.localize(datetime.utcnow())
    workingStart = workingStart.split(":")
    workingFinish = workingFinish.split(":")
    workStart = utc_now.replace(
        hour=int(workingStart[0]), minute=int(workingStart[1]), second=0, microsecond=0,
    )
    workFinish = utc_now.replace(
        hour=int(workingFinish[0]),
        minute=int(workingFinish[1]),
        second=0,
        microsecond=0,
    )
    utcDelta = timedelta(minutes=utcOffset)
    workStart = workStart - utcDelta
    workFinish = workFinish - utcDelta

    sunriseDateTime, sunsetDateTime = getSunriseSunsetDateTimes()

    return max(workStart, sunriseDateTime), min(workFinish, sunsetDateTime)


print(calculateStartTimeAndEndTimes())

#     currentDate = str(date.today())

#     # epoch_time = int(time.time())

#     # googleMapsTimeZoneAPI = (
#     #     "https://maps.googleapis.com/maps/api/timezone/json?location="
#     #     + str(latitude)
#     #     + ","
#     #     + str(longitude)
#     #     + "&timestamp="
#     #     + str(epoch_time)
#     #     + "&key="
#     #     + API_KEY
#     # )

#     # timeZoneResponse = requests.get(googleMapsTimeZoneAPI)

#     # timeZoneInfo = timeZoneResponse.json()

#     # dstOffset = timeZoneInfo["dstOffset"]
#     # rawOffset = timeZoneInfo["rawOffset"]

#     workingStart24Hour = config["workingStart"]
#     workingFinish24Hour = config["workingFinish"]

#     def convert24HourToDecimal(twentyFourHourTime: str) -> float:
#         twentyFourHourTime = str(twentyFourHourTime)
#         twentyFourHourTime = twentyFourHourTime.split(":")

#         return int(twentyFourHourTime[0]) + float(twentyFourHourTime[1]) / 60

#     assert convert24HourToDecimal("13:30") == 13.5

#     workingStartFloat = convert24HourToDecimal(workingStart24Hour)
#     workingFinishFloat = convert24HourToDecimal(workingFinish24Hour)

#     def convertDecimalTo24Hour(decimalTime: float) -> str:
#         decimalTime = str(decimalTime)
#         decimalTime = decimalTime.split(".")
#         return str(decimalTime[0] + ":" + str(int(float("0." + decimalTime[1]) * 60)))

#     assert convertDecimalTo24Hour(13.5) == "13:30"

#     workingStart = convertDecimalTo24Hour(
#         workingStartFloat + dstOffset / 60 / 60 - rawOffset / 60 / 60
#     )

#     workingFinish = convertDecimalTo24Hour(
#         workingFinishFloat + dstOffset / 60 / 60 - rawOffset / 60 / 60
#     )

#     from dateutil.parser import parse

#     workingStartDatetime = parse(currentDate + " " + workingStart + "+00:00")
#     workingFinishDatetime = parse(currentDate + " " + workingFinish + "+00:00")

#     sunriseDateTime, sunsetDateTime = getSunriseSunsetDateTimes()

#     earliestStart = max(sunriseDateTime, workingStartDatetime)
#     latestFinish = min(sunsetDateTime, workingFinishDatetime)

#     return earliestStart, latestFinish


# if __name__ == "__main__":
#     print(get_utc_offset(latitude, longitude))
#     # bergamo = dict({"lat": 45.69, "lng": 9.67})
#     # print(offset(bergamo))
