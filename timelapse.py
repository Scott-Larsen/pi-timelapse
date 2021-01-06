#!/usr/bin/python3

import errno
import os
import sys

# import yaml
import pytz
import shutil
from yaml import safe_load
from picamera import PiCamera
from datetime import datetime, timedelta
from time import sleep
from send2trash import send2trash
from pathlib import Path
from sunriseSunset import calculateStartTimeAndEndTimes
from dropboxTransfer import dropboxUploader, dropboxGetFileDownloadLinks
from sendEMail import sendEMail
from checkSQS import checkSQSforGoLiveCommand
from config import STREAM_TOKEN


config = safe_load(open(os.path.join(sys.path[0], "config.yml")))
image_number = 0

testing = config["testing"]
if testing:
    print("Running in test mode.")
    takeNewPhotos = config["take_new_photos_in_testing"]
    currentTime = datetime.utcnow().replace(tzinfo=pytz.utc)
    endTimeWhenTesting = currentTime + timedelta(
        0, 223
    )  # Second number adds X seconds/ photos

LIVESTREAM_COMMAND = "raspivid -o - -t 0 -vf -hf -fps 24 -b 4500000 -rot 180 | ffmpeg -re -an -f s16le -i /dev/zero -i - -vcodec copy -acodec aac -ab 384k -g 17 -strict experimental -f flv -t "
if testing:
    LIVESTREAM_DURATION = config["livestream_test_duration"]
else:
    LIVESTREAM_DURATION = config["livestream_duration"]
TWITCH_ADDRESS = " rtmp://live-jfk.twitch.tv/app/"


def create_timestamped_dir(stillsDirectory):
    try:
        os.makedirs(stillsDirectory)
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


def capture_images(stillsDirectory, initiationDateString, endTime):
    try:
        global image_number

        if testing:
            interval = 1
        else:
            interval = config["interval"]

        while datetime.utcnow().replace(tzinfo=pytz.utc) < endTime:

            lastPictureCaptureTime = datetime.utcnow().replace(tzinfo=pytz.utc)
            n = 10 if testing else 100
            if image_number % n == 0:
                print(f"Taking picture #{image_number}")
                print(
                    f"Time of latest picture: {lastPictureCaptureTime}, End of timelapse: {endTime}\n"
                )

            # Start up the camera.
            camera = PiCamera()
            set_camera_options(camera)

            # Capture a picture.
            camera.capture(
                str(stillsDirectory)
                + "/"
                + initiationDateString
                + "-{0:05d}.jpg".format(image_number)
            )

            camera.close()

            image_number += 1

            print("Checking for livestream command")
            for i in range((interval - 1) // 5 if (interval - 1) // 5 > 1 else 1):
                if checkSQSforGoLiveCommand():
                    print("\nWe're going Live!\n")
                    os.system(
                        LIVESTREAM_COMMAND
                        + str(LIVESTREAM_DURATION)
                        + TWITCH_ADDRESS
                        + STREAM_TOKEN
                    )
                sleep(5)

            currentTime = datetime.utcnow().replace(tzinfo=pytz.utc)
            if currentTime < lastPictureCaptureTime + timedelta(0, interval):
                sleep(
                    (
                        lastPictureCaptureTime + timedelta(0, interval) - currentTime
                    ).total_seconds()
                )

        print("\nTime-lapse capture complete!\n")

    except (KeyboardInterrupt):
        print("\nTime-lapse capture cancelled.\n")


def create_video(stillsDirectory, initiationDateString, timelapseFullPath):
    print("\nCreating video (within the create_video function).\n")

    command = (
        "ffmpeg -r 24 -i "
        + str(stillsDirectory)
        + "/"
        + initiationDateString
        + "-%05d.jpg"
        + " -c:v libx265 -crf 28 "
        + str(timelapseFullPath)
    )

    os.system(command)


def create_meta_video(initiationDateString, workingDirectory, stillsDirectory, endTime):

    dest_dir = Path.joinpath(workingDirectory, "metaTimelapse")

    files = os.listdir(Path.joinpath(stillsDirectory))
    files.sort()
    lastPhotographNumber = int(files[-1][-9:-4])

    for i in range(lastPhotographNumber // 50 + 50, lastPhotographNumber - 50, 50):
        filename = initiationDateString + "-" + str(i).zfill(5) + ".jpg"
        src_file = Path.joinpath(stillsDirectory, filename)
        shutil.copy(src_file, dest_dir)  # copy the file to destination dir

    command = 'ffmpeg -r 24 -pattern_type glob -i "metaTimelapse/*.jpg" -c:v libx264 -vf fps=24 metaTimelapse.mp4'

    os.system(command)


def uploadDailyImageFolders():
    dailyImageSubfolders = [
        f.name for f in os.scandir() if f.is_dir() and "-timelapse" in f.name
    ]
    for folder in dailyImageSubfolders:
        print(f"Uploading folder {folder}.\n")
        dropboxUploader(folder)
        send2trash(folder)
        print(f"Finished uploading {folder}.\n")


def uploadLog():
    print(f"Uploading log.txt\n")
    dropboxUploader("log.txt")
    send2trash("log.txt")


def main():
    startTime, endTime = calculateStartTimeAndEndTimes()

    currentTime = datetime.utcnow().replace(tzinfo=pytz.utc)

    if testing:
        initialSleep = 3
        endTime = endTimeWhenTesting
        print(f"endTime = {endTime}")
    else:
        initialSleep = (
            (startTime - currentTime).total_seconds()
            if (startTime - currentTime).total_seconds() >= 0
            else 0
        )
    print(f"Sleeping for {int(initialSleep)} seconds.\n")
    sleep(initialSleep)

    # Create directory based on current timestamp.
    if testing:
        initiationDate = datetime.now(pytz.timezone("US/Eastern"))  # datetime.today()
    else:
        initiationDate = datetime.utcnow().date()
    initiationDateString = initiationDate.strftime("%Y-%m-%d")

    fileFolderName = initiationDateString + "-timelapse"
    print(f"fileFolderName is: " + fileFolderName)

    workingDirectory = Path("/home/pi/pi-timelapse")
    stillsDirectory = Path.joinpath(workingDirectory, fileFolderName)

    timelapseFilename = fileFolderName + ".mp4"
    timelapseFullPath = Path.joinpath(workingDirectory, timelapseFilename)

    if not testing or testing and takeNewPhotos:
        print(f"Creating the <{stillsDirectory}> for the still images.\n")
        create_timestamped_dir(stillsDirectory)

        # Kick off the capture process.
        print("Capturing the first image.\n")
        capture_images(stillsDirectory, initiationDateString, endTime)

        print("Captured all of the images.\n")

    # Create a video (Requires ffmpeg).
    if config["create_video"]:
        create_video(stillsDirectory, initiationDateString, timelapseFullPath)
        print("Daily timelapse video created.\n")

        print(
            f"Uploading {timelapseFilename} to Dropbox at "
            + datetime.utcnow().strftime("%Y-%m-%d %H:%m:%s")
            + " UTC\n"
        )
        try:
            dropboxUploader(timelapseFilename)
            send2trash(timelapseFilename)
            print(
                "Uploaded daily timelapse video to Dropbox and deleted it from Raspberry Pi\n"
            )
        except:
            print("Daily timelapse failed to upload to Dropbox")

    if config["create_meta_video"]:
        create_meta_video(
            initiationDateString,
            workingDirectory,
            stillsDirectory,
            endTime,
        )
        print("MetaTimelapse updated")

        try:
            dropboxUploader("metaTimelapse.mp4", "overwrite")
            send2trash("metaTimelapse.mp4")
            print("MetaTimelapse uploaded to Dropbox and deleted from Raspberry Pi\n")
        except:
            print("MetaTimelapse failed to upload to Dropbox")

    # Send e-mail about new video being uploaded to Dropbox
    if config["create_video"] or config["create_meta_video"]:
        dropboxFileDownloadLinks = dropboxGetFileDownloadLinks()
        sendEMail(dropboxFileDownloadLinks)

    uploadDailyImageFolders()

    uploadLog()


if __name__ == "__main__":
    main()
