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


if __name__ == "__main__":
    calculateStartTimeAndEndTimes()
