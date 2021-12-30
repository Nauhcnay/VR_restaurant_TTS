import json
import os
import base64
import urllib.parse
import configparser
from random import choice
from aiohttp import web

'''
text and speech generation
'''
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

# let's put more template if possible
greatings = ["", "Hello! ", "Hi! "]
first_st = ["I wish to, emmmmmmmmmmm, have a ", "em, I want a ", "I'd like a ", "I will have the "]
rest_st = [" and a ", ". I also want a ", " with a ", " ", ", emmmmmmmmmmm, and the ", ". Oh, and also a "]
end_st = [". That's all, thanks", ". Thank you!", ". Thanks!"]

def to_base64():
    '''
    A helper function to read the wav file and convert it to base64
    '''
    with open("tts_output.wav", 'rb') as output:
        speech = output.read()
    speech = base64.encodebytes(speech).decode("utf-8")
    return speech

def text_to_speech(text, speaker):
    cmd = "tts --model_name \"tts_models/en/vctk/vits\" --text "
    cmd += text
    cmd += " --speaker_idx %s "%speaker
    cmd += "--use_cuda true"
    os.system(cmd)

def gen_text(request):
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

'''
HTTP server
'''
routes = web.RouteTableDef()

@routes.get("/")
async def welcome(request):
    print("log:\twe got one see our homepage!")
    return web.Response(text="The TTS server for VR restaruant is running!")

@routes.get("/get_menu")
async def welcome(request):
    with open("foods.json", 'r') as f:
        ans = json.load(f)
    return web.json_response(ans)

@routes.get("/get_speaker")
async def welcome(request):
    ans = json.dumps(list(speakers.keys()))
    return web.json_response(ans)

@routes.post("/set_menu")
async def welcome(request):
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
@routes.post("/to_speech")
async def welcome(request):
    req = await request.text()
    req = urllib.parse.unquote(req)
    print("log:\tget message %s"%req)
    req = json.loads(req)
    print("Log:\tget request %s"%str(req))
    text, speaker = gen_text(req)
    text_to_speech(text, speaker)
    # maybe don't encode it would be better
    '''
    data = to_base64()
    result = {}
    result["data"] = data
    return web.json_response(result)
    '''
    with open("tts_output.wav", 'rb') as output:
        speech = output.read()

    return web.Response(body=speech)

@routes.get("/talk")
async def welcome(request):
    return web.Response(text="under construction")

def main():
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)
    
if __name__ == '__main__':
    main()


