#!/usr/bin/python3

import errno
import os
import sys
import pytz
import shutil
import dropbox
from time import time
from yaml import safe_load
from picamera import PiCamera
from datetime import date, datetime, timedelta
from time import sleep
from send2trash import send2trash
from pathlib import Path
from math import ceil
from sunriseSunset import calculateStartTimeAndEndTimes
from dropboxTransfer import dropboxUploader, dropboxGetFileDownloadLinks
from sendEMail import sendEMail
from checkSQS import checkSQSforGoLiveCommand
from config import STREAM_TOKEN, D_ACCESS_TOKEN


config = safe_load(open(os.path.join(sys.path[0], "config.yml")))
image_number = 0

testing = config["testing"]
if testing:
    print("Running in test mode.")
    takeNewPhotos = config["take_new_photos_in_testing"]
    currentTime = datetime.utcnow().replace(tzinfo=pytz.utc)
    endTimeWhenTesting = currentTime + timedelta(
        0, config["num_photos_testing"]
    )

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

    # Set exposure_compensation
    if config["exposure_compensation"]:
        camera.exposure_compensation = config["exposure_compensation"]

    # Set camera rotation
    if config["rotation"]:
        camera.rotation = config["rotation"]

    return camera


def capture_images(stillsDirectory, initiationDateString, endTime):
    try:
        global image_number

        # Start up the camera.
        camera = PiCamera()
        set_camera_options(camera)

        if testing:
            interval = 1
        else:
            interval = config["interval"]
        iterations = ceil(timeRemaining.total_seconds() / interval)
        logInterval = 10 if testing == True else 100
        for i in range(iterations):
            lastPictureCaptureTime = datetime.utcnow().replace(tzinfo=pytz.utc)
            if i % logInterval == 0:
                print(f"Taking picture #{image_number}")
            # Capture a picture.
            camera.capture(
                str(stillsDirectory)
                + "/"
                + initiationDateString
                + "-{0:05d}.jpg".format(image_number)
            )

            numStreamingChecks = max(1, interval // 10)
            for j in range(numStreamingChecks):
                if i % logInterval == 0:
                    print("Checking whether to go live.")
                    if checkSQSforGoLiveCommand():
                        print("\nWe're going Live!\n")
                        os.system(
                            LIVESTREAM_COMMAND
                            + str(LIVESTREAM_DURATION)
                            + TWITCH_ADDRESS
                            + STREAM_TOKEN
                        )

            currentTime = datetime.utcnow().replace(tzinfo=pytz.utc)
            if currentTime < lastPictureCaptureTime + timedelta(0, interval):
                sleep(
                    (
                        lastPictureCaptureTime + timedelta(0, interval) - currentTime
                    ).total_seconds()
                )
            
            image_number += 1

        camera.close()

        print("\nTime-lapse stills captured.\n")

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
        + " -hide_banner -loglevel error"
    )

    os.system(command)


def create_meta_video(initiationDateString, workingDirectory, stillsDirectory, endTime):
    """ Copy a few stills from todays photographs and create metaTimelapse of overall project."""

    dest_dir = Path.joinpath(workingDirectory, "metaTimelapse")
    
    files = os.listdir(Path.joinpath(stillsDirectory))
    files.sort()
    lastPhotographNumber = int(files[-1][-9:-4])

    for i in range(lastPhotographNumber // 50 + 50, lastPhotographNumber - 50, 50):
        filename = initiationDateString + "-" + str(i).zfill(5) + ".jpg"
        src_file = Path.joinpath(stillsDirectory, filename)
        shutil.copy(src_file, dest_dir)

    # Create metaTimelapse
    command = 'ffmpeg -r 24 -pattern_type glob -i "metaTimelapse/*.jpg" -c:v libx264 -vf fps=24 metaTimelapse.mp4 -hide_banner -loglevel error'
    os.system(command)


def uploadDailyImageFolders(tf):
    dailyImageSubfolders = [
        f.name for f in os.scandir() if f.is_dir() and "-timelapse" in f.name
    ]
    for folder in dailyImageSubfolders:
        if tf:
            print(f"Uploading folder {folder}.\n")
            dropboxUploader(folder)
            send2trash(folder)
            print(f"Finished uploading {folder}.\n")
        else:
            if time() - os.stat(folder).st_mtime > 7 * 24 * 60 * 60:
                send2trash(folder)
                print(f"Deleting {folder} from Dropbox.\n\n")


def updateMetaTimelapseStills():
    dbx = dropbox.Dropbox(D_ACCESS_TOKEN)
    try:
        metaTimelapseStillsOnPi = [
            f.name for f in os.scandir(path="metaTimelapse") if f.name.startswith(date.today().strftime("%Y-%m-%d"))]
        
        for file in metaTimelapseStillsOnPi:
            print(f"Uploading file {file}.\n")
            dropboxUploader(f"metaTimelapse/{file}")
    
    except dropbox.exceptions.ApiError as e: # Directory doesn't exist on Dropbox
        if "ListFolderError" in e:
            print(f"Uploading metaTimelapse folder to Dropbox.\n")
            dropboxUploader("/metaTimelapse")
    print(f"Finished updating Metatimelapse folder.\n")


def uploadLog():
    try:
        print("Uploading log.txt\n")
        dropboxUploader("log.txt", write_mode="overwrite")
        send2trash("log.txt")
    except:
        print("Log failed to upload to Dropbox\n")


def main():
    startTime, endTime = calculateStartTimeAndEndTimes()

    currentTime = datetime.utcnow().replace(tzinfo=pytz.utc)

    if testing:
        initialSleep = 2
        endTime = endTimeWhenTesting
    else:
        initialSleep = (
            (startTime - currentTime).total_seconds()
            if (startTime - currentTime).total_seconds() >= 0
            else 0
        )
    print(f"Sleeping for {int(initialSleep)} seconds.\n")
    sleep(initialSleep)

    if testing:
        initiationDate = datetime.now(pytz.timezone("US/Eastern"))
    else:
        initiationDate = datetime.utcnow().date()
    initiationDateString = initiationDate.strftime("%Y-%m-%d")

    fileFolderName = initiationDateString + "-timelapse"

    workingDirectory = Path("/home/pi/pi-timelapse")
    stillsDirectory = Path.joinpath(workingDirectory, fileFolderName)

    timelapseFilename = fileFolderName + ".mp4"
    timelapseFullPath = Path.joinpath(workingDirectory, timelapseFilename)

    if not testing or testing and takeNewPhotos:
        create_timestamped_dir(stillsDirectory)

        # Kick off the capture process.
        print("Capturing the first image.\n")
        capture_images(stillsDirectory, initiationDateString, endTime)

        print("Captured all of the images.\n")

    # Create a video (Requires ffmpeg).
    if config["create_video"]:
        create_video(stillsDirectory, initiationDateString, timelapseFullPath)
        print("Daily timelapse video created.\n")

        try:
            dropboxUploader(timelapseFilename)
            send2trash(timelapseFilename)
            print(
                "Daily timelapse video deleted from Raspberry Pi\n"
            )
        except:
            print("Daily timelapse failed to upload to Dropbox")

    if config["create_meta_video"]:
        create_meta_video(
            initiationDateString, workingDirectory, stillsDirectory, endTime,
        )
        print("MetaTimelapse updated")

        try:
            dropboxUploader("metaTimelapse.mp4", "overwrite")
            send2trash("metaTimelapse.mp4")
            print("MetaTimelapse deleted from Raspberry Pi\n")
        except:
            print("MetaTimelapse failed to upload to Dropbox")

    # Send e-mail about new video being uploaded to Dropbox
    if config["create_video"] or config["create_meta_video"]:
        dropboxFileDownloadLinks = [x for x in dropboxGetFileDownloadLinks() if "imelapse" in x]

        sendEMail(dropboxFileDownloadLinks)

    uploadDailyImageFolders(config["upload_stills"])

    if config["upload_meta_stills"]:
        updateMetaTimelapseStills()

    if os.path.exists("log.txt"):
        uploadLog()


if __name__ == "__main__":
    main()
