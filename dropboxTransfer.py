import os
import dropbox
from config import D_ACCESS_TOKEN


class TransferData:
    def __init__(self, access_token):
        self.access_token = access_token

    def upload_file(self, fileOrFolderName, file_to):
        dbx = dropbox.Dropbox(self.access_token)

        # This should detect individual files
        if fileOrFolderName[-4] == ".":
            with open(
                fileOrFolderName, "rb"
            ) as f:  # Deleted leading "/" to upload .mp4
                dbx.files_upload(f.read(), file_to)

        # This should upload directories
        else:
            for root, dirs, files in os.walk(fileOrFolderName):
                for filename in files:

                    localPath = os.path.join(root, filename)

                    relativePath = os.path.relpath(localPath, fileOrFolderName)
                    dropboxPath = os.path.join("/", fileOrFolderName, relativePath)

                    with open(localPath, "rb") as f:
                        dbx.files_upload(f.read(), dropboxPath)

    def download_file(self, filename, writePath):
        dbx = dropbox.Dropbox(self.access_token)

        with open(writePath + filename, "wb") as f:
            _, res = dbx.files_download(path="/" + filename)
            f.write(res.content)

    def dropboxGetFileDownloadLinks(self):
        dbx = dropbox.Dropbox(self.access_token)

        listOfDropboxLinks = []
        response = dbx.files_list_folder(path="")
        for file in response.entries:
            listOfDropboxLinks.append(
                dbx.sharing_create_shared_link("/" + file.name).url
            )
        return listOfDropboxLinks


def dropboxUploader(fileOrFolderName):
    access_token = D_ACCESS_TOKEN
    transferData = TransferData(access_token)

    print("File(s) uploading to Dropbox.\n")

    transferData.upload_file(fileOrFolderName, "/" + fileOrFolderName)

    print("File successfully uploaded to Dropbox\n")


def dropboxDownloader(filename, writePath):
    access_token = D_ACCESS_TOKEN
    transferData = TransferData(access_token)

    print("File downloading from Dropbox.\n")

    transferData.download_file(filename, writePath)

    print("File successfully downloaded from Dropbox\n")


def dropboxGetFileDownloadLinks():
    access_token = D_ACCESS_TOKEN
    transferData = TransferData(access_token)

    return transferData.dropboxGetFileDownloadLinks()


# dropboxUploader("2020-11-17-timelapse")
# dropboxUploader("log.txt")