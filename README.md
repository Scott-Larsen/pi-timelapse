# Construction Cam

This is a timelapse camera/ app designed to monitor construction progress at a remote site. If you have access to the internet at the jobsite you'll be able to receive daily timelapse videos, 'metatimelapses' of the entire project as well as to trigger livestreaming to Twitch from a [companion Flask app]("https://github.com/Scott-Larsen/pi-timelapse-flask-app") for up to the moment updates.

This project is built off of the excellent [Raspberry Pi Time-Lapse App]("https://github.com/geerlingguy/pi-timelapse") by [Jeff Geerling]("https://www.youtube.com/c/JeffGeerling"), without whom I'm not sure that I could have pulled it all together.

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

### Triggering the Raspberry Pi daily

In order to get the timelapse to run daily it's necessary to set a cronjob on the Raspberry Pi. In the terminal type the following:

`crontab -e`

In the editor window that opens, enter the following command:

`ENTER COMMAND`

This will start the script at \***\*5AM\*\*** every day, before the earliest sunrise of the year. Incidentally, the project was built on the understanding that the Raspberry Pi's clock was not set away from UTC and I am on Eastern US Time Zone (UTC-05:00 - New York) so you may have to make adjustments to the trigger times for your location.

While we're editing the crontab, and since the Raspberry Pi will be at a remote site and inaccessible to me, I wanted to add a second command to restart the Pi once a day to make sure it recovered if it had any issue. Because of that I also entered:

`ENTER COMMAND`

This will restart the pi once a day at **\***AM**\***

When you've entered both commands, close and save the file (`control-x` and `control-s` in Nano).

## Creating videos and 'metatimelapses'

### Videos

Requirements: You should install [FFmpeg](https://ffmpeg.org) — `sudo apt-get -y install ffmpeg`)

If you have `create_video` set to `True` in `config.yml`, the Pi will also generate a video immediately following the conclusion of the capture.

> Note: Video generation can take a very long time on slower Pis, like the Pi Zero, A+, or original A or B.

### Metatimelapses

If you'd like a 'metatimelapse' - a timelapse spanning the entire length of the project, set `create_metatimelapse` to `True` in `config.yml`.

### Manually Compiling Videos with `ffmpeg`

You can use `ffmpeg` on other platforms to put together image sequences after the fact. For example, to take a sequence like `2021-01-03-00000.jpg` to `2021-01-03-00999.jpg` and generate an MP4 video, swap `<date as it appears in files>` in the commande below with `2021-01-03` and run it in the terminal:

    ffmpeg -r 24 -i <date as it appears in files>-%05d.jpg -c:v libx265 -crf 28 timelapse.mp4

And if you wanted to start the video in the middle of the sequence (e.g. instead of starting at `2021-01-03-00000.jpg`, start at `2021-01-03-00634.jpg`), you can pass the `-start_number` option:

    ffmpeg -r 24 -start_number 634 -i <date as it appears in files>-%05d.jpg -c:v libx265 -crf 28 timelapse.mp4

These commands assume you're inside the folder containing all the images, and output a file named `timelapse.mp4` in the same directory.

## Manual Settings

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
