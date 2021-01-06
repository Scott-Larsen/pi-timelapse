#! usr/bin/python3

import os
import sys
import requests
import yaml
from datetime import datetime, date
import time
from config import API_KEY, GPS_LOCATION


def calculateStartTimeAndEndTimes():

    config = yaml.safe_load(open(os.path.join(sys.path[0], "config.yml")))

    latitude, longitude = GPS_LOCATION

    currentDate = str(date.today())

    epoch_time = int(time.time())

    googleMapsTimeZoneAPI = (
        "https://maps.googleapis.com/maps/api/timezone/json?location="
        + str(latitude)
        + ","
        + str(longitude)
        + "&timestamp="
        + str(epoch_time)
        + "&key="
        + API_KEY
    )

    timeZoneResponse = requests.get(googleMapsTimeZoneAPI)

    timeZoneInfo = timeZoneResponse.json()

    dstOffset = timeZoneInfo["dstOffset"]
    rawOffset = timeZoneInfo["rawOffset"]

    sunrise_sunsetRequest = (
        "https://api.sunrise-sunset.org/json?lat="
        + str(latitude)
        + "&lng="
        + str(longitude)
        + "&formatted=0"
    )

    response = requests.get(sunrise_sunsetRequest)

    sunriseSunset = response.json()["results"]

    sunriseTime = sunriseSunset["sunrise"]
    sunsetTime = sunriseSunset["sunset"]

    sunriseDateTime = datetime.fromisoformat(sunriseTime)
    sunsetDateTime = datetime.fromisoformat(sunsetTime)

    interval = config["interval"]

    workingStart24Hour = config["workingStart"]
    workingFinish24Hour = config["workingFinish"]

    def convert24HourToDecimal(twentyFourHourTime: str) -> float:
        twentyFourHourTime = str(twentyFourHourTime)
        twentyFourHourTime = twentyFourHourTime.split(":")

        return int(twentyFourHourTime[0]) + float(twentyFourHourTime[1]) / 60

    assert convert24HourToDecimal("13:30") == 13.5

    workingStartFloat = convert24HourToDecimal(workingStart24Hour)
    workingFinishFloat = convert24HourToDecimal(workingFinish24Hour)

    def convertDecimalTo24Hour(decimalTime: float) -> str:
        decimalTime = str(decimalTime)
        decimalTime = decimalTime.split(".")
        return str(decimalTime[0] + ":" + str(int(float("0." + decimalTime[1]) * 60)))

    assert convertDecimalTo24Hour(13.5) == "13:30"

    workingStart = convertDecimalTo24Hour(
        workingStartFloat + dstOffset / 60 / 60 - rawOffset / 60 / 60
    )

    workingFinish = convertDecimalTo24Hour(
        workingFinishFloat + dstOffset / 60 / 60 - rawOffset / 60 / 60
    )

    from dateutil.parser import parse

    workingStartDatetime = parse(currentDate + " " + workingStart + "+00:00")
    workingFinishDatetime = parse(currentDate + " " + workingFinish + "+00:00")

    earliestStart = max(sunriseDateTime, workingStartDatetime)
    latestFinish = min(sunsetDateTime, workingFinishDatetime)

    return earliestStart, latestFinish
