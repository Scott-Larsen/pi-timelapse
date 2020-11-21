import dropbox
from config import D_ACCESS_TOKEN


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
            metadata, res = dbx.files_download(path="/" + filename)
            f.write(res.content)

        # with open("Prime_Numbers.txt", "wb") as f:
        #     metadata, res = dbx.files_download(path="/Homework/math/Prime_Numbers.txt")
        #     f.write(res.content)


def dropboxUploader(filename):
    access_token = D_ACCESS_TOKEN
    transferData = TransferData(access_token)

    transferData.upload_file(filename, "/" + filename)


def dropboxDownloader(filename, writePath):
    access_token = D_ACCESS_TOKEN
    transferData = TransferData(access_token)

    transferData.download_file(filename, writePath + filename)


dropboxDownloader(
    "series-2020-11-12-timelapse.mp4",
    "/Users/Scott/Desktop/DATA/Photos/Kenyon-Construction/",
)
# "series-2020-11-13-timelapse.mp4"
