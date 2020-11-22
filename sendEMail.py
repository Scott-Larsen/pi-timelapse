from datetime import datetime
import pytz
import smtplib

from config import USER, PASS, EMAIL


def sendEMail(links):
    # jobs = jobs
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(USER, PASS)

    subject = f"New construction video uploaded!"

    body = (
        "Today's video:\n"
        + links.pop()
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

    msg = f"Subject: {subject}\n\n{body}"

    server.sendmail(EMAIL, EMAIL, msg)

    timeZone_NY = pytz.timezone("America/NEW_York")
    datetime_NY = datetime.now(timeZone_NY)
    print(f"E-mail was sent at {datetime_NY.strftime('%H:%M')}.\n\n")

    server.quit()


# sendEMail(
#     [
#         "https://www.dropbox.com/s/a5eibgl74y1w5xk/series-2020-11-12-timelapse.mp4?dl=0",
#         "https://www.dropbox.com/s/a5eibgl74y1w5xk/series-2020-11-11-timelapse.mp4?dl=0",
#         "https://www.dropbox.com/s/a5eibgl74y1w5xk/series-2020-11-10-timelapse.mp4?dl=0",
#     ]
# )

