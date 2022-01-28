import requests
import base64
import io
import os
import json
import argparse
import configparser
import time
import zipfile
from tqdm import tqdm
# usage:
# python run_client_test.py -c  -customers ./../Customer.ini -o ./../../Assets/Resources/speech_audios/
#python run_client_test.py -d -o./hiddenrequest/
#python run_client_test.py -s -o ./../../Assets/Resources/StaffRespond/
# python run_client_test.py  -ms -o ./test/
'''
usage: run_client_test.py [-h] [-a] [-c] [-d] [-s] [-g] [-t] [-ms] [-o O]
                          [-misc MISC] [-customers CUSTOMERS]
                          [-sentences SENTENCES] [-speakers SPEAKERS]
                          [-stuff STUFF]

optional arguments:
  -h, --help            show this help message and exit
  -a                    all speeches for customer and stuff, including hidden
                        request events, so this command equivalent to -c -d -s
  -c                    customer's speech
  -d                    hidden event speeches (asking more dinner sets)
  -s                    staff response speeches
  -g                    get all speaker id and save to ./speaker.ini
  -t                    traverse sample sentence by all speakers
  -ms                   misc speeches (could be any text speaked by any speaker)
                        specified in 'misc.ini'
  -o O                  the path to save generated audios
  -misc MISC            misc config, default is ./Misc.ini
  -customers CUSTOMERS  customer event config, default is ./CustTest.ini
  -sentences SENTENCES  sentence template config, default is ./Sentences.ini
  -speakers SPEAKERS    speaker list, default is ./Speakers.ini
  -stuff STUFF          stuff event config, default is ./StaffRespond.ini
'''
url_root = "http://164.90.158.133:8080"
url_get_speech = "/to_speech"
url_get_speech_aug = "/to_speech_aug"
url_get_speech_stuff = "/to_speech_stuff"
url_get_speech_misc = "/to_speech_misc"
url_get_speaker = "/get_speaker"
url_get_audios = "/is_ready"

path_menu = './Misc.ini'
path_st = './Sentences.ini'
path_cus = './CustTest.ini'

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
def get_speeches(misc, customers, sentences, output):
    req = {}
    req["misc"] = read_config(misc)
    req["customers"] = read_config(customers)
    req["sentences"] = read_config(sentences)
    result = requests.post(url_root+url_get_speech, json=req)
    # download the file when it is ready
    # or maybe we can print a progress bar here
    post_to_url(result, url_root+url_get_audios, output)

def post_to_url(result, url, output):
    prog_old = 0
    prog_new = 0
    if result.status_code != 200:
        print("Log:\t%s"%result.text)
    else:
        print("Log:\t%s"%result.text)
        if "processing" in result.text:
            pid = result.text.split(" ")[-1]
            bar = tqdm()
            bar.total = 100
            while True:
                # update every 10s
                time.sleep(5)
                result_check = requests.post(url, data=pid, stream=True)
                if result_check.status_code == 200:
                    bar.update(100 - prog_old)
                    if os.path.exists(output) == False:
                        os.mkdir(output)
                    zip_path_temp = os.path.join(output, "speech_audios.zip")
                    with open(zip_path_temp, "wb") as f:
                        f.write(result_check.content)
                    with zipfile.ZipFile(zip_path_temp, 'r') as zip_ref:
                        zip_ref.extractall(output)
                    # clean up
                    os.remove(zip_path_temp)
                    break
                else:
                    try:
                        prog_old = prog_new
                        prog_new = float(result_check.text)
                        bar.update(prog_new - prog_old)
                    except:
                        pass

# get all speech audio files and unzip them into './audios/'
def get_speeches_aug(sentences, output):
    req = {}
    req["sentences"] = read_config(sentences)
    result = requests.post(url_root+url_get_speech_aug, json=req)
    # download the file when it is ready
    # or maybe we can print a progress bar here
    post_to_url(result, url_root+url_get_audios, output)

def get_speeches_stuff(stuff, output):
    req = {}
    req["stuff"] = read_config(stuff)
    result = requests.post(url_root+url_get_speech_stuff, json=req)
    # download the file when it is ready
    # or maybe we can print a progress bar here
    post_to_url(result, url_root+url_get_audios, output)

def get_speeches_misc(speaker, misc, output, traverse=False):
    req = {}
    req["misc"] = read_config(misc)
    if os.path.exists(speaker) == False:
        get_speakers(speaker)
    req["speakers"] = read_config(speaker)
    req["traverse"] = traverse
    result = requests.post(url_root+url_get_speech_misc, json=req)
    # download the file when it is ready
    # or maybe we can print a progress bar here
    post_to_url(result, url_root+url_get_audios, output)


# get and save speakers into ./speakers.ini
def get_speakers(path_to_speaker):
    result = requests.get(url_root+url_get_speaker)
    if result.status_code == 200:
        speakers = result.json()
        if type(speakers) == str:
            speakers = speakers.strip("[").strip("]").split(",")
        config_speakers = configparser.ConfigParser()
        dict_speakers = {}
        for idx, spk in enumerate(speakers):
            dict_speakers["%03d"%idx] = spk.strip(" ").strip("\"")
        config_speakers["speakers"] = dict_speakers
        with open(path_to_speaker, "w") as f:
            config_speakers.write(f)
        print("Log:\tspeakers are saved to %s"%path_to_speaker)
    else:
        print("Error:\tfailed to get correct speak info")

# verify if all needed audio files are ready
def verify_speeches(misc, customers, sentences):
    pass

if __name__ == "__main__":
    # parse cmd lines
    parser = argparse.ArgumentParser()
    # main functions
    parser.add_argument('-a', action='store_true',
        help="all speeches for customer and stuff, including hidden request events, so this command equivalent to -c -d -s")
    parser.add_argument('-c', action='store_true',
        help="customer's speech")
    parser.add_argument("-d", action='store_true',
        help="hidden event speeches (asking more dinner sets)")
    parser.add_argument('-s', action='store_true',
        help="staff response speeches")

    # help functions
    parser.add_argument('-g', action='store_true',
        help="get all speaker id and save to ./speaker.ini")
    parser.add_argument('-t', action='store_true',
        help="traverse sample sentence by all speakers")
    parser.add_argument('-ms', action='store_true',
        help="misc speeches (could be any text speaked by any speaker) specified in 'misc.ini'")
    
    ## file pathes
    parser.add_argument("-o", type=str, default='./speech_audios',
        help="the path to save generated audios")
    # don't change the reset path unless necessary
    parser.add_argument("-misc", type=str, default='./Misc.ini',
        help="misc config, default is ./Misc.ini")
    parser.add_argument("-customers", type=str, default='./CustTest.ini',
        help="customer event config, default is ./CustTest.ini")
    parser.add_argument("-sentences", type=str, default='./Sentences.ini',
        help="sentence template config, default is ./Sentences.ini")
    parser.add_argument("-speakers", type=str, default='./Speakers.ini',
        help="speaker list, default is ./Speakers.ini")
    parser.add_argument("-stuff", type=str, default='./StaffRespond.ini',
        help="stuff event config, default is ./StaffRespond.ini")
    args = parser.parse_args()

    # send request and get result
    no_cmd = True
    # main functions
    if args.a:
        get_speeches(args.misc, args.customers, args.sentences, args.o)
        get_speeches_aug(args.sentences, args.o)
        get_speeches_stuff(args.stuff, args.o)
        no_cmd = False
    if args.c:
        get_speeches(args.misc, args.customers, args.sentences, args.o)
        no_cmd = False
    if args.d:
        get_speeches_aug(args.sentences, args.o)
        no_cmd = False
    if args.s:
        get_speeches_stuff(args.stuff, args.o)
        no_cmd = False

    # help functions
    if args.g:
        get_speakers(args.speakers)
        no_cmd = False
    if args.t:
        get_speeches_misc(args.speakers, args.misc, args.o, traverse = True)
        no_cmd = False
    if args.ms:
        get_speeches_misc(args.speakers, args.misc, args.o, traverse = False)
        no_cmd = False

    # if no arguments, print help menu
    if no_cmd:
        parser.print_help()
