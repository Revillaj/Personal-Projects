#!/usr/bin/env python3
import cv2
from ppadb.client import Client as AdbClient
import os
import time


# ******************* installation instructions *******************
# --- on raspberry pi ---
# sudo apt-get update && sudo apt-get upgrade
# sudo apt-get install android-tools-adb
# sudo pip install opencv-contrib-python
# sudo pip install pure-python-adb

# --- on phone ---
# make sure phone and computer are a trusted source, try "adb devices"
# https://stackoverflow.com/questions/23081263/adb-android-device-unauthorized
# make sure phone is connected to raspberry
# into terminal type in "adb tcpip 5555"
# into terminal type in "adb shell ip addr show wlan0" and copy the IP address after the "inet" until the "/"
# into terminal type in "adb connect ip-address-of-device:5555"
# your phone should be connected wirelessly to the raspberry pi
# https://help.famoco.com/developers/dev-env/adb-over-wifi/

# --- get activity name ---
# adb shell dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'

# --- on code ---
# all you should change is variable phone_ip on line 94 to the ip address of your phone

# --- running in background ---
# if you want to run in the background
# python3 wynn.py &
# https://www.geeksforgeeks.org/running-python-program-in-the-background/


def deviceconnection():
    global device
    client = AdbClient("127.0.0.1", port=5037)
    client.remote_connect(phone_ip, 5555)
    device = client.device(phone_ip + ":5555")
    print(device.shell('getprop ro.product.model'), len(AdbClient().devices()))


def restart():
    print('restart')
    device.shell('am force-stop com.torpedolabs.wynn.slots')
    time.sleep(5)
    device.shell('am start -n com.torpedolabs.wynn.slots/com.unity3d.player.UnityPlayerActivity')
    time.sleep(5)


def openApp():
    print('Opening ' + Game)
    device.shell('am start -n com.torpedolabs.wynn.slots/com.unity3d.player.UnityPlayerActivity')
    time.sleep(5)


def screenShot():
    image = device.screencap()
    with open(Game + '.png', 'wb') as f:
        f.write(image)


def tap(location):
    device.shell('input tap ' + str(location[0]) + " " + str(location[1]))


def comparison():
    screenShot()
    haystack_img = cv2.imread(Game + '.png', cv2.IMREAD_UNCHANGED)
    while True:
        try:
            gray_Haystack = cv2.cvtColor(haystack_img, cv2.COLOR_BGR2GRAY)
            break;
        except AssertionError:
            print(AssertionError)
            continue

    for x in range(numberofpictures):
        needle_img = cv2.imread('grayed' + Game + '/' + str(x + 1) + '.png', cv2.IMREAD_UNCHANGED)
        result = cv2.matchTemplate(gray_Haystack, needle_img, cv2.TM_CCOEFF_NORMED)
        max_val = cv2.minMaxLoc(result)[1]
        max_loc = cv2.minMaxLoc(result)[3]
        if max_val > .88:
            if str(x + 1) == 5:
                restart()
                break
            print(str(x + 1) + '.png', round(max_val, 2), max_loc)
            tap(max_loc)
            break


def convert():
    global numberofpictures
    numberofpictures = len(os.listdir('templates' + Game))
    try:
        os.mkdir('grayed' + Game)
    except OSError:
        pass
    for x in range(numberofpictures):
        needle_img = cv2.imread('templates' + Game + '/' + str(x + 1) + '.png', cv2.IMREAD_UNCHANGED)
        gray_Needle = cv2.cvtColor(needle_img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite('grayed' + Game + '/' + str(x + 1) + '.png', gray_Needle)


Game = 'wynn'
numberofpictures = 0
phonenumber = 0
counter = 0
device = None
phone_ip = '192.168.10.15'

deviceconnection()
convert()
# restart()
while True:
    counter += 1
    activeApp = (device.shell("dumpsys window windows | grep -E 'mCurrentFocus'"))
    if counter >= 2000:
        restart()
        counter = 0
    if Game not in activeApp:
        openApp()
    time.sleep(1)
    comparison()
    time.sleep(10)
