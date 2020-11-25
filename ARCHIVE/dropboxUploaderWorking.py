import dropbox
from config import D_ACCESS_TOKEN


class TransferData:
    def __init__(self, access_token):
        self.access_token = access_token

    def upload_file(self, file_from, file_to):
        dbx = dropbox.Dropbox(self.access_token)

        with open(file_from, "rb") as f:
            dbx.files_upload(f.read(), file_to)


def main():
    access_token = D_ACCESS_TOKEN
    transferData = TransferData(access_token)

    file_from = "image00734.jpg"  # This is name of the file to be uploaded
    file_to = "/image00734.jpg"  # This is the full path to upload the file to, including name that you wish the file to be called once uploaded.

    # API v2
    transferData.upload_file(file_from, file_to)


if __name__ == "__main__":
    main()
