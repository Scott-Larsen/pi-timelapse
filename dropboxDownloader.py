import dropbox
from dropboxTransfer import dropboxDownloader, dropboxDownloadFolderZipped
import os
import send2trash
import shutil
from datetime import datetime
from zipfile import ZipFile

# from send2trash

# from os import walk
from config import D_ACCESS_TOKEN

IMPORT_FOLDER = "/Users/Scott/Desktop/DATA/Photos/Kenyon-Construction/"

# print(os.listdir())
videosAndFoldersOnMac = [
    x
    for x in os.listdir(IMPORT_FOLDER)
    if x[-4:] == ".mp4" or os.path.isdir(IMPORT_FOLDER + "/" + x)
]
# print(videosAndFoldersOnMac)

dbx = dropbox.Dropbox(D_ACCESS_TOKEN)
response = dbx.files_list_folder(path="")
# print(response)
for fileOrFolderName in response.entries:
    # print("\n")
    # print(fileOrFolderName.name)
    # print(
    #     f"{fileOrFolderName.name} is a file {os.path.isfile('/' + fileOrFolderName.name)} or folder {os.path.isdir('/' + fileOrFolderName.name)}."
    # )
    if fileOrFolderName.name not in videosAndFoldersOnMac:
        if fileOrFolderName.name[-4] == ".":
            dropboxDownloader(fileOrFolderName.name, IMPORT_FOLDER)
            print(f"Downloading the file, {fileOrFolderName.name}.\n")
        elif fileOrFolderName.name[-4] != ".":
            dropboxDownloadFolderZipped(fileOrFolderName.name, IMPORT_FOLDER)
            print(
                f"Downloaded the zipped folder {fileOrFolderName.name}, now unzipping it."
            )

            zf = ZipFile(IMPORT_FOLDER + fileOrFolderName.name + ".zip")
            zf.extractall(IMPORT_FOLDER)
            zf.close()

            print(f"Deleting the local zip file {fileOrFolderName.name}.")
            send2trash.send2trash(IMPORT_FOLDER + fileOrFolderName.name + ".zip")
            print(
                f"Downloaded the folder {fileOrFolderName.name}, now deleting it from Drobox.\n"
            )
            dbx.files_delete_v2("/" + fileOrFolderName.name)
            print(f"Deleting {fileOrFolderName.name} from Dropbox.\n")

        else:
            print(f"Checking if {fileOrFolderName.name} is 7 days old")
            # print(
            #     f"os.path.isfile(fileOrFolderName) = {os.path.isfile('/' + fileOrFolderName.name)}"
            # )
            if (
                datetime.utcnow() - fileOrFolderName.client_modified.total_seconds()
                > 7 * 24 * 60 * 60
            ):
                print(f"Deleting {fileOrFolderName.name} from Dropbox.\n")
    # print("\n")
    # dbx.files_delete(fileOrFolderName.name)

    # with open(localPath, "rb") as f:
    #     dbx.files_upload(f.read(), dropboxPath)

#             # if "." not in fileOrFolderName.name[-4:]:
#             #     print(f"deleting {fileOrFolderName}.\n")
#             #     dbx.files_delete_v2("/" + fileOrFolderName.name)

#     if (
#         fileOrFolderName.name[-4] == "."
#         and (datetime.utcnow() - fileOrFolderName.client_modified).total_seconds()
#         > 7 * 24 * 60 * 60
#     ):
#         print(f"deleting {fileOrFolderName}.\n")
#         dbx.files_delete_v2("/" + fileOrFolderName.name)


# dropboxDownloader(
#     "series-2020-11-12-timelapse.mp4",
#     ,
# )
