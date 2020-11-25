#!/usr/bin/python3

from picamera import PiCamera
import errno
import os
import sys
from datetime import datetime
from time import sleep
import yaml
import time
import pytz
from sunriseSunset import calculateStartTimeAndNumberOfPictures


config = yaml.safe_load(open(os.path.join(sys.path[0], "config.yml")))
image_number = 0


def create_timestamped_dir(dir):
    try:
        os.makedirs(dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def set_camera_options(camera):
    # Set camera resolution.
    if config["resolution"]:
        camera.resolution = (
            config["resolution"]["width"],
            config["resolution"]["height"],
        )

    # Set ISO.
    if config["iso"]:
        camera.iso = config["iso"]

    # Set shutter speed.
    if config["shutter_speed"]:
        camera.shutter_speed = config["shutter_speed"]
        # Sleep to allow the shutter speed to take effect correctly.
        sleep(1)
        camera.exposure_mode = "off"

    # Set white balance.
    if config["white_balance"]:
        camera.awb_mode = "off"
        camera.awb_gains = (
            config["white_balance"]["red_gain"],
            config["white_balance"]["blue_gain"],
        )

    # Set camera rotation
    if config["rotation"]:
        camera.rotation = config["rotation"]

    return camera


def capture_images(dir, numberOfPhotographsToTake):
    try:
        global image_number

        # total_images = config["total_images"]
        interval = config["interval"]

        while image_number < numberOfPhotographsToTake:

            # Set a timer to take another picture at the proper interval after this
            # picture is taken.
            # if image_number < (config["total_images"] - 1):
            #     thread = threading.Timer(config["interval"], capture_images).start()

            # Start up the camera.
            camera = PiCamera()
            set_camera_options(camera)

            # Capture a picture.
            # camera.capture(dir + "/image{0:05d}.jpg".format(image_number))
            camera.capture(dir + "/image{0:05d}.jpg".format(image_number))
            camera.close()

            # if image_number < (config["total_images"] - 1):
            image_number += 1

            # print(time.localtime(), image_number, total_images)

            time.sleep(interval)

        # else:
        print("\nTime-lapse capture complete!\n")
        # TODO: This doesn't pop user into the except block below :(.
        sys.exit()

    except (KeyboardInterrupt, SystemExit):
        print("\nTime-lapse capture cancelled.\n")


def create_animated_gif():
    print("\nCreating animated gif.\n")
    os.system(
        "convert -delay 10 -loop 0 " + dir + "/image*.jpg " + dir + "-timelapse.gif"
    )  # noqa


def create_video():
    print("\nCreating video.\n")

    subfolder = dir.split("/")[-1]

    command = (
        "ffmpeg -r 24 -i "
        + dir
        + "/image%05d.jpg"
        + " -c:v libx264 -vf fps=24 "
        + dir
        + "-timelapse.mp4"
    )

    os.system(command)


def main():
    # createVideo = config["create_video"]
    # print(f"{createVideo = }")
    # print(config["create_video"])

    startTime, numberOfPhotographsToTake = calculateStartTimeAndNumberOfPictures()

    # startTime =

    print(
        f"Scheduling the timelapse to start at {startTime} UTC and take {numberOfPhotographsToTake} photographs.\n"
    )

    currentTime = datetime.utcnow().replace(tzinfo=pytz.utc)
    initialSleep = (startTime - currentTime).total_seconds()
    print(f"Sleeping for {int(initialSleep)} seconds.\n")
    # time.sleep(initialSleep)

    # Create directory based on current timestamp.
    dir = os.path.join(
        sys.path[0], "series-" + datetime.utcnow().date().strftime("%Y-%m-%d")
    )
    # print(datetime.utcnow().date().strftime("%Y-%m-%d"))
    print("Creating the Directory for the still images.\n")
    create_timestamped_dir(dir)

    # Kick off the capture process.
    print("Capturing the first image.\n")
    capture_images(dir, numberOfPhotographsToTake)

    print("Captured all of the images.\n")

    # TODO: These may not get called after the end of the threading process...
    # Create an animated gif (Requires ImageMagick).
    if config["create_gif"]:
        create_animated_gif()

    # Create a video (Requires avconv - which is basically ffmpeg).
    if config["create_video"]:
        print("Creating video.\n")
        create_video()
        print("Video finished.\n")


if __name__ == "__main__":
    main()