from datetime import datetime
import pytz
import smtplib

from config import USER, PASS, FROM_EMAIL, TO_EMAIL


def sendEMail(links):
    # jobs = jobs
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(USER, PASS)

    subject = f"New construction video uploaded."

    # print(links)

    # Find metaTimelapse link
    for link in links:
        if "metaTimelapse" in link:
            metaTimelapseFilename = link
            break

    i = links.index(metaTimelapseFilename)
    metaTimelapseLink = links.pop(i)

    body = (
        "Today's video:\n"
        + links.pop()
        + "\n\nOverall project timelapse:\n"
        + metaTimelapseLink
        + "\n\nPrevious days' videos:\n"
        + "\n".join(links)
    )

    # jobIDs = [
    #     jobs[x] for x in sorted(jobs.keys(), key=lambda x: jobs[x][0], reverse=True)
    # ][:25]
    # for jobID in jobIDs:
    #     body += f"({jobID[0]}) {jobID[2]} at {jobID[3]} in {jobID[5]} posted {jobID[4][5:11]}\n{jobID[1]}\n... {jobID[6][100:500]} ...\n\n\n"
    # if len(body) == 0:
    #     body += "\nNo results."
    # body = body.encode("ascii", "ignore").decode("ascii")  # last working

    for email in TO_EMAIL:
        msg = f"From: {FROM_EMAIL}\r\nTo: {email}\r\nSubject: {subject}\n\n{body}"
        server.sendmail(FROM_EMAIL, email, msg)

    timeZone_NY = pytz.timezone("America/NEW_York")
    datetime_NY = datetime.now(timeZone_NY)
    print(f"E-mail was sent at {datetime_NY.strftime('%H:%M')}.\n\n")

    server.quit()


links = [
    "https://www.dropbox.com/s/3wsltnew4gcvfdo/2020-12-26-timelapse.mp4?dl=0",
    "https://www.dropbox.com/s/6cq30esswmp5yv5/metaTimelapse.mp4?dl=0",
    "https://www.dropbox.com/s/c2q5clcfze1bc9m/2020-12-18-timelapse.mp4?dl=0",
    "https://www.dropbox.com/s/ouh2q3yf4dq5gnv/2020-12-19-timelapse.mp4?dl=0",
    "https://www.dropbox.com/s/5bmwhb1fucp72lu/2020-12-20-timelapse.mp4?dl=0",
    "https://www.dropbox.com/s/8y6fe08vvnnq52e/2020-12-24-timelapse.mp4?dl=0",
    "https://www.dropbox.com/s/98gr44m08w4x6jb/2020-12-25-timelapse.mp4?dl=0",
]

if __name__ == "__main__":
    sendEMail(links)
# sendEMail(
#     [
#         "https://www.dropbox.com/s/a5eibgl74y1w5xk/series-2020-11-12-timelapse.mp4?dl=0",
#         "https://www.dropbox.com/s/a5eibgl74y1w5xk/series-2020-11-11-timelapse.mp4?dl=0",
#         "https://www.dropbox.com/s/a5eibgl74y1w5xk/series-2020-11-10-timelapse.mp4?dl=0",
#     ]
# )
