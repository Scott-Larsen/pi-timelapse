import dropbox
import os
from datetime import datetime

# from zipfile import ZipFile
from dropboxTransfer import (
    dropboxDownloader,
    dropboxDownloadFolderZipped,
    dropboxDeleteFile,
)
from config import D_ACCESS_TOKEN

IMPORT_FOLDER = "/Users/Scott/Desktop/DATA/Photos/Kenyon-Construction/"

videosAndFoldersOnMac = [
    x
    for x in os.listdir(IMPORT_FOLDER)
    if x[-4:] == ".mp4" or os.path.isdir(IMPORT_FOLDER + "/" + x)
]

dbx = dropbox.Dropbox(D_ACCESS_TOKEN)
response = dbx.files_list_folder(path="")
for fileOrFolderName in response.entries:
    if (
        fileOrFolderName.name not in videosAndFoldersOnMac
        or fileOrFolderName.name == "metaTimelapse.mp4"
    ):
        if fileOrFolderName.name[-4:] == ".mp4":
            dropboxDownloader(fileOrFolderName.name, IMPORT_FOLDER)
            print(f"Downloading the file, {fileOrFolderName.name}.\n")
        elif fileOrFolderName.name[-4] != ".":
            dropboxDownloadFolderZipped(fileOrFolderName.name, IMPORT_FOLDER)
    else:
        try:
            print(
                f"{fileOrFolderName.name} is {(datetime.utcnow() - fileOrFolderName.client_modified).days} days old."
            )
            if (datetime.utcnow() - fileOrFolderName.client_modified).days > 7:
                print(f"Deleting {fileOrFolderName.name} from Dropbox.\n\n")
                dropboxDeleteFile(fileOrFolderName.name)
        except AttributeError:  # indicates it's a folder
            print(fileOrFolderName.name)
            folderDate = "-".join(fileOrFolderName.name.split("-")[:-1])
            print(folderDate)
            # datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
            if datetime.utcnow() - datetime.strptime(folderDate, "%Y-%m-%d"):
                dropboxDeleteFile(fileOrFolderName.name)

# dropboxDownloader(
#     "series-2020-11-12-timelapse.mp4",
#     ,
# )

# dropboxDeleteFile("2020-11-20-timelapse.mp4")
# dropboxDeleteFile()
