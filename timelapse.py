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
import shutil
from sunriseSunset import calculateStartTimeAndNumberOfPictures
from dropboxTransfer import dropboxUploader, dropboxGetFileDownloadLinks
from sendEMail import sendEMail

testing = 1  # 1 for True (i.e., testing), 0 for False
if testing:
    takeNewPhotos = 1  # 1 for True (i.e., take photos), 0 for False

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
        if testing:
            interval, numberOfPhotographsToTake = 1, 100
        else:
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
            # camera.capture(dir + f"/image{image_number}.jpg")
            camera.close()

            # if image_number < (config["total_images"] - 1):
            image_number += 1

            # print(time.localtime(), image_number, total_images)

            time.sleep(interval)

        # else:
        print("\nTime-lapse capture complete!\n")
        # TODO: This doesn't pop user into the except block below :(.
        # sys.exit()

    except (KeyboardInterrupt):  # , SystemExit):
        print("\nTime-lapse capture cancelled.\n")


def create_animated_gif():
    print("\nCreating animated gif.\n")
    os.system(
        "convert -delay 10 -loop 0 " + dir + "/image*.jpg " + dir + "-timelapse.gif"
    )


def create_meta_video(fileFolderName, numberOfPhotographsToTake):

    # src_dir = os.getcwd() #get the current working dir
    # print(src_dir)

    # create a dir where we want to copy and rename
    # dest_dir = os.mkdir('subfolder')
    # os.listdir()
    # numberOfPhotographsToTake
    src_dir = fileFolderName
    dest_dir = "metaTimelapse"
    for i in range(
        numberOfPhotographsToTake // 50 + 50, numberOfPhotographsToTake - 50, 50
    ):
        filename = "image" + str(i).zfill(5) + ".jpg"
        src_file = os.path.join(src_dir, filename)
        shutil.copy(src_file, dest_dir)  # copy the file to destination dir

        dst_file = os.path.join(dest_dir, filename)
        new_dst_file_name = os.path.join(dest_dir, fileFolderName + "-" + filename)

        os.rename(dst_file, new_dst_file_name)  # rename

    command = (
        "ffmpeg -r 24 -i metaTimelapse/*.jpg -c:v libx264 -vf fps=24 metaTimelapse.mp4"
    )

    # print(dir)
    os.system(command)

    # os.chdir(dest_dir)

    # print(os.listdir())


def create_video(dir, fileFolderName):
    print("\nCreating video (within the create_video function).\n")

    # ffmpeg -r 24 -i 2020-11-18-timelapse/image%05d.jpg -c:v libx264 -vf fps=24 2020-11-18-timelapse.mp4
    command = (
        "ffmpeg -r 24 -i "
        + dir
        + "/image%05d.jpg"
        + " -c:v libx265 -crf 28 "
        + dir
        + ".mp4"  # -vf fps=24 -v verbose"
    )

    print(dir)
    os.system(command)
    print("os.system - video creating command - command should have run.\n")


def main():

    startTime, numberOfPhotographsToTake = calculateStartTimeAndNumberOfPictures()

    print(
        f"Scheduling the timelapse to start at {startTime} UTC and take {numberOfPhotographsToTake} photographs.\n"
    )

    currentTime = datetime.utcnow().replace(tzinfo=pytz.utc)
    if testing:
        initialSleep = 0
    else:
        initialSleep = (
            (startTime - currentTime).total_seconds()
            if (startTime - currentTime).total_seconds() >= 0
            else 0
        )
    print(f"Sleeping for {int(initialSleep)} seconds.\n")
    time.sleep(initialSleep)

    # Create directory based on current timestamp.
    if testing:
        initiationDate = datetime.now(pytz.timezone("US/Eastern"))  # datetime.today()
    else:
        initiationDate = datetime.utcnow().date()

    fileFolderName = initiationDate.strftime("%Y-%m-%d") + "-timelapse"
    print(f"fileFolderName is: " + fileFolderName)

    dir = os.path.join(sys.path[0], fileFolderName)
    print("dir is: " + dir)

    timelapseFilename = fileFolderName + ".mp4"

    if not testing or testing and takeNewPhotos:
        print("Creating the Directory for the still images.\n")
        create_timestamped_dir(dir)

    if not testing or testing and takeNewPhotos:
        # Kick off the capture process.
        print("Capturing the first image.\n")
        capture_images(dir, numberOfPhotographsToTake)

    print("Captured all of the images.\n")

    # Create an animated gif (Requires ImageMagick).
    if config["create_gif"]:
        create_animated_gif()

    if config["create_meta_video"]:
        create_meta_video("/" + fileFolderName, numberOfPhotographsToTake)

    # Create a video (Requires ffmpeg).
    print("About to trigger video")
    if config["create_video"]:
        print("Triggering main timelapse function.\n")
        create_video(dir, fileFolderName)
        print("Timelapse video created.\n")

        # Print all folders in the directory
        print("os.listdir(fileFolderName) =:")
        print(os.listdir(fileFolderName))
        # dir = os.path.join(sys.path[0], fileFolderName)

        print("config.py exists - " + str(os.path.exists(dir + "config.py")))
        print(
            timelapseFilename
            + " exists - "
            + str(os.path.exists(dir + timelapseFilename))
        )

        print(
            f"Uploading {timelapseFilename} to Dropbox at "
            + datetime.utcnow().strftime("%Y-%m-%d %H:%m:%s")
            + "\n"
        )

        dropboxUploader(timelapseFilename)
        print("Uploaded video to Dropbox\n")

        # Send e-mail about new video being uploaded to Dropbox
        dropboxFileDownloadLinks = dropboxGetFileDownloadLinks()
        sendEMail(dropboxFileDownloadLinks)

    print("Uploading folder of still images.\n")
    dropboxUploader(fileFolderName)
    print("Finished uploading still images.\n")


if __name__ == "__main__":
    main()
