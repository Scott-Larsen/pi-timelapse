import dropbox
from config import D_ACCESS_TOKEN

dbx = dropbox.Dropbox(D_ACCESS_TOKEN)

with open(
    "/Users/Scott/Desktop/DATA/Photos/Kenyon-Construction/series-2020-11-12-timelapse.mp4",
    "wb",
) as f:
    metadata, res = dbx.files_download(path="/series-2020-11-12-timelapse.mp4")
    f.write(res.content)
