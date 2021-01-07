# Construction Cam

This is a timelapse camera/ app designed to monitor construction progress at a remote site. If you have access to the internet at the jobsite you'll be able to receive daily timelapse videos, 'metatimelapses' of the entire project as well as to trigger livestreaming to Twitch from a [companion Flask app](https://github.com/Scott-Larsen/pi-timelapse-flask-app) for up to the moment updates.

This project is built off of the excellent [Raspberry Pi Time-Lapse App](https://github.com/geerlingguy/pi-timelapse) by [Jeff Geerling](https://www.youtube.com/c/JeffGeerling), without whom I'm not sure that I could have pulled it all together.

There are many steps in the process and I'm sure I'll leave something out so feel free to get in touch if something is not clear. I've been working with a Raspberry Pi 3 Model B+ and Camera Module V2 so I can't account for other combinations of Pi hardware.

<p  align="center"><a  href="https://www.youtube.com/watch?v=mThXDhkj0aA"><img  src="https://img.youtube.com/vi/mThXDhkj0aA/0.jpg"  alt="Cirrus clouds on a sunny day - Raspberry Pi Zero W time-lapse by Jeff Geerling"  /></a></p>

## Usage

> For an in-depth overview, see my blog post [Raspberry Pi Zero W as a headless time-lapse camera](https://www.jeffgeerling.com/blog/2017/raspberry-pi-zero-w-headless-time-lapse-camera).

First, make sure the camera interface is enabled—if you don't, you'll see the message `Camera is not enabled. Try running 'sudo raspi-config'`:

1. Run `sudo raspi-config`
2. Go to 'Interfacing Options'
3. Select 'Camera'
4. Select 'Yes' for enabling the camera
5. Select 'Finish' in the main menu and then 'Yes' to reboot the Pi

Now, set up the timelapse app on your Raspberry Pi:

1. In the Terminal, navigate to the folder on your Pi in which you'd like to install the timelapse software. I added a `pi-timelapse` directory (`mkdir pi-timelapse` and then `cd pi-timelapse`), which is an arbitrary decision but it may affect commands you see later.
2. Install dependencies: `sudo apt-get install -y git python-picamera python-yaml`
3. Clone this repository to your Pi: `git clone https://github.com/Scott-Larsen/pi-timelapse.git`
4. Copy `configEXAMPLE.py` to `config.py`. Take note that the sensitive data is saved in config.py while the more innocuous settings are saved in `config.yml`. Double-check that `config.py` is in your `.gitignore` file before pushing any changes back to GitHub.
5. Configure the timelapse by modifying values in `config.yml` and signing up for keys for the various services in `config.py`.
6. Once everything is setup you might flip the `testing` flag in `config.yml` to `1` (on) to check if everything is working. Then you can enter `python3 timelapse.py` to run it.

After the capture is completed, the images will be stored in a directory named `<date>-timelapse`.


### Triggering the Raspberry Pi daily, software updates and Pi restarts using crontab

The best way I could find to get the timelapse to run daily was to set a cronjob on the Raspberry Pi. In the terminal type the following:

`crontab -e`

In the editor window that opens, enter the following command:

```4 10 * * * cd /home/pi/pi-timelapse && /usr/bin/python3 timelapse.py >> /home/pi/pi-timelapse/log.txt```

The project assumes that you haven't changed the clock on the Pi so it should be set to UTC.  This means that at 4:10 ([AM] UTC [~1AM in New York]) it navigates to the /home/pi/pi-timelapse folder (change <username> `pi` and project folder `pi-timelapse` as necessary) and using python3 executes `timelapse.py`.  The logging that you'd normally see in the terminal is written to `log.txt` within the project directory which you can check if things go wrong.

Because I'd have this setup at a remote location without direct access into the network with the Pi I also wanted it to be able to pull updates from GitHub.  I wrote the `gitPuller.py` script and have it run daily.

```3 10 * * * cd /home/pi/pi-timelapse && /usr/bin/python3 gitPuller.py >> /home/pi/pi-timelapse/pullLog.txt```

And since I knew problems would develop over time and I won't be around to restart the Pi I run this command to restart the Pi daily.

````3 40 * * * /sbin/shutdown -r now```

When you've entered all of the commands, close and save the crontab file (`control-x` and `S` in Nano).

## Creating videos and 'metatimelapses'

### Videos

Requirements: You should install [FFmpeg](https://ffmpeg.org) — `sudo apt-get -y install ffmpeg`)

If you have `create_video` set to `True` in `config.yml`, the Pi will also generate a video immediately following the conclusion of the still captures.

> Note: Video generation can take a very long time on slower Pis, like the Pi Zero, A+, or original A or B.

### Metatimelapses

If you'd like a 'metatimelapse' - a timelapse spanning the entire length of the project - set `create_metatimelapse` to `True` in `config.yml`.

### Uploading files to Dropbox

In order to get the files from the Pi, I upload them to my personal Dropbox account and then set a cronjob on my laptop to download them.

<!-- https://www.dropbox.com/developers/apps

`Scoped access` > `App folder`

You'll need to copy the `App key` and `App secret` and enter them in the config.py file.

`Permissions` tab and `Files and folders` make sure that `files.content.write` and `files.content.read` -->

### Sending e-mail notifications

I built this with a client in mind so wanted a way to alert them about updates nightly.  The script is built around using a gmail account so you're going to have to sign up for an app password for gmail and enter your credentials in `config.py`.  You can find directions for setting up an app password at [https://support.google.com/accounts/answer/185833?hl=en](https://support.google.com/accounts/answer/185833?hl=en).  The `TO_EMAIL` field is a list and can include multiple e-mail addresses to which you want to send e-mail updates.

### Downloading the files from Dropbox

Once again I'm using a cronjob, this time on my laptop, to download the files from Dropbox using `dropboxDownloader.py` (which, in turn, uses `dropboxTransfer.py`).  
<!-- Be sure your computer has a copy of the `config.py` file on your computer with the Dropbox credentials in it (without putting it up on Github) -->

Again, invoke `crontab -e` and enter the following code making the necessary adjustments for your file paths.

55 */6 * * *  python3 /Users/PATH-TO-PROJECT/pi-timelapse/dropboxDownloader.py >> /Users/PATH-TO-PROJECT/pi-timelapse/downloadLog.txt

### Livestreaming from the Raspberry Pi

The final feature of the app is that, during the hours that it's filming a timelapse, you can prompt it to broadcast live video via Twitch that you can watch from anywhere on your phone or computer.  Enabling this capability requires setting up a Twitch account and an Amazon/ AWS SQS (Simple Queue Service) and enter those details in `config.py`

I believe getting the Twitch streaming key involves signing up for a standard account and then going to `https://dashboard.twitch.tv/u/USERNAME/settings/channel` (replacing *USERNAME* with your username) and copying the `Primary Stream key` at the top.

With AWS, if you don't already have an account for AWS you'll need to start by signing up for one.  You'll then want to navigate to [https://console.aws.amazon.com/sqs](https://console.aws.amazon.com/sqs) to create a Simple Queue Service (SQS).  This is where we set a boolean in the cloud that the Pi checks every 5 seconds to see whether you want it to go live.  You want to `create queue` in the upper-right corner and select `standard`.



### Manually Compiling Videos with `ffmpeg`

You can use `ffmpeg` on other platforms to put together image sequences after the fact. For example, to take a sequence like `2021-01-03-00000.jpg` to `2021-01-03-00999.jpg` and generate an MP4 video, swap `<date as it appears in files>` in the commande below with `2021-01-03` and run it in the terminal:

    ffmpeg -r 24 -i <date as it appears in files>-%05d.jpg -c:v libx265 -crf 28 timelapse.mp4

And if you wanted to start the video in the middle of the sequence (e.g. instead of starting at `2021-01-03-00000.jpg`, start at `2021-01-03-00634.jpg`), you can pass the `-start_number` option:

    ffmpeg -r 24 -start_number 634 -i <date as it appears in files>-%05d.jpg -c:v libx265 -crf 28 timelapse.mp4

These commands assume you're inside the folder containing all the images, and output a file named `timelapse.mp4` in the same directory.

### Manual Settings

## 
Installing numpy
`apt install python3-numpy`

The most important settings in terms of determining the timing for the timelapse are the GPS location of the project (saved in `config.py` for potential privacy concerns) and `workingStart` and `workingFinish` in `config.yml`, which represents the earliest and latest hours that the construction workers might work.  The app uses the GPS coordinates of the project to determine sunrise and sunset times and then chooses the latter of sunrise or `workingStart` and the earlier of sunset and `workingFinish` to start and end the timelapse each day.

In order to get the proper time throughout the year you're going to have to sign up for a Google maps API account to be able to get the time zone and daylight saving time updates for the GPS location. [https://developers.google.com/maps/documentation/timezone/get-api-key](https://developers.google.com/maps/documentation/timezone/get-api-key)

For a more pleasing timelapse, it's best to lock in manual settings for exposure and white balance (otherwise the video has a lot of inconsistency from frame to frame). This project allows almost complete control over manual exposure settings through variables in `config.yml`, and below are listed some rules of thumb for your own settings.

> Read more about the [Raspberry Pi's Camera hardware](https://picamera.readthedocs.io/en/latest/fov.html).

### Resolution

The most common and useful Pi Camera resolutions (assuming a V2 camera module—V1 modules have different optimal resolutions) are listed below:

| Size (width x height) | Aspect | Common name        |
| --------------------- | ------ | ------------------ |
| 3280 x 2464           | 4:3    | (max resolution)   |
| 1920 x 1080           | 16:9   | 1080p              |
| 1280 x 720            | 16:9   | 720p (2x2 binning) |
| 640 x 480             | 4:3    | 480p (2x2 binning) |

Binning allows the Pi to sample a grid of four pixels and downsample the average values to one pixel. This makes for a slightly more color-accurate and sharp picture at a lower resolution than if the Pi were to skip pixels when generating the image.

### ISO

ISO is basically an indication of 'light sensitivity'. Without getting too deep in the weeds, you should use lower ISO values (`60` (V2 camera only), `100`, `200`) in bright situations, and higher ISO values (`400`, `800`) in dark situations. There's a lot more to it than that, and as you find out creative ways to use shutter speed and ISO together, those rules go out the window, but for starters, you can choose the following manual values to lock in a particular ISO on the Pi Camera:

- `60` (not available on V1 camera module)
- `100`
- `200`
- `400`
- `800`

### Shutter Speed

Most photographers are familiar with the fractional values for common shutter speeds (1s, 1/10s, 1/30s, 1/60s, etc.), so here's a table to help convert some of the most common shutter speeds into microseconds (the value used in `config.yml`):

| Fractional Shutter Speed | µs      |
| ------------------------ | ------- |
| 6 seconds (max)          | 6000000 |
| 1 second                 | 1000000 |
| 1/8                      | 125000  |
| 1/15                     | 66666   |
| 1/30                     | 33333   |
| 1/60                     | 16666   |
| 1/125                    | 8000    |
| 1/250                    | 4000    |
| 1/500                    | 2000    |
| 1/500                    | 2000    |
| 1/1000                   | 1000    |
| 1/2000                   | 500     |

### White Balance

White balance values on the Raspberry Pi camera are set by adjusting the red and blue gain values—the green value is constant. You need to amplify red and blue certain amounts to set a specific color temperature, and here are some of the settings that worked in specific situations for _my_ camera. Note that you might need to adjust/eyeball things a little better for your own camera, as some unit-to-unit variance is to be expected on such an inexpensive little camera!

| White Balance Setting | Color Temperature (approx) | red_gain | blue_gain |
| --------------------- | -------------------------- | -------- | --------- |
| Clear blue sky        | 8000K+                     | 1.5      | 1.5       |
| Cloudy sky / overcast | 6500K                      | 1.5      | 1.2       |
| Daylight              | 5500K                      | 1.5      | 1.45      |
| Fluorescent / 'cool'  | 4000K                      | 1.3      | 1.75      |
| Incandescent / 'warm' | 2700K                      | 1.25     | 1.9       |
| Candle                | <2000K                     | TODO     | TODO      |

Note: These values will be updated over time as I find more time to calibrate my Pi camera against a few DSLRs and other devices which are much more accurate! Please file an issue if you can help make these mappings better, or find a nicer way to adjust calibrations rather than a `red_gain` and `blue_gain` value.

### Rotation

Depending on the placement of your camera, the picture taken could be upside down. To correct this, set `rotation` to a value of `0` (no rotation), or `90`, `180` or `270` degrees to rotate the image.

## License

MIT License.

## Author

This project is maintained by [Jeff Geerling](https://www.jeffgeerling.com/), author of [Ansible for DevOps](https://www.ansiblefordevops.com/).
