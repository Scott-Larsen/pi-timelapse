#!/usr/bin/python3

from picamera import PiCamera
import errno
import os
import sys
from datetime import datetime, timedelta
from time import sleep
import yaml
import time
import pytz
import shutil
from send2trash import send2trash
from pathlib import Path
from sunriseSunset import calculateStartTimeAndEndTimes
from dropboxTransfer import dropboxUploader, dropboxGetFileDownloadLinks
from sendEMail import sendEMail

testing = 0  # 1 for TruePath.joinpath(stillsDirectory (i.e., testing), 0 for False
if testing:
    takeNewPhotos = 1  # 1 for True (i.e., take photos), 0 for False
    currentTime = datetime.utcnow().replace(tzinfo=pytz.utc)
    # currentTime = datetime.now()
    # print(currentTime)
    endTimeWhenTesting = currentTime + timedelta(0, 103) # Adds 103 seconds/ photos

config = yaml.safe_load(open(os.path.join(sys.path[0], "config.yml")))
image_number = 0


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
            interval = 1 #, endTime = 1, currentTime + 103
        else:
            interval = config["interval"]

        print(datetime.utcnow().replace(tzinfo=pytz.utc), endTime)
        while datetime.utcnow().replace(tzinfo=pytz.utc) < endTime:

            # Set a timer to take another picture at the proper interval after this
            # picture is taken.
            # if image_number < (config["total_images"] - 1):
            #     thread = threading.Timer(config["interval"], capture_images).start()

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


def create_video(stillsDirectory, initiationDateString, timelapseFullPath):
    print("\nCreating video (within the create_video function).\n")

    # ffmpeg -r 24 -i 2020-11-18-timelapse/image%05d.jpg -c:v libx264 -vf fps=24 2020-11-18-timelapse.mp4
    # ffmpeg -r 24 -i /home/pi/pi-timelapse/2020-11-22-timelapse/image%05d.jpg -c:v libx265 -crf 28 /home/pi/pi-timelapse/2020-11-22-timelapse.mp4
    # 2020-11-22-00006.jpg

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


def create_meta_video(
    initiationDateString, workingDirectory, stillsDirectory, endTime
):

    # src_dir = os.getcwd() #get the current working dir
    # print(src_dir)

    # create a dir where we want to copy and rename
    # dest_dir = os.mkdir('subfolder')
    # os.listdir()
    # endTime
    # src_dir = stillsDirectory
    # endTime = 103

    dest_dir = Path.joinpath(workingDirectory, "metaTimelapse")

    files = os.listdir(Path.joinpath(stillsDirectory))
    files.sort()
    lastPhotographNumber = int(files[-1][-9:-4])

    for i in range(
        lastPhotographNumber // 50 + 50, lastPhotographNumber - 50, 50
    ):
        filename = initiationDateString + "-" + str(i).zfill(5) + ".jpg"
        src_file = Path.joinpath(stillsDirectory, filename)
        shutil.copy(src_file, dest_dir)  # copy the file to destination dir

        # dst_file = os.path.join(dest_dir, filename)
        # new_dst_file_name = os.path.join(dest_dir, fileFolderName + "-" + filename)

        # os.rename(dst_file, new_dst_file_name)  # rename
    # Delete the metaTimelapse.mp4 to make way for the new one.
    # send2trash("metaTimelapse.mp4")

    command = 'ffmpeg -r 24 -pattern_type glob -i "metaTimelapse/*.jpg" -c:v libx264 -vf fps=24 metaTimelapse.mp4'

    # print(dir)
    os.system(command)

    # os.chdir(dest_dir)

    # print(os.listdir())


def uploadDailyImageFolders():
    dailyImageSubfolders = [
        f.name for f in os.scandir() if f.is_dir() and "-timelapse" in f.name
    ]
    for folder in dailyImageSubfolders:
        print(f"Uploading folder {folder}.\n")
        dropboxUploader(folder)
        send2trash(folder)
        print(f"Finished uploading {folder}.\n")


def main():

    startTime, endTime = calculateStartTimeAndEndTimes()

    # print(f"Scheduling the timelapse to start at")
    # print(f"Sleeping for {startTime} seconds.\n")
    currentTime = datetime.utcnow().replace(tzinfo=pytz.utc)
    if testing:
        initialSleep = 0
        endTime = endTimeWhenTesting
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

    # Create an animated gif (Requires ImageMagick).
    if config["create_gif"]:
        create_animated_gif()

    # Create a video (Requires ffmpeg).
    if config["create_video"]:
        create_video(stillsDirectory, initiationDateString, timelapseFullPath)
        print("Daily timelapse video created.\n")

        # Print all folders in the directory
        # print("os.listdir(workingDirectory) =:")
        # print(os.listdir(workingDirectory))
        # dir = os.path.join(sys.path[0], fileFolderName)

        # print(
        #     str(stillsDirectory)
        #     + " exists - "
        #     + str(os.path.exists(stillsDirectory))
        #     + "\n"
        #     + str(timelapseFilename)
        #     + " exists - "
        #     + str(os.path.exists(timelapseFullPath))
        #     + "\n"
        #     + "metaTimelapse exists - "
        #     + str(os.path.exists(workingDirectory / "metaTimelapse"))
        #     + "\n"
        # )

        print(
            f"Uploading {timelapseFilename} to Dropbox at "
            + datetime.utcnow().strftime("%Y-%m-%d %H:%m:%s")
            + " UTC\n"
        )
        dropboxUploader(timelapseFilename)
        send2trash(timelapseFilename)
        print(
            "Uploaded daily timelapse video to Dropbox and deleted if from Raspberry Pi\n"
        )

    if config["create_meta_video"]:
        create_meta_video(
            initiationDateString,
            workingDirectory,
            stillsDirectory,
            endTime,
        )
        print("MetaTimelapse updated")
        # print(
        #     "metaTimelapse.mp4 exists - "
        #     + str(os.path.exists(workingDirectory / "metaTimelapse.mp4"))
        #     + "\n"
        # )
        dropboxUploader("metaTimelapse.mp4", "overwrite")
        send2trash("metaTimelapse.mp4")
        print("MetaTimelapse uploaded to Dropbox and deleted from Raspberry Pi\n")

    if config["create_video"] or config["create_meta_video"]:
        # Send e-mail about new video being uploaded to Dropbox
        dropboxFileDownloadLinks = dropboxGetFileDownloadLinks()
        sendEMail(dropboxFileDownloadLinks)

    uploadDailyImageFolders()


if __name__ == "__main__":
    main()
