#!/usr/bin/env python3
import os
import requests

from subprocess import check_output
from PIL import Image

SUBREDDIT = "EarthPorn"
USER_AGENT = "javiber-bot"
WALLPAPER_PATH = "/home/javiber/.config/background.jpg"
LOCK_IMAGE_PATH = "/home/javiber/.config/lock.png"
LOCK_ICON_PATH = "/home/javiber/.config/lock_icon.png"

def get_posts():
    headers = {"User-agent": USER_AGENT}
    url = "https://www.reddit.com/r/{}/top.json".format(SUBREDDIT)
    list_response = requests.get(url, headers=headers)
    list_response.raise_for_status()

    return list_response.json()


def get_monitor_resolution():
    resolution = check_output("xrandr".split())
    resolution = next((l for l in resolution.split("\n") if "*" in l), "")
    resolution = resolution.strip().split(" ")[0]
    return map(int, resolution.split("x"))


def download_image(post):
    url = post["data"]["url"]
    if not url:
        return False

    image_response = requests.get(url)
    if image_response.headers["Content-Type"] != "image/jpeg":
        return False

    with open(WALLPAPER_PATH, "w") as f:
        f.write(image_response.content)

    return WALLPAPER_PATH


def set_background(path):
    check_output(["feh", "--bg-fill", path])


def resize_img(image):
    width = image.size[0]
    height = image.size[1]

    aspect = width / float(height)

    ideal_width, ideal_height = get_monitor_resolution()

    ideal_aspect = ideal_width / float(ideal_height)

    if aspect > ideal_aspect:
        # Then crop the left and right edges:
        new_width = int(ideal_aspect * height)
        offset = (width - new_width) / 2
        resize = (offset, 0, width - offset, height)
    else:
        # ... crop the top and bottom:
        new_height = int(width / ideal_aspect)
        offset = (height - new_height) / 2
        resize = (0, offset, width, height - offset)

    thumb = image.crop(resize).resize(
        (ideal_width, ideal_height), Image.ANTIALIAS)
    thumb.save(WALLPAPER_PATH)


def create_lock_image(path):
    if os.path.isfile(path):
        check_output([
            "convert", path, "-channel", "RGBA", "-blur", "0x8",
            LOCK_IMAGE_PATH])

        check_output([
            "convert", LOCK_IMAGE_PATH, LOCK_ICON_PATH, "-gravity",
            "center", "-composite", "-matte", LOCK_IMAGE_PATH])


if __name__ == "__main__":
    if os.path.isfile(WALLPAPER_PATH):
        set_background(WALLPAPER_PATH)
    x, y = get_monitor_resolution()
    target_aspect_ratio = float(x) / y
    min_ar = target_aspect_ratio - 0.5
    max_ar = target_aspect_ratio + 0.5

    posts = get_posts()

    for p in posts["data"]["children"]:
        path = download_image(p)
        if path:
            image = Image.open(WALLPAPER_PATH)
            image_aspect_ration = float(image.size[0]) / float(image.size[1])

            if (min_ar < image_aspect_ration < max_ar):
                resize_img(image)
                set_background(WALLPAPER_PATH)
                break

    create_lock_image(WALLPAPER_PATH)
