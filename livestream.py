import os
import dropbox
from time import sleep

from config import STREAM_TOKEN, D_ACCESS_TOKEN
from dropboxTransfer import dropboxDownloader

LIVESTREAM_COMMAND = "raspivid -o - -t 0 -vf -hf -fps 24 -b 4500000 -rot 180 | ffmpeg -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -i - -vcodec copy -acodec aac -ab 384k -g 17 -strict experimental -f flv rtmp://live-jfk.twitch.tv/app/"

dbx = dropbox.Dropbox(D_ACCESS_TOKEN)
response = dbx.files_list_folder(path="")
# for response in response.entries:
#     print(response.name)
# print(response.entries)
filenames = [x.name for x in response.entries]
# if "golive" in filenames:
#     print("golive!!")
# print(LIVESTREAM_COMMAND + STREAM_TOKEN)
if "golive" in filenames:
    print("golive!")
    os.system(LIVESTREAM_COMMAND + STREAM_TOKEN)
    sleep(300)
