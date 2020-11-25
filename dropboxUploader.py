import dropbox
from config import D_ACCESS_TOKEN


class TransferData:
    def __init__(self, access_token):
        self.access_token = access_token

    def upload_file(self, filename, file_to):
        dbx = dropbox.Dropbox(self.access_token)

        with open(filename, "rb") as f:
            dbx.files_upload(f.read(), file_to)


def dropboxUploader(filename):
    access_token = D_ACCESS_TOKEN
    transferData = TransferData(access_token)

    transferData.upload_file(filename, "/" + filename)
