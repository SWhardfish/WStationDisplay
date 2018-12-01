#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Author: Anders Rylander aka Hardfish (https://github.com/SWhardfish) 2018
#Modifications by Hardsfish based on the LoveBootCaptain orignal software.
#The following changes have been made:
#-Modified source to WunderGround
#-Added additional information and sensor readings to display
#-Added Graph based on Matplotlib
#
# MIT License
#
#
# Copyright (c) 2016 LoveBootCaptain (https://github.com/LoveBootCaptain)
# Author: Stephan Ansorge aka LoveBootCaptain
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILI TY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import datetime
from datetime import timedelta
from datetime import time

import json
import os
import threading
import time
import sys

import pygame
import requests
import config

import csv
import pandas
import logging
import locale

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import StrMethodFormatter

logging.basicConfig(filename='logs/WeatherPi_TFT.log',
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO,
    filemode='w')

logging.info('Starting')

os.putenv('SDL_FBDEV', '/dev/fb0')

locale.setlocale(locale.LC_ALL, '')

pygame.init()

pygame.mouse.set_visible(False)

DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 800

BLACK = (0, 0, 0)

DARK_GRAY = (43, 43, 43)
WHITE = (255, 255, 255)
GREY = (233, 233, 233)

RED = (255, 0, 0)

GREEN = (39, 174, 96)
BLUE = (16, 42, 234)

YELLOW = (241, 196, 15)
ORANGE = (238, 153, 18)
BROWN = (227, 174, 87)

ICON_PATH = sys.path[0] + '/icons/'
FONT_PATH = sys.path[0] + '/fonts/'
LOG_PATH = sys.path[0] + '/logs/'
PATH = sys.path[0] + '/'

TFT = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.NOFRAME)
#TFT = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.FULLSCREEN)

pygame.display.set_caption('WeatherPi_TFT')

font_xsmall = pygame.font.Font(FONT_PATH + 'Roboto-Medium.ttf', 10)
font_small = pygame.font.Font(FONT_PATH + 'Roboto-Medium.ttf', 14)
font_big = pygame.font.Font(FONT_PATH + 'Roboto-Medium.ttf', 30)

font_medium_bold = pygame.font.Font(FONT_PATH + 'Roboto-Bold.ttf', 18)
font_small_bold = pygame.font.Font(FONT_PATH + 'Roboto-Bold.ttf', 15)
font_xsmall_bold = pygame.font.Font(FONT_PATH + 'Roboto-Bold.ttf', 10)
font_big_bold = pygame.font.Font(FONT_PATH + 'Roboto-Bold.ttf', 30)

Refresh_Path = ICON_PATH + 'refresh.png'
NoRefresh_Path = ICON_PATH + 'no-refresh.png'
SyncRefresh_Path = ICON_PATH + 'sync-refresh.png'

WiFi_Path = ICON_PATH + 'wifi.png'
NoWiFi_Path = ICON_PATH + 'no-wifi.png'
SyncWiFi_Path = ICON_PATH + 'sync-wifi.png'

API_Path = ICON_PATH + 'api.png'
NoAPI_Path = ICON_PATH + 'Noapi.png'

Path_Path = ICON_PATH + 'path.png'
NoPath_Path = ICON_PATH + 'no-path.png'
SyncPath_Path = ICON_PATH + 'sync-path.png'

WeatherIcon_Path = ICON_PATH + 'unknown.png'

ForeCastIcon_Day_1_Path = ICON_PATH + 'mini_unknown.png'
ForeCastIcon_Day_2_Path = ICON_PATH + 'mini_unknown.png'
ForeCastIcon_Day_3_Path = ICON_PATH + 'mini_unknown.png'

Humidity_Path = ICON_PATH + 'humidity.png'
Pressure_Path = ICON_PATH + 'pressure.png'

MoonIcon_Path = ICON_PATH + 'moon-0.png'
RainIcon1h_Path = ICON_PATH + 'rain-0.png'
RainIcon24h_Path = ICON_PATH + 'rain-0.png'

SunRise_Path = ICON_PATH + 'sunrise.png'
SunSet_Path = ICON_PATH + 'sunset.png'

MoonRise_Path = ICON_PATH + 'moonrise.png'
MoonSet_Path = ICON_PATH + 'moonset.png'

PrecipSnow_Path = ICON_PATH + 'precipsnow.png'
PrecipRain_Path = ICON_PATH + 'preciprain.png'

Wind_Path = ICON_PATH + 'wind.png'
Rain_Path = ICON_PATH + 'rainindicator.png'

WUndergroundLogo_Path = ICON_PATH + 'wundergroundLogo.png'
graph_path = 'Graph1Live.png'

CONNECTION_ERROR = True
REFRESH_ERROR = True
PATH_ERROR = True
PRECIPTYPE = 'NULL'
PRECIPCOLOR = WHITE

skey = config.stationkey
sid = config.stationid

threads = []
json_data = {}

class DrawString:
    def __init__(self, string: object, font: object, color: object, y: object) -> object:
        """
        :param string: the input string
        :param font: the fonts object
        :param color: a rgb color tuple
        :param y: the y position where you want to render the text
        """
        self.string = string
        self.font = font
        self.color = color
        self.y = y
        self.size = self.font.size(self.string)

    def left(self, offset=0):
        """
        :param offset: define some offset pixel to move strings a little bit more left (default=0)
        """

        x = 10 + offset

        self.draw_string(x)

    def right(self, offset=0):
        """
        :param offset: define some offset pixel to move strings a little bit more right (default=0)
        """

        x = (DISPLAY_WIDTH - self.size[0] - 10) - offset

        self.draw_string(x)

    def center(self, parts, part, offset=0):
        """
        :param parts: define in how many parts you want to split your display
        :param part: the part in which you want to render text (first part is 0, second is 1, etc.)
        :param offset: define some offset pixel to move strings a little bit (default=0)
        """

        x = ((((DISPLAY_WIDTH / parts) / 2) + ((DISPLAY_WIDTH / parts) * part)) - (self.size[0] / 2)) + offset

        self.draw_string(x)

    def draw_string(self, x):
        """
        takes x and y from the functions above and render the fonts
        """

        TFT.blit(self.font.render(self.string, True, self.color), (x, self.y))
        logging.info('Class DrawString')


class DrawImage:
    def __init__(self, image_path, y):
        """
        :param image_path: the path to the image you want to render
        :param y: the y-position of the image you want to render
        """

        self.image_path = image_path
        self.image = pygame.image.load(self.image_path)
        self.y = y
        self.size = self.image.get_rect().size

    def left(self, offset=0):
        """
        :param offset: define some offset pixel to move image a little bit more left(default=0)
        """

        x = 10 + offset

        self.draw_image(x)

    def right(self, offset=0):
        """
        :param offset: define some offset pixel to move image a little bit more right (default=0)
        """

        x = (DISPLAY_WIDTH - self.size[0] - 10) - offset

        self.draw_image(x)

    def center(self, parts, part, offset=0):
        """
        :param parts: define in how many parts you want to split your display
        :param part: the part in which you want to render text (first part is 0, second is 1, etc.)
        :param offset: define some offset pixel to move strings a little bit (default=0)
        """

        x = int(((((DISPLAY_WIDTH / parts) / 2) + ((DISPLAY_WIDTH / parts) * part)) - (self.size[0] / 2)) + offset)

        self.draw_image(x)

    def draw_image(self, x):
        """
        takes x from the functions above and the y from the class to render the image
        """

        TFT.blit(self.image, (x, self.y))
        logging.info('Class DrawImage')


class Update:
    @staticmethod
    def update_json():
        logging.info('Update JSON')
        global threads, CONNECTION_ERROR

        thread = threading.Timer(90, Update.update_json)

        thread.start()

        threads.append(thread)

        try:

            request_url = str('http://api.wunderground.com/api/{skey1}/conditions/forecast/astronomy/q/pws:{sid1}.json').format(skey1=skey, sid1=sid)

            data = requests.get(request_url).json()

            with open(LOG_PATH + 'latest_weather.json', 'w') as outputfile:
                json.dump(data, outputfile, indent=2, sort_keys=False)

            print('\njson file saved')

            CONNECTION_ERROR = False

        except (requests.HTTPError, requests.ConnectionError):

            CONNECTION_ERROR = True

            print('Connection ERROR')

            pass

        DrawImage(SyncWiFi_Path, 3).left(2)
        pygame.display.update()


    @staticmethod
    def read_json():
        logging.info('Update ReadJSON')
        global threads, json_data, REFRESH_ERROR
        thread = threading.Timer(90, Update.read_json)
        thread.start()
        threads.append(thread)

        try:
            data = open(LOG_PATH + 'latest_weather.json').read()
            new_json_data = json.loads(data)
            print('\njson file read by module')
            json_data = new_json_data
            REFRESH_ERROR = False

        except IOError:

            REFRESH_ERROR = True

            print('ERROR - json file read by module')

        DrawImage(SyncPath_Path, 9).right(2)
        pygame.display.update()

        time.sleep(1)

        icon_path()

    @staticmethod
    def graph_layer():
        logging.info('Update GraphLayerLog')
        thread = threading.Timer(120, Update.graph_layer)
        thread.start()
        threads.append(thread)

        try:
            graph_temp_string = str(round((json_data['current_observation']['temp_c']), 1))

            xtimestamp = time.strftime('%m-%d-%Y %H:%M:%S')
            temp_graph = "GraphTempDataLive.txt"
            temp_file = open(temp_graph, "a", newline='')
            with temp_file:
                myfields = ['t_stamp', 'temp']
                writer = csv.DictWriter(temp_file, fieldnames=myfields)
                # writer.writeheader()
                writer.writerow({'t_stamp': xtimestamp, 'temp': graph_temp_string})

            df = pandas.read_csv('GraphTempDataLive.txt')

            # convert to datetime
            df['t_stamp'] = pandas.to_datetime(df['t_stamp'])

            # calculate mask
            m1 = df['t_stamp'] >= (pandas.to_datetime('now') - pandas.DateOffset(days=1))
            m2 = df['t_stamp'] <= pandas.to_datetime('now')
            mask = m1 & m2

            # output masked dataframes
            # df[~mask].to_csv('out1.csv', index=False)
            df[mask].to_csv('out2.csv', index=False)

            pygame.display.update()
            logging.info('Def DrawImageLayer-GraphPAth')

        except:

            print('Unable to write Graph Data')

            pass


    @staticmethod
    def graph_image():
        logging.info('Update GraphImageLog')
        thread = threading.Timer(600, Update.graph_image)
        thread.start()
        threads.append(thread)

        try:
            series = pandas.read_csv('out2.csv', usecols=['t_stamp', 'temp'], parse_dates=['t_stamp'])
            series.set_index('t_stamp', inplace=True)

            ax = series.plot(kind='line', legend=True, linewidth=0.5, figsize=(5.2, 1.5))
            ax.set(xlabel='', ylabel='')
            ax.tick_params(axis='x', labelsize=8, colors='white')
            ax.tick_params(axis='y', labelsize=8, colors='white')
            ax.legend(["Temp"], loc='best', fontsize='x-small')
            # set ticks every week
            ax.xaxis.set_major_locator(plt.LinearLocator(6))
            # set major ticks format
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%I %p'))
            ax.yaxis.set_major_formatter(StrMethodFormatter(u"{x:.1f} °C"))
            plt.xticks(rotation=0, horizontalalignment='center')
            # plt.axes(frameon=True)
            plt.grid(which='major', axis='both', color='grey', linestyle='dotted', linewidth=0.5)
            plt.savefig('Graph1Live.png', transparent=True, bbox_inches='tight')
            logging.info('Def DrawImageLayer-GraphImage')

        except:

            print('Unable to write Graph Image')

            pass


    @staticmethod
    def get_precip_type():
        logging.info('Update PrecipType')
        global json_data, PRECIPCOLOR, PRECIPTYPE

        if int(json_data['forecast']['simpleforecast']['forecastday'][0]['pop']) == 0:

            PRECIPTYPE = 'Precipitation'
            PRECIPCOLOR = WHITE

        else:

            precip_type = json_data['forecast']['simpleforecast']['forecastday'][0]['conditions']

            if precip_type == 'rain':

                PRECIPTYPE = 'Rain'
                PRECIPCOLOR = BLUE

            elif precip_type == 'snow':

                PRECIPTYPE = 'Snow'
                PRECIPCOLOR = WHITE

            else:

                PRECIPTYPE = str(precip_type)
                PRECIPCOLOR = RED

        print('\nupdate PRECIPTYPE to: {}'.format(PRECIPTYPE))
        print('\nupdate PRECIPCOLOR to: {}'.format(PRECIPCOLOR))
        print('\nupdated PATH')

    @staticmethod
    def run():
        logging.info('Update RUN')
        Update.update_json()
        Update.read_json()
        Update.graph_layer()
        Update.graph_image()

    logging.info('Class Update')

def icon_path():

    global WeatherIcon_Path, ForeCastIcon_Day_1_Path, \
        ForeCastIcon_Day_2_Path, ForeCastIcon_Day_3_Path, MoonIcon_Path, RainIcon1h_Path, RainIcon24h_Path, PRECIPTYPE, PRECIPCOLOR

    folder_path = ICON_PATH
    icon_extension = '.png'
    mini = 'mini_'

    updated_list = []

    # known conditions:
    # clear-day, clear-night, partly-cloudy-day, partly-cloudy-night, wind, cloudy, rain, snow, fog

    icon = json_data['current_observation']['icon']

    forecast_icon_1 = json_data['forecast']['txt_forecast']['forecastday'][2]['icon']
    forecast_icon_2 = json_data['forecast']['txt_forecast']['forecastday'][4]['icon']
    forecast_icon_3 = json_data['forecast']['txt_forecast']['forecastday'][6]['icon']

    forecast = (str(forecast_icon_1), str(forecast_icon_2), str(forecast_icon_3))

    moon_icon = json_data['moon_phase']['ageOfMoon']
    rain1h_icon = json_data['current_observation']['precip_1hr_metric']
    rain24h_icon = json_data['current_observation']['precip_today_metric']

    moon_icon = int((float(moon_icon)))
    rain1h_icon = int((float(rain1h_icon)))
    rain24h_icon = int((float(rain24h_icon)))

    moon = 'moon-' + str(moon_icon)
    rain1h = 'rain-' + str(rain1h_icon)
    rain24h = 'rain-' + str(rain24h_icon)

    print(icon, forecast, moon_icon)

    WeatherIcon_Path = folder_path + icon + icon_extension

    ForeCastIcon_Day_1_Path = folder_path + mini + forecast[0] + icon_extension
    ForeCastIcon_Day_2_Path = folder_path + mini + forecast[1] + icon_extension
    ForeCastIcon_Day_3_Path = folder_path + mini + forecast[2] + icon_extension

    MoonIcon_Path = folder_path + moon + icon_extension
    RainIcon1h_Path = folder_path + rain1h + icon_extension
    RainIcon24h_Path = folder_path + rain24h + icon_extension

    path_list = [WeatherIcon_Path, ForeCastIcon_Day_1_Path,
                 ForeCastIcon_Day_2_Path, ForeCastIcon_Day_3_Path,
                 MoonIcon_Path, RainIcon1h_Path, RainIcon24h_Path]

    print('\nvalidating path: {}\n'.format(path_list))

    for path in path_list:

        if os.path.isfile(path):

            print('TRUE :', path)

            updated_list.append(path)

        else:

            print('FALSE :', path)

            if 'mini' in path:

                updated_list.append(ICON_PATH + 'mini_unknown.png')

            elif 'moon' in path:

                updated_list.append(ICON_PATH + 'moon-unknown.png')

            elif 'rain' in path:

                updated_list.append(ICON_PATH + 'rain-unknown.png')

            else:

                updated_list.append(ICON_PATH + 'unknown.png')

    WeatherIcon_Path = updated_list[0]
    ForeCastIcon_Day_1_Path = updated_list[1]
    ForeCastIcon_Day_2_Path = updated_list[2]
    ForeCastIcon_Day_3_Path = updated_list[3]
    MoonIcon_Path = updated_list[4]
    RainIcon1h_Path = updated_list[5]
    RainIcon24h_Path = updated_list[6]

    global PATH_ERROR

    if any("unknown" in s for s in updated_list):

        PATH_ERROR = True

    else:

        PATH_ERROR = False

    print('\nupdate path for icons: {}'.format(updated_list))

    Update.get_precip_type()

    DrawImage(SyncRefresh_Path, 9).right(27)
    pygame.display.update()
    logging.info('Def IconPath')

def convert_timestamp(timestamp, param_string):

    """
    :param timestamp: takes a normal integer unix timestamp
    :param param_string: use the default convert timestamp to timestring options
    :return: a converted string from timestamp
    """

    timestring = str(datetime.datetime.fromtimestamp(int(timestamp)).strftime(param_string))

    return timestring

    logging.info('Def ConvertTimestamp')

def draw_wind_layer(y):

    angle = json_data['current_observation']['wind_degrees']

    arrow_icon = pygame.transform.rotate(pygame.image.load(ICON_PATH + 'arrow.png'),
                                         (360 - angle) + 180)  # (360 - angle) + 180

    def draw_middle_position_icon(icon):

        position_x = (DISPLAY_WIDTH - ((DISPLAY_WIDTH / 3) / 2) - (icon.get_rect()[2] / 2))

        position_y = (y - (icon.get_rect()[3] / 2))

        position = (position_x, position_y)

        TFT.blit(icon, position)

    draw_middle_position_icon(arrow_icon)

    print('\nwind direction: {}'.format(angle))

    logging.info('Def DrawWindLayer')

def draw_image_layer():
    logging.info('Def DrawImageLayer-FirstLine')
    if CONNECTION_ERROR:

        DrawImage(NoWiFi_Path, 3).left(2)
        logging.info('Def DrawImageLayer-NoWiFiPath')
    else:

        DrawImage(WiFi_Path, 3).left(2)

    if REFRESH_ERROR:

        DrawImage(NoRefresh_Path, 9).right(27)
        logging.info('Def DrawImageLayer-NoRefreshPath')
    else:

        DrawImage(Refresh_Path, 9).right(27)
        logging.info('Def DrawImageLayer-RefreshPath')
    if PATH_ERROR:

        DrawImage(NoPath_Path, 9).right(2)
        logging.info('Def DrawImageLayer-NoPath')
    else:

        DrawImage(Path_Path, 9).right(2)

    DrawImage(WeatherIcon_Path, 70).center(2, 0)

    if PRECIPTYPE == 'Rain':

        DrawImage(PrecipRain_Path, 150).left(185)
        logging.info('Def DrawImageLayer-PreciRainPath')

    elif PRECIPTYPE == 'Chance of rain':

        DrawImage(PrecipRain_Path, 150).left(185)
        logging.info('Def DrawImageLayer-ChanceRainPath')

    elif PRECIPTYPE == 'Snow':

        DrawImage(PrecipSnow_Path, 150).left(185)
        logging.info('Def DrawImageLayer-PreciSnowPath')

#Checking that the file from WUnderground is current
    logging.info('Def DrawImageLayer-StartCheckWUFile')
    filetime = json_data['current_observation']['observation_time_rfc822']
    filetime = filetime[:-6]
    filetime = datetime.datetime.strptime(filetime, "%a, %d %b %Y %H:%M:%S")
    logging.info('Def DrawImageLayer-WUFileTime')
    today = datetime.datetime.now()

    timediff = timedelta(hours=0.75)

    timebuffer = today - timediff
    logging.info('Def DrawImageLayer-TimeBufferWUFile')
    filevalidity = timebuffer > filetime
    print('new time :', timebuffer)
    print('filetime :', filetime)
    print('now > filetime :', filevalidity)
    logging.info('Def DrawImageLayer-FileValidityWUFile')
    if not filevalidity:

        DrawImage(API_Path, 7).right(53)
        logging.info('Def DrawImageLayer-APIPathWUFile')

    else:

        DrawImage(NoAPI_Path, 7).right(53)
        logging.info('Def DrawImageLayer-NoAPIPathWUFile')

    DrawImage(ForeCastIcon_Day_1_Path, 260).center(3, 0)
    DrawImage(ForeCastIcon_Day_2_Path, 260).center(3, 1)
    DrawImage(ForeCastIcon_Day_3_Path, 260).center(3, 2)
    logging.info('Def DrawImageLayer-ForeCastIcon')

    DrawImage(Pressure_Path, 400).center(3,1)
    DrawImage(Humidity_Path, 440).center(3,1,4)

    draw_wind_layer(434)
    DrawImage(Wind_Path, 416).right(4)
    logging.info('Def DrawImageLayer-WindLayer')

    DrawImage(SunRise_Path, 517).left(35)
    DrawImage(SunSet_Path, 541).left(35)

    DrawImage(MoonIcon_Path, 510).center(1, 0)
    logging.info('Def DrawImageLayer-MoonIcon')

    DrawImage(RainIcon1h_Path, 400).center(3,0,-29)
    DrawImage(RainIcon24h_Path, 400).center(3,0,29)
    DrawImage(Rain_Path, 400).center(3,0)
    logging.info('Def DrawImageLayer-RainPath')

    DrawImage(MoonRise_Path, 515).left(362)
    DrawImage(MoonSet_Path, 544).left(364)

    DrawImage(WUndergroundLogo_Path, 760).left(5)
    logging.info('Def DrawImageLayer-WUlogo')

    DrawImage(graph_path, 600).left(0)
    logging.info('Def DrawImageLayer-GraphPAth')

    print('\n' + WeatherIcon_Path)
    print(ForeCastIcon_Day_1_Path)
    print(ForeCastIcon_Day_2_Path)
    print(ForeCastIcon_Day_3_Path)
    print(MoonIcon_Path)
    print(RainIcon1h_Path)
    print(RainIcon24h_Path)
    logging.info('Def DrawImageLayer-Print')

    logging.info('Def DrawImageLayer')

def draw_time_layer():
    timestamp = time.time()

    date_time_string = convert_timestamp(timestamp, '%H:%M:%S')
    date_day_string = convert_timestamp(timestamp, '%A - %d %b %Y')

    print('\nDay: {}'.format(date_day_string))
    print('Time: {}'.format(date_time_string))

    DrawString(date_day_string, font_small_bold, WHITE, 10).center(1, 0)
    DrawString(date_time_string, font_big_bold, WHITE, 25).center(1, 0)

    logging.info('Def DrawTimeLayer')

def draw_text_layer():
    summary_string = json_data['current_observation']['weather']
    temp_out_string = str(round((json_data['current_observation']['temp_c']), 1)) + ' °C'
    rain_string = str(int(json_data['forecast']['simpleforecast']['forecastday'][0]['pop'])) + ' %'

    pressure_string = str(int((json_data['current_observation']['pressure_mb']))) + ' mb'

    forecast_day_1_string = json_data['forecast']['simpleforecast']['forecastday'][1]['date']['weekday_short']
    forecast_day_2_string = json_data['forecast']['simpleforecast']['forecastday'][2]['date']['weekday_short']
    forecast_day_3_string = json_data['forecast']['simpleforecast']['forecastday'][3]['date']['weekday_short']

    forecast_day_0_min_max_string = json_data['forecast']['simpleforecast']['forecastday'][0]['low']['celsius'] + ' | ' + json_data['forecast']['simpleforecast']['forecastday'][0]['high']['celsius'] + ' °C'
    forecast_day_1_min_max_string = json_data['forecast']['simpleforecast']['forecastday'][1]['low']['celsius'] + ' | ' + json_data['forecast']['simpleforecast']['forecastday'][1]['high']['celsius']
    forecast_day_2_min_max_string = json_data['forecast']['simpleforecast']['forecastday'][2]['low']['celsius'] + ' | ' + json_data['forecast']['simpleforecast']['forecastday'][2]['high']['celsius']
    forecast_day_3_min_max_string = json_data['forecast']['simpleforecast']['forecastday'][3]['low']['celsius'] + ' | ' + json_data['forecast']['simpleforecast']['forecastday'][3]['high']['celsius']

    sunrise_string = json_data['moon_phase']['sunrise']['hour'] + ':' + json_data['moon_phase']['sunrise']['minute']
    sunset_string = json_data['moon_phase']['sunset']['hour'] + ':' + json_data['moon_phase']['sunset']['minute']

    moon_phase = json_data['moon_phase']['phaseofMoon']
    moon_illum_string = str(int(json_data['moon_phase']['percentIlluminated'])) + ' %'

    moonrise_string = json_data['moon_phase']['moonrise']['hour'] + ':' + json_data['moon_phase']['moonrise']['minute']
    moonset_string = json_data['moon_phase']['moonset']['hour'] + ':' + json_data['moon_phase']['moonset']['minute']

    north_string = 'N'
    kms_string = 'km/h'
    wind_speed_string = str(round((float(json_data['current_observation']['wind_kph']) * 1.609344), 1))

    rain_hour_string0 = '1h'
    rain_hour_string = str(json_data['current_observation']['precip_1hr_metric']) + 'mm'
    rain_today_string0 = '24h'
    rain_today_string = str(json_data['current_observation']['precip_today_metric']) + 'mm'

    relhumidity_string = str(json_data['current_observation']['relative_humidity'])

    draw_time_layer()

    DrawString(summary_string, font_small_bold, WHITE, 185).center(2, 0)

    DrawString(temp_out_string, font_big, WHITE, 105).left(185)

    DrawString(rain_string, font_small_bold, PRECIPCOLOR, 150).left(210)
    DrawString(PRECIPTYPE, font_small_bold, PRECIPCOLOR, 150).left(255)

    DrawString(forecast_day_1_string, font_medium_bold, RED, 225).center(3, 0)
    DrawString(forecast_day_2_string, font_medium_bold, RED, 225).center(3, 1)
    DrawString(forecast_day_3_string, font_medium_bold, RED, 225).center(3, 2)

    DrawString(forecast_day_0_min_max_string, font_big, WHITE, 105).left(310)
    DrawString(forecast_day_1_min_max_string, font_small_bold, WHITE, 245).center(3, 0)
    DrawString(forecast_day_2_min_max_string, font_small_bold, WHITE, 245).center(3, 1)
    DrawString(forecast_day_3_min_max_string, font_small_bold, WHITE, 245).center(3, 2)

    DrawString(sunrise_string, font_small_bold, WHITE, 520).left(65)
    DrawString(sunset_string, font_small_bold, WHITE, 547).left(65)

    DrawString(moon_illum_string, font_small_bold, WHITE, 550).left(265)
    DrawString(moon_phase, font_xsmall_bold, WHITE, 570).center(1, 0)

    DrawString(moonrise_string, font_small_bold, WHITE, 520).left(392)
    DrawString(moonset_string, font_small_bold, WHITE, 547).left(392)

    DrawString(north_string, font_small_bold, WHITE, 380).center(3, 2)
    DrawString(wind_speed_string, font_small_bold, WHITE, 420).center(3, 2)
    DrawString(kms_string, font_xsmall, WHITE, 435).center(3, 2)

    DrawString(rain_hour_string0, font_small_bold, WHITE, 380).center(3,0,-30)
    DrawString(rain_hour_string, font_small_bold, WHITE, 465).center(3,0,-29)
    DrawString(rain_today_string0, font_small_bold, WHITE, 380).center(3,0,29)
    DrawString(rain_today_string, font_small_bold, WHITE, 465).center(3,0,29)
    #DrawString(pressure_string0, font_small_bold, WHITE, 395).left(40)
    DrawString(pressure_string, font_small_bold, WHITE, 412).center(3,1,55)
    #DrawString(relhumidity_string0, font_small_bold, WHITE, 415).left(40)
    DrawString(relhumidity_string, font_small_bold, WHITE, 452).center(3,1,43)

    print('\nsummary: {}'.format(summary_string))
    print('temp out: {}'.format(temp_out_string))
    print('temp min|max: {}'.format(forecast_day_0_min_max_string))
    print('{}: {}'.format(PRECIPTYPE, rain_string))
    print('pressure mb: {}'.format(pressure_string))
    print('forecast: '
          + forecast_day_1_string + ' ' + forecast_day_1_min_max_string + ' ; '
          + forecast_day_2_string + ' ' + forecast_day_2_min_max_string + ' ; '
          + forecast_day_3_string + ' ' + forecast_day_3_min_max_string
          )
    print('sunrise: {} ; sunset {}'.format(sunrise_string, sunset_string))
    print('WindSpeed: {}'.format(wind_speed_string))

    logging.info('Def DrawTextLayer0')

def draw_to_tft():
    TFT.fill(BLACK)
    logging.info('Def DrawtoTFT-TFT.fill')
    draw_image_layer()
    logging.info('Def DrawtoTFT-DrawImageLayer')
    draw_text_layer()
    logging.info('Def DrawtoTFT-DrawTextLayer')
    #RectangleMain = pygame.Rect(0, 50, 480, 599)
    #pygame.display.update(RectangleMain)
    #pygame.display.update()
    pygame.display.flip()
    logging.info('Def DrawtoTFT-PygameDisplayUpdate')
    time.sleep(1)

    logging.info('Def DrawtoTFT')

def quit_all():
    global threads

    for thread in threads:
        thread.cancel()
        thread.join()

    pygame.quit()
    quit()

    logging.info('Def QuitAll')

def loop():
    Update.run()
    logging.info('Def Loop-UpdateRun')
    running = True
    logging.info('Loop Running0: %s', running)
    logging.info('Def Loop-BeforeWhileRunning')
    while running:
        logging.info('Loop Running1: %s', running)
        logging.info('Def Loop-WhileRunning')
        draw_to_tft()
        logging.info('Loop Running2: %s', running)
        logging.info('Def Loop-DrawtoTFT')
        for event in pygame.event.get():
            logging.info('Def Loop-PygameEventGet')
            if event.type == pygame.QUIT:
                logging.info('Def Loop-PygameQuit')
                running = False

                quit_all()

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    running = False

                    quit_all()

                elif event.key == pygame.K_SPACE:

                    print('SPACE')

    quit_all()

    logging.info('Def Loop')

if __name__ == '__main__':

    try:

        loop()

    except KeyboardInterrupt:

        quit_all()
