import requests
import base64
import io
import os
import json
import argparse
import configparser
import time

url_root = "http://164.90.158.133:8080"
url_get_speech = "/to_speech"
url_get_speaker = "/get_speaker"
url_get_audios = "/is_ready"
path_menu = './Menu.ini'
path_st = './Sentences.ini'
path_cus = './Customer.ini'

# read the ini file to string
def read_config(path_to_ini):
    with open(path_to_ini, "r") as f:
        config = f.read()
    return config

# tell if the audio file is ready, since generating all 
# audio files will probably takes a long time and it will time out
# the client.
def is_ready():
    pass

# get all speech audio files and unzip them into './audios/'
def get_speeches(menu, customers, sentences):
    req = {}
    req["menu"] = read_config(menu)
    req["customers"] = read_config(customers)
    req["sentences"] = read_config(sentences)
    result = requests.post(url_root+url_get_speech, json=req)
    # download the file when it is ready
    # or maybe we can print a progress bar here
    print("Log:\t%s"%result.text)
    if result.status_code == 200:
        while True:
            time.sleep(5)
            result = requests.get(url_root+url_get_audios, stream=True)
            if result.status_code == 200:
                with open("./speech_audios.zip", "wb") as f:
                    f.write(result.content)
                print("log:\tsaved all files to ./speech_audios.zip")
                break

# get and save speakers into ./speakers.ini
def get_speakers(path_to_speaker):
    result = requests.get(url_root+url_get_speaker)
    if result.status_code == 200:
        speakers = result.json()
        if type(speakers) == str:
            speakers = speakers.strip("[").strip("]").split(",")
        config_speakers = configparser.ConfigParser()
        dict_speakers = {}
        # import pdb
        # pdb.set_trace()
        for idx, spk in enumerate(speakers):
            dict_speakers["%03d"%idx] = spk.strip(" ").strip("\"")
        config_speakers["speakers"] = dict_speakers
        with open(path_to_speaker, "w") as f:
            config_speakers.write(f)
        print("Log:\tspeakers are saved to %s"%path_to_speaker)
    else:
        print("Error:\tfailed to get correct speak info")

# verify if all needed audio files are ready
def verify_speeches(menu, customers, sentences):
    pass

if __name__ == "__main__":
    # parse cmd lines
    parser = argparse.ArgumentParser()
    parser.add_argument('--speech', action='store_true',
        help="get all speech audios in a zip file")
    parser.add_argument('--speaker', action='store_true',
        help="get all speaker id and put them into ./speaker.ini")
    parser.add_argument("--menu", type=str, default='./Menu.ini',
        help="the path to menu config file, default is ./Menu.ini")
    parser.add_argument("--customers", type=str, default='./Customer.ini',
        help="the path to customer config file, default is ./Customer.ini")
    parser.add_argument("--sentences", type=str, default='./Sentences.ini',
        help="the path to sentence template file, default is ./Sentences.ini")
    parser.add_argument("--speakers", type=str, default='./Speakers.ini',
        help="the path to save speaker keys, default is ./Speakers.ini")
    args = parser.parse_args()

    # send request and get result
    if args.speech:
        get_speeches(args.menu, args.customers, args.sentences)
    elif args.speaker:
        get_speakers(args.speakers)
    else:
        print("Log:\tno commands found, please indicate one operation you want")
        parser.print_help()