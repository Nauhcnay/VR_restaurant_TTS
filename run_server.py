import json
import os
import base64
import urllib.parse
import configparser
import copy
import shutil
import random
from multiprocessing import Process
from random import choice
from aiohttp import web

MAX_TASK = 4
TRAVERSE = False # generate all possible voices if true
'''
text and speech generation
'''
ps = []
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
# we need to pick up some speakers whoes vioce is ditinguishable
speakers_selected = ["p225", "p233", "p335", "p364"]

# let's put more template if possible
'''
greatings = ["", "Hello! ", "Hi! "]
first_st = ["I wish to, emmmmmmmmmmm, have a ", "em, I want a ", "I'd like a ", "I will have the "]
rest_st = [" and a ", ". I also want a ", " with a ", " ", ", emmmmmmmmmmm, and the ", ". Oh, and also a "]
end_st = [". That's all, thanks", ". Thank you!", ". Thanks!"]
'''
def to_base64():
    '''
    A helper function to read the wav file and convert it to base64
    '''
    with open("tts_output.wav", 'rb') as output:
        speech = output.read()
    speech = base64.encodebytes(speech).decode("utf-8")
    return speech

def text_to_speech(text, speaker, outpath):
    cmd = "tts --model_name \"tts_models/en/vctk/vits\" --text "
    cmd += "\""+text+"\""
    cmd += " --speaker_idx %s"%speaker
    cmd += " --use_cuda true"
    cmd += " --out_path " + outpath
    os.system(cmd)

def gen_text_old(request):
    # try to add more useless words to make the sentense more realistic
    order = request["order"]
    speaker = request["speaker"][0]
    with open("foods.json", 'r') as f:
        foods = json.load(f)
    st = choice(greatings) + choice(first_st)
    skip_greating = True
    for key in order:
        if skip_greating:
            st = st + foods[key]
            skip_greating = False
        else:
            st += choice(rest_st)
            st += foods[key]
            st += " "

    st += choice(end_st)
    st = "\"" + st + "\""
    return st, speaker

def order_to_text(order):
    order_real_st = []
    order_key = []
    for food in order:
        if "none" in food.lower(): continue
        order_real_st.append(food.replace("_", " "))
        order_key.append(food.lower().strip(" "))
    if len(order_real_st) > 1:
        order_real_st[-1] = "and " + order_real_st[-1]
    if len(order_real_st) > 0:
        return ", ".join(order_real_st), order_key
    else:
        return [], []
def def_text_dinnerset(speakers, sentences):
    pass

def gen_text_groups(customers, misc, sentences, gen_all=TRAVERSE):
    # return the dict of file name and text content and speaker list
    # if all is true, then generate all possible sentences
    texts = {}
    beverages = [f.lower() for f in misc["beverages"].split(",")]
    def sample_st_key(iidx):
        st_keys = list(sentences[incident_key[iidx]].keys())
        try:
            st_keys.remove("s00")
        except:
            # do nothing
            pass
        st_key = random.sample(st_keys, 1)[0]
        return st_key

    for c_key in customers:
        if c_key == "speakers": continue
        incident_key = list(sentences.keys())
        incident_key.sort()
        speaker = customers[c_key]["speaker"]
        incidents = customers[c_key]["incidents"]
        order_st, order = order_to_text(customers[c_key]["meal_order"])
        extra_order_st, extra_order = order_to_text(customers[c_key]["extra_order"])
        _, replace_order = order_to_text(customers[c_key]["replace_order"])
        # ReadyToOrder
        if "1" in incidents and gen_all == False:
            greeting = sentences[incident_key[0]].get("s00", "")
            st_key = sample_st_key(0)
            # generate greeting
            name = c_key + incident_key[0] + "s00" + ".wav"
            texts[name] = [greeting, speaker]
            # generate sentence
            name = c_key + incident_key[0] + ".wav"
            texts[name] = [sentences[incident_key[0]][st_key].replace("_", order_st), speaker]
        elif gen_all:
            for st_key in sentences[incident_key[0]]:
                if st_key == "s00": continue
                greeting = sentences[incident_key[0]].get("s00", "")
                name = c_key + incident_key[0] + st_key + ".wav"
                texts[name] = [greeting + ' ' + sentences[incident_key[0]][st_key].replace("_", order_st), speaker]

        # WantFoodIncident
        if "2" in incidents and gen_all == False:
            greeting = sentences[incident_key[1]].get("s00", "")
            st_key = sample_st_key(1)
            # generate greeting
            name = c_key + incident_key[1] + "s00" + ".wav"
            texts[name] = [greeting, speaker]
            for food_key in order:
                name = c_key + incident_key[1] + food_key + ".wav"
                texts[name] = [sentences[incident_key[1]][st_key].replace("_", food_key.replace("_", " ")), speaker]   
        elif gen_all:
            greeting = sentences[incident_key[1]].get("s00", "")
            for st_key in sentences[incident_key[1]]:
                if st_key == "s00": continue
                for food_key in order:
                    name = c_key + incident_key[1] + st_key + food_key + ".wav"
                    texts[name] = [greeting + ' ' + sentences[incident_key[1]][st_key].replace("_", order[food_key]), speaker]

        # CheckOutIncident
        if "3" in incidents and gen_all == False:
            st_key = sample_st_key(2)
            # generate greeting
            name = c_key + incident_key[2] + "s00" + ".wav"
            texts[name] = [greeting, speaker]
            # generate sentence
            name = c_key + incident_key[2] + ".wav"
            texts[name] = [sentences[incident_key[2]][st_key], speaker]
        elif gen_all:
            for st_key in sentences[incident_key[2]]:
                name = c_key + incident_key[2] + st_key + ".wav"
                texts[name] = [sentences[incident_key[2]][st_key], speaker]

        # CreditCardIncident
        if "4" in incidents and gen_all == False:
            st_key = sample_st_key(3)
            name = c_key + incident_key[3] + ".wav"
            texts[name] = [sentences[incident_key[3]][st_key], speaker]
        elif gen_all:
            for st_key in sentences[incident_key[3]]:
                name = c_key + incident_key[3] + st_key + ".wav"
                texts[name] = [sentences[incident_key[3]][st_key], speaker]

        # OrderMoreIncident
        if "5" in incidents and gen_all == False:
            st_key = sample_st_key(4)
            # generate greeting
            greeting = sentences[incident_key[4]].get("s00", "")
            name = c_key + incident_key[4] + "s00" + ".wav"
            texts[name] = [greeting, speaker]
            # generate sentence
            name = c_key + incident_key[4] + ".wav"
            texts[name] = [sentences[incident_key[4]][st_key].replace("_", extra_order_st), speaker]
        elif gen_all:
            greeting = sentences[incident_key[4]].get("s00", "")
            for st_key in sentences[incident_key[4]]:
                if st_key == "s00": continue
                name = c_key + incident_key[4] + st_key + ".wav"
                texts[name] = [greeting + ' ' + sentences[incident_key[4]][st_key].replace("_", extra_order_st), speaker]

        # DropDrinkIncident
        if "6" in incidents and gen_all == False:
            st_key = sample_st_key(5)
            for food_key in order:
                if food_key not in beverages: continue
                name = c_key + incident_key[5] + food_key + ".wav"
                texts[name] = [sentences[incident_key[5]][st_key].replace("_", food_key.replace("_", " ")), speaker]       
        elif gen_all:
            for st_key in sentences[incident_key[5]]:
                for food_key in order:
                    if food_key not in beverages: continue
                    name = c_key + incident_key[5] + st_key + food_key + ".wav"
                    texts[name] = [sentences[incident_key[5]][st_key].replace("_", food_key.replace("_", " ")), speaker]

        # FoodReplacementIncident
        if "7" in incidents and gen_all == False:
            st_key = sample_st_key(6)
            for food_key in order:
                if food_key in beverages: continue
                name = c_key + incident_key[6] + food_key + ".wav"
                texts[name] = [sentences[incident_key[6]][st_key].replace("_", food_key.replace("_", " ")), speaker]       
        elif gen_all:
            for st_key in sentences[incident_key[6]]:
                for food_key in order:
                    if food_key in beverages: continue
                    name = c_key + incident_key[6] + st_key + food_key + ".wav"
                    texts[name] = [sentences[incident_key[6]][st_key].replace("_", food_key.replace("_", " ")), speaker]
    return texts

def read_customer(customers_text):
    # return customer list, order list, extra order list, replace order list, incident list
    customers_ini = configparser.ConfigParser()
    customers_ini.read_string(customers_text)
    customers = {}
    
    # for each group random assign a unique speaker ID
    spk_idx = []
    group_nums = int(remove_comment(customers_ini["General"]["totCustGroup"]))
    for _ in range(group_nums):
        if TRAVERSE:
            spk_idx.append(random.sample(speakers_selected, len(speakers_selected)))
        else:
            assert len(speakers_selected) >= 4
            spk_idx.append(speakers_selected[0:4])
    
    customers["speakers"] = speakers_selected[0:4]
    # read and format customer info
    for sec in customers_ini:
        sec_keys = list(customers_ini[sec].keys())
        if sec.lower() == "default": continue
        if "-Customer" in sec:
            g, c = sec.split("-")
            g_idx = int(g.strip("Group")) # group index
            if g_idx + 1 > group_nums: continue # skip the rest groups
            c_idx = int(c.strip("Customer")) -1 # customer index
            g = "g%d"%g_idx
            c = "c%d"%(c_idx + 1)
            name = g + c
            customers[name] = {}
            # we need to assign a speaker to each customer
            customers[name]["speaker"] = spk_idx[g_idx][c_idx]
            customers[name]["meal_order"] = remove_comment(customers_ini[sec]["mealorder"]).split(",") if "mealorder" in sec_keys else []
            customers[name]["extra_order"] = remove_comment(customers_ini[sec]["extraorder"]).split(",") if "extraorder" in sec_keys else []
            customers[name]["replace_order"] = remove_comment(customers_ini[sec]["replaceorder"]).split(",") if "replaceorder" in sec_keys else []
            customers[name]["incidents"] = remove_comment(customers_ini[sec]["Incidentorder"]).split(",") if "incidentorder" in sec_keys else []
    return customers

def remove_comment(value):
    return value.split(";")[0]

def read_sentences(sentences_text):
    # return sentence template list per incidents
    sentences_ini = configparser.ConfigParser()
    sentences_ini.read_string(sentences_text)
    st_template = {}
    idx = 1
    for sec in sentences_ini:
        if sec.lower() == "default": continue
        name = "i%d"%idx
        idx += 1
        st_template[name] = {}
        for st_key in sentences_ini[sec].keys():
            st_template[name][st_key] = \
            remove_comment(sentences_ini[sec][st_key])
    return st_template        

def read_misc(misc_text):
    # returns the dict mapping from key to food name
    misc_ini = configparser.ConfigParser()
    misc_ini.read_string(misc_text)
    misc = {}
    for sec in misc_ini:
        if sec.lower() == "default": continue
        for key in misc_ini[sec]:
            misc[key] = remove_comment(misc_ini[sec][key].lower())
    return misc
'''
HTTP server
'''
routes = web.RouteTableDef()

@routes.get("/")
async def welcome(request):
    print("log:\twe got one see our homepage!")
    return web.Response(text="The TTS server for VR restaruant is running!")

@routes.get("/get_menu")
async def get_menu(request):
    with open("foods.json", 'r') as f:
        ans = json.load(f)
    return web.json_response(ans)

@routes.get("/get_speaker")
async def get_speaker(request):
    ans = json.dumps(list(speakers.keys()))
    return web.json_response(ans)

@routes.post("/set_menu")
async def set_menu(request):
    req = await request.json()
    req = json.loads(req)
    print("log:\tget new menu \n%s:"%str(req))
    with open("foods.json", 'w') as f:
        json.dump(req, f)

# a example of incoming request:
'''
{
    "order": ["00", "10", "20", "30"],
    "speaker": "p225"
}
'''
'''
@routes.post("/to_speech")
async def welcome(request):
    req = await request.text()
    req = urllib.parse.unquote(req)
    print("log:\tget message %s"%req)
    req = json.loads(req)
    print("Log:\tget request %s"%str(req))
    text, speaker = gen_text_old(req)
    text_to_speech(text, speaker)
    # maybe don't encode it would be better
    # data = to_base64()
    # result = {}
    # result["data"] = data
    # return web.json_response(result)
    with open("tts_output.wav", 'rb') as output:
        speech = output.read()

    return web.Response(body=speech)
'''

@routes.post("/to_speech")
async def to_speech(request):
    req = await request.json()
    if len(ps) <= MAX_TASK:
        sentences = read_sentences(req["sentences"])
        misc = read_misc(req["misc"])
        customers = read_customer(req["customers"])
        texts = gen_text_groups(customers, misc, sentences)
        # create a non-block sub-process to generate audioes
        p = create_job(to_speech_multi_proc, texts)
        ps.append(p)
        return web.Response(text="processing with pid %s"%str(p.pid))
    else:
        return web.Response(status=404, text="server busy, please try again later")

@routes.post("/to_speech_aug")
async def to_speech_aug(request):
    req = await request.json()
    if len(ps) <= MAX_TASK:
        sentences = read_sentences(req["sentences"])
        texts = {}
        for i in range(1,5):
            c_key = "c%d"%i
            i8 = "i8"
            i9 = "i9"
            # random pickup one sentence
            st_keys = list(sentences[i8].keys())
            st_key = random.sample(st_keys, 1)[0]
            for item_key in sentences[i9]:
                food_key = sentences[i9][item_key].lower()
                name = c_key+i8+food_key+".wav"
                st = sentences[i8][st_key].replace("_", food_key.replace("_", " "))
                texts[name] = [st, speakers_selected[i-1]]
        # create a non-block sub-process to generate audioes
        p = create_job(to_speech_multi_proc, texts)
        ps.append(p)
        return web.Response(text="processing with pid %s"%str(p.pid))
    else:
        return web.Response(status=404, text="server busy, please try again later")

@routes.get("/talk")
async def talk(request):
    return web.Response(text="under construction")

# need fix later
@routes.post("/is_ready")
async def is_ready(request):
    pid = await request.text()
    target_file = "./audio_output_%s.zip"%(str(pid))
    if os.path.exists(target_file):
        print("log:\tsend files to client")
        with open(target_file, "rb") as f:
            audios = f.read()
        # clean up
        os.remove(target_file)
        ps.pop()
        return web.Response(status=200, body=audios)
    else:
        if os.path.exists("progress_%s.txt"%str(pid)):
            with open("progress_%s.txt"%str(pid), "r") as f:
                progress = f.read()
            return web.Response(status=404, text="%s"%progress)
        else:
            return web.Response(status=404, text="task is not found")

def to_speech_multi_proc(texts):
    text_count = 1
    text_total = len(texts)
    pid = str(os.getpid())
    for file_name in texts: 
        text, speaker = texts[file_name]
        file_path = "./audio_output_%s/"%pid
        if os.path.exists(file_path) == False:
            os.mkdir(file_path)
        text_to_speech(text, speaker, os.path.join(file_path, file_name))
        
        # record the progress
        with open("progress_%s.txt"%str(pid), "w") as f:
            f.write("%.2f"%(text_count /  text_total * 100))
        text_count += 1

    shutil.make_archive("./audio_output_%s"%(str(pid)), 'zip', "./audio_output_%s"%(str(pid)))
    
    # clean up
    os.remove("progress_%s.txt"%str(pid))
    shutil.rmtree("./audio_output_%s"%(str(pid)))

def create_job(target, *args):
    p = Process(target=target, args=args)
    p.start()
    return p

def main():
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)
    
if __name__ == '__main__':
    main()


