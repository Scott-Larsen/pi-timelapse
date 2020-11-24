import dropbox
import send2trash
from config import D_ACCESS_TOKEN
from zipfile import ZipFile


class TransferData:
    def __init__(self, access_token):
        self.access_token = access_token

    def upload_file(self, filename, file_to):
        dbx = dropbox.Dropbox(self.access_token)

        with open(filename, "rb") as f:
            dbx.files_upload(f.read(), file_to)

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


def dropboxUploader(filename):
    access_token = D_ACCESS_TOKEN
    transferData = TransferData(access_token)

    print(f"{filename} uploading to Dropbox.\n")

    transferData.upload_file(filename, "/" + filename)

    print(f"{filename} successfully uploaded to Dropbox\n")


def dropboxDownloader(filename, writePath):
    access_token = D_ACCESS_TOKEN
    transferData = TransferData(access_token)

    print(f"{filename} downloading from Dropbox.\n")

    transferData.download_file(filename, writePath)

    print(f"{filename} successfully downloaded from Dropbox.\n")


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
