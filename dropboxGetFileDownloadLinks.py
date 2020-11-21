import dropbox
from config import D_ACCESS_TOKEN

dbx = dropbox.Dropbox(D_ACCESS_TOKEN)


def dropboxGetFileDownloadLinks():
    listOfDropboxLinks = []

    response = dbx.files_list_folder(path="")
    for file in response.entries:
        listOfDropboxLinks.append(dbx.sharing_create_shared_link("/" + file.name).url)
    return listOfDropboxLinks


# print(dropboxGetFileDownloadLinks())
