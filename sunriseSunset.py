#! usr/bin/python3

import os
import sys
import requests
import yaml
from datetime import datetime, date, timedelta
import time
from config import API_KEY


def calculateStartTimeAndNumberOfPictures():

    config = yaml.safe_load(open(os.path.join(sys.path[0], "config.yml")))

    latitude = config["latitude"]
    longitude = config["longitude"]

    currentDate = str(date.today())

    # print(currentDate)

    # epoch_time = int(time.time())
    epoch_time = int(time.time())
    # assert (epoch_time, integer)
    # print(epoch_time)

    # time as seconds since midnight, January 1, 1970 UTC
    # https://maps.googleapis.com/maps/api/timezone/json?location=39.6034810,-119.6822510&timestamp=1331161200&key=YOUR_API_KEY
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

    # print(response.json())

    sunriseSunset = response.json()["results"]

    # print(sunriseSunset)

    sunriseTime = sunriseSunset["sunrise"]
    sunsetTime = sunriseSunset["sunset"]
    # dayLength = sunriseSunset["day_length"]

    # print(sunriseTime)
    # date = datetime.fromisoformat("2017-01-01T12:30:59.000000")
    sunriseDateTime = datetime.fromisoformat(sunriseTime)
    sunsetDateTime = datetime.fromisoformat(sunsetTime)
    # sunriseDateTime = datetime.datetime.strptime(sunriseTime, "%Y-%m-%dT%I:%M:%S %p")
    # sunsetDateTime = datetime.datetime.strptime(sunsetTime, "%Y-%m-%dT%I:%M:%S %p")

    # print(sunriseDateTime)

    # timeDifferential = sunsetDateTime - sunriseDateTime

    interval = config["interval"]

    workingStart24Hour = config[
        "workingStart"
    ]  # str(config["workingStart"].split(":")[0] + dstOffset + rawOffset) + ":00"
    # print(type(workingStart24Hour))
    # print(workingStart24Hour)
    workingFinish24Hour = config["workingFinish"]

    def convert24HourToDecimal(twentyFourHourTime: str) -> float:
        # print(f"{twentyFourHourTime = } 86")
        # print(f"{type(twentyFourHourTime) = } 87")
        # print(f"{type(twentyFourHourTime) = }, {twentyFourHourTime = }")
        twentyFourHourTime = str(twentyFourHourTime)
        twentyFourHourTime = twentyFourHourTime.split(":")
        # print(f"{twentyFourHourTime = } 89")
        # print(f"{type(twentyFourHourTime) = } 90")
        # print(f"{twentyFourHourTime[1] = }")

        return int(twentyFourHourTime[0]) + float(twentyFourHourTime[1]) / 60

    assert convert24HourToDecimal("13:30") == 13.5

    # print(convert24HourToDecimal("13:30"))

    workingStartFloat = convert24HourToDecimal(workingStart24Hour)
    workingFinishFloat = convert24HourToDecimal(workingFinish24Hour)

    # print(f"{workingStart24Hour = }")
    # print(f"{workingStartFloat = }")
    # from dateutil.parser import parse

    def convertDecimalTo24Hour(decimalTime: float) -> str:
        decimalTime = str(decimalTime)
        # print(f"{decimalTime = }")
        decimalTime = decimalTime.split(".")
        # print(f"{decimalTime = }")
        return str(decimalTime[0] + ":" + str(int(float("0." + decimalTime[1]) * 60)))

    assert convertDecimalTo24Hour(13.5) == "13:30"

    # print(workingStartFloat, dstOffset, rawOffset)
    # print(workingStartFloat, dstOffset / 60 / 60, rawOffset / 60 / 60)
    # print(type(workingStartFloat + dstOffset / 60 / 60 + rawOffset / 60 / 60))
    # workingStartFloatUTC = workingStartFloat + dstOffset / 60 / 60 + rawOffset / 60 / 60
    # print(f"{workingStartFloatUTC = }, {type(workingStartFloatUTC) = }")
    workingStart = convertDecimalTo24Hour(
        workingStartFloat + dstOffset / 60 / 60 - rawOffset / 60 / 60
    )

    workingFinish = convertDecimalTo24Hour(
        workingFinishFloat + dstOffset / 60 / 60 - rawOffset / 60 / 60
    )
    # print(f"{workingStart = }")

    # time_obj = parse(time_str)
    from dateutil.parser import parse

    workingStartDatetime = parse(currentDate + " " + workingStart + "+00:00")

    workingFinishDatetime = parse(currentDate + " " + workingFinish + "+00:00")

    earliestStart = max(sunriseDateTime, workingStartDatetime)
    latestFinish = min(sunsetDateTime, workingFinishDatetime)

    dayLengthInSeconds = (latestFinish - earliestStart).total_seconds()
    # If dayLengthInSeconds is negative, it's split over two days and we need to add a day's worth of seconds
    if dayLengthInSeconds < 0:
        dayLengthInSeconds = dayLengthInSeconds + 24 * 60 * 60

    (numberOfIntervals, remainingTime) = divmod(dayLengthInSeconds, interval)

    numberOfPhotographsToTake = int(numberOfIntervals + 1)

    startTime = earliestStart + timedelta(seconds=remainingTime / 2)

    return startTime, numberOfPhotographsToTake
