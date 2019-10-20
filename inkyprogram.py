#!/usr/bin/env python
# -*- coding: utf-8 -*-



import glob
import time
import argparse
from inky import InkyPHAT
from PIL import Image, ImageDraw, ImageFont
from font_fredoka_one import FredokaOne
import httplib, urllib, base64
import json

try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")

try:
    import geocoder
except ImportError:
    exit("This script requires the geocoder module\nInstall with: sudo pip install geocoder")

try:
    from bs4 import BeautifulSoup
except ImportError:
    exit("This script requires the bs4 module\nInstall with: sudo pip install beautifulsoup4")



CITY = "Exeter"
COUNTRYCODE = "GB"
WARNING_TEMP = 25.0


inky_display = InkyPHAT("yellow")
inky_display.set_border(inky_display.WHITE)
font = ImageFont.truetype(FredokaOne, 22)

img = Image.open("lowlevel4.png")
img2 = Image.open("highlevel2.png")
#draw = ImageDraw.Draw(img)

def rotated_text(imagename, text):
    txt = Image.new('1', (w, w))
    draw = ImageDraw.Draw(txt)
    draw.text((0, 0), text, 1, font)
    imagename.paste(inky_display.BLACK, (-10, 50), txt.rotate(270))

def get_coords(address):
    g = geocoder.arcgis(address)
    coords = g.latlng
    return coords

def get_weather(address):
    coords = get_coords(address)
    weather = {}
    res = requests.get("https://darksky.net/forecast/{}/uk212/en".format(",".join([str(c) for c in coords])))
    if res.status_code == 200:
        soup = BeautifulSoup(res.content, "lxml")
        curr = soup.find_all("span", "currently")
        weather["summary"] = curr[0].img["alt"].split()[0]
        weather["temperature"] = int(curr[0].find("span", "summary").text.split()[0][:-1])
        press = soup.find_all("div", "pressure")
        weather["pressure"] = int(press[0].find("span", "num").text)
        return weather
    else:
        return weather
    
def get_tides():
    print('getting tides')
    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': '',
    }

    params = urllib.urlencode({
        # Request parameters
        'duration': '1',
    })

    try:
        print('trying api')
        conn = httplib.HTTPSConnection('admiraltyapi.azure-api.net')
        conn.request("GET", "/uktidalapi/api/V1/Stations/0027/TidalEvents?%s" % params, None, headers)
        print('making connection')
        response = conn.getresponse()
        print(response.status)
        data = response.read()
        print(data)
        tides = json.loads(data)
        print(tides[1]["EventType"][:-5])
        print(tides[1]["DateTime"][11:16])
        print(tides[2]["EventType"][:-5])
        print(tides[2]["DateTime"][11:16])
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))


#x = (inky_display.WIDTH / 2) - (w / 2)
#y = (inky_display.HEIGHT / 2) - (h / 2)


datetime = time.strftime("%d/%m %H:%M")

message = "2010"
w, h = font.getsize(message)
rotated_text(img, message)

message2 = "2030"
w, h = font.getsize(message2)
rotated_text(img2, message2)
get_tides()
#draw.text((36, 12), datetime, inky_display.YELLOW, font=font)
#draw.text((x, y), message, inky_display.BLACK, font)
#while True:
inky_display.set_image(img)
inky_display.show()
#    time.sleep(5)
#    inky_display.set_image(img2)
#    inky_display.show()