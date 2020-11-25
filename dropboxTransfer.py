import os
import dropbox
from dropbox.files import WriteMode
from config import D_ACCESS_TOKEN


class TransferData:
    def __init__(self, access_token):
        self.access_token = access_token

    def upload_file(self, fileOrFolderName, file_to, write_mode):
        dbx = dropbox.Dropbox(self.access_token)

        # This should detect individual files
        if fileOrFolderName[-4] == ".":
            with open(
                fileOrFolderName, "rb"
            ) as f:  # Deleted leading "/" to upload .mp4
                dbx.files_upload(f.read(), file_to, mode=WriteMode(write_mode, None))

        # This should upload directories
        else:
            for root, dirs, files in os.walk(fileOrFolderName):
                for filename in files:

                    localPath = os.path.join(root, filename)

                    relativePath = os.path.relpath(localPath, fileOrFolderName)
                    dropboxPath = os.path.join("/", fileOrFolderName, relativePath)

                    with open(localPath, "rb") as f:
                        dbx.files_upload(
                            f.read(), dropboxPath, mode=WriteMode(write_mode, None)
                        )

    def download_file(self, filename, writePath):
        dbx = dropbox.Dropbox(self.access_token)

        with open(writePath + filename, "wb") as f:
            _, res = dbx.files_download(path="/" + filename)
            f.write(res.content)

    def download_folder_zipped(self, folderName, writePath):
        dbx = dropbox.Dropbox(self.access_token)

        with open(writePath + folderName + ".zip", "wb") as f:
            _, res = dbx.files_download_zip(path="/" + folderName)
            f.write(res.content)

        print(f"Downloaded the zipped folder {folderName}, now unzipping it.")

        zf = ZipFile(writePath + folderName + ".zip")
        zf.extractall(writePath)
        zf.close()

        print(f"Deleting the local zip file {folderName}.zip.")
        send2trash.send2trash(writePath + folderName + ".zip")
        print(f"Downloaded the folder {folderName}, now deleting it from Drobox.\n")
        dbx.files_delete_v2("/" + folderName)

    def dropboxGetFileDownloadLinks(self):
        dbx = dropbox.Dropbox(self.access_token)

        listOfDropboxLinks = []
        response = dbx.files_list_folder(path="")
        for file in response.entries:
            listOfDropboxLinks.append(
                dbx.sharing_create_shared_link("/" + file.name).url
            )
        return listOfDropboxLinks

    def dropboxDeleteFile(self, filename):
        dbx = dropbox.Dropbox(self.access_token)

        dbx.files_delete_v2("/" + filename)


def dropboxUploader(fileOrFolderName, write_mode="add"):
    access_token = D_ACCESS_TOKEN
    transferData = TransferData(access_token)

    print("File(s) uploading to Dropbox.\n")

    transferData.upload_file(fileOrFolderName, "/" + fileOrFolderName, write_mode)

    print("File successfully uploaded to Dropbox\n")


def dropboxDownloader(filename, writePath):
    access_token = D_ACCESS_TOKEN
    transferData = TransferData(access_token)

    print("File downloading from Dropbox.\n")

    transferData.download_file(filename, writePath)

    print("File successfully downloaded from Dropbox\n")


def dropboxDownloadFolderZipped(folderName, writePath):
    access_token = D_ACCESS_TOKEN
    transferData = TransferData(access_token)

    print(f"\n{folderName} downloading from Dropbox as a Zip file.")

    transferData.download_folder_zipped(folderName, writePath)

    print(f"{folderName} successfully downloaded from Dropbox.\n")


def dropboxGetFileDownloadLinks():
    access_token = D_ACCESS_TOKEN
    transferData = TransferData(access_token)

    return transferData.dropboxGetFileDownloadLinks()


def dropboxDeleteFile(filename):
    access_token = D_ACCESS_TOKEN
    transferData = TransferData(access_token)

    return transferData.dropboxDeleteFile(filename)
