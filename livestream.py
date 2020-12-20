import os
import dropbox
from time import sleep

from config import STREAM_TOKEN, D_ACCESS_TOKEN
from dropboxTransfer import dropboxDownloader, dropboxDeleteFile

LIVESTREAM_COMMAND = "raspivid -o - -t 0 -vf -hf -fps 24 -b 4500000 -rot 180 | ffmpeg -re -an -f s16le -i /dev/zero -i - -vcodec copy -acodec aac -ab 384k -g 17 -strict experimental -f flv rtmp://live-jfk.twitch.tv/app/"

dbx = dropbox.Dropbox(D_ACCESS_TOKEN)
response = dbx.files_list_folder(path="")
filenames = [x.name for x in response.entries]
if "golive" in filenames:
    print("We're going live!")
    dropboxDeleteFile("golive")
    os.system(LIVESTREAM_COMMAND + STREAM_TOKEN)
    
    sleep(300)
