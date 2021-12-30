import requests
import base64
import io
import os
import json
import argparse
import configparser

url = "http://164.90.158.133:8080"
to_speech = "/to_speech"


# data =  {
#             "order": ["00", "10", "20", "30"],
#             "speaker": "p225"
#         }


speakers = {'ED\n': 0, 'p225': 1, 'p226': 2, 'p227': 3, 'p228': 4, 'p229': 5, 
    'p230': 6, 'p231': 7, 'p232': 8, 'p233': 9, 'p234': 10, 'p236': 11, 'p237': 12, 
    'p238': 13, 'p239': 14, 'p240': 15, 'p241': 16, 'p243': 17, 'p244': 18, 'p245': 19, 
    'p246': 20, 'p247': 21, 'p248': 22, 'p249': 23, 'p250': 24, 'p251': 25, 'p252': 26, 
    'p253': 27, 'p254': 28, 'p255': 29, 'p256': 30, 'p257': 31, 'p258': 32, 'p259': 33, 
    'p260': 34, 'p261': 35, 'p262': 36, 'p263': 37, 'p264': 38, 'p265': 39, 'p266': 40, 
    'p267': 41, 'p268': 42, 'p269': 43, 'p270': 44, 'p271': 45, 'p272': 46, 'p273': 47, 
    'p274': 48, 'p275': 49, 'p276': 50, 'p277': 51, 'p278': 52, 'p279': 53, 'p280': 54, 
    'p281': 55, 'p282': 56, 'p283': 57, 'p284': 58, 'p285': 59, 'p286': 60, 'p287': 61, 
    'p288': 62, 'p292': 63, 'p293': 64, 'p294': 65, 'p295': 66, 'p297': 67, 'p298': 68, 
    'p299': 69, 'p300': 70, 'p301': 71, 'p302': 72, 'p303': 73, 'p304': 74, 'p305': 75, 
    'p306': 76, 'p307': 77, 'p308': 78, 'p310': 79, 'p311': 80, 'p312': 81, 'p313': 82, 
    'p314': 83, 'p316': 84, 'p317': 85, 'p318': 86, 'p323': 87, 'p326': 88, 'p329': 89, 
    'p330': 90, 'p333': 91, 'p334': 92, 'p335': 93, 'p336': 94, 'p339': 95, 'p340': 96, 
    'p341': 97, 'p343': 98, 'p345': 99, 'p347': 100, 'p351': 101, 'p360': 102, 'p361': 103, 
    'p362': 104, 'p363': 105, 'p364': 106, 'p374': 107, 'p376': 108}
    
# read the ini file
def read_config(path_to_ini):
    config = configparser.ConfigParser()
    config.read(path_to_ini)
    return config

# send 
def

def get_speeches(menu, customers, sentences):
    data = []
    result = requests.post(url+to_speech, json = json.dumps(data))

if __name__ == "__main__":
    # parse cmd lines
    parser = argparse.ArgumentParser()
    parse.add_argument('--to_speech', type=str, 
        help="get all speech audios in a zip file")
    parse.add_argument('--get_speaker', type=str, 
        help="get all speaker id and put them into ./speaker.ini")

    parser.add_argument("--menu", type=str, defualt='./menu.ini',
        help="the path to menu config file, defualt is ./menu.ini")
    parser.add_argument("--customers", type=str, defualt='./Customer.ini',
        help="the path to customer config file, defualt is ./Customer.ini")
    parser.add_argument("--sentences", type=str, defualt='./sentences.ini',
        help="the path to sentence template file, defualt is ./sentences.ini")
    args = parser.parse_args()

    # send request and get result