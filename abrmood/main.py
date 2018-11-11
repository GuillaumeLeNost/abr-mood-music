""" Abbey Road Studio Hackathon
"""
import argparse
import math
import spotipy
import json
import requests
import random
import numpy as np
import cognitive_face as CF

from enum import Enum

from spotipy.oauth2 import SpotifyClientCredentials
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

# CONSTANTS
SPOTIPY_CLIENT_ID='b509b7869aa74a86975f5ce05f811513'
SPOTIPY_CLIENT_SECRET='cf40126280e542329081f89c616af220'
SPOTIPY_REDIRECT_URI='https://www.getpostman.com/oauth2/callback'
MICROSOFT_KEY = '73a3cd9b370c4744b57d11e25c14ffee'  # Replace with a valid Subscription Key here.
BASE_URL = 'https://uksouth.api.cognitive.microsoft.com/face/v1.0'  # Replace with your regional Base URL

# Initialise credentials
CF.Key.set(MICROSOFT_KEY)
CF.BaseUrl.set(BASE_URL)

client_credentials_manager = SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
user_token = 'BQDdWh2GTlDAH5_PRoIJ6G9FJUcvsr3hLCT9UUf0GvjZbmZhQjDmmi6RuGLmhaoa7t7oFPnYEYy6uRregGXlLhOfEin8ybYa8_iJoCgmVILxsMBDLT8ZhofXZhFwma1r79ccCdDw8HRIcG6PKypELTmimafm_IAEbbD2m1dh1OjgkzVzrdFTdhPSrq7yphVSmpvuVJzoWy_gGXDr5QLjmY1baARyaHjVKOhp363lqYG2R1IAv7oHAXvsm_cMrGDPAXKvcZCgYaWmZVKVmQ'
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, auth=user_token)

# Model
# anger, contempt, disgust, fear, happiness, neutral, sadness, surprise
current_emotions = {"anger": 0.0, "contempt": 0.0, "disgust": 0.0, "fear": 0.0, "happiness": 1.0, "neutral": 0.0, "sadness": 0.0, "surprise": 0.0}
target_emotions = {"anger": 0.0, "contempt": 0.0, "disgust": 0.0, "fear": 0.0, "happiness": 0.0, "neutral": 0.0, "sadness": 0.0, "surprise": 0.0}
target_mask = {"happiness"}
target_mood = "party"

lookup = {}
with open('lookup.json') as f:
    lookup = json.load(f)


# Functions ------------------------------------------------------------------------------------------------------------
def mood2targetemotions(mood):
    # Return weighted
    target_mood = mood

    try:
        target_mask = lookup[target_mood]["target"]
        print(target_mask)
    except:
        print("Mood could not be found")

    # re-init target_emotions
    for emo in target_emotions:
        emo = 0.0

    for prop in target_mask:
        target_emotions[prop] = 1.0

    print(target_emotions)
    print(target_mask)


def mood2spotify(mood):
    print("Requesting tracks for mood{0}".format(mood))
    audio_features = getRecommendationsFromMood(mood)
    print(audio_features)

    next_audio = audio_features[random.randint(0, len(audio_features))]['uri']
    playSong(next_audio, user_token)






def fetch_faces():
    # img_url = 'https://raw.githubusercontent.com/Microsoft/Cognitive-Face-Windows/master/Data/detection1.jpg'
    img_url = 'C:\\dev\\Repositories\\abr-mood-music\\abrmood\\img\\frame.jpg'
    # img_url = 'C:\img\son.jpg'
    result = CF.face.detect(img_url, attributes='emotion')
    return result

def faces2emotions(faces):

    emotions = {}

    # TODO: only take into account last fast (!)
    for face in faces:
        emotions = face["faceAttributes"]["emotion"]

    return emotions


def emodistance(c, t, mask):

    mask_sum = len(mask)

    if len(c) < 1:
        return 1.0

    if len(t) < 1:
        return 1.0

    sum = 0

    for prop in mask:
        sum = sum + abs(t[prop] - c[prop])

    sum = sum / mask_sum

    return sum

# Emotions to Spotify --------------------------------------------------------------------------------------------------
def openJson(json_file):
    with open(json_file) as f:
        data = json.load(f)
    return(data)

def getRecommendations(**kwargs):

    recom_tracks = sp.recommendations(limit=100, **kwargs)['tracks']
    result=[]
    for track in recom_tracks:
        result.append(track['id'])
    return result

def getAudioFeatures(track_ids):
    audio_features=sp.audio_features(tracks=track_ids)
    return audio_features

def playSong(uri, token):
    url='https://api.spotify.com/v1/me/player/play'
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+token}
    data='{\"uris\":["'+uri+'"]}'
    response = requests.put(url, data, headers=headers)

def getRecommendationsFromMood(mood):
    mood = "party"
    data = openJson("lookup.json")
    recommendations=getRecommendations(**data[mood])
    audio_features = getAudioFeatures(recommendations)
    return(audio_features)

# OSC handlers ---------------------------------------------------------------------------------------------------------
def moodtarget(args,mood):
    print("Set mood target to: {0}".format(mood))
    mood2targetemotions(mood)


def getemotions(args):
    print("GET emotions")
    client.send_message("/emotions/anger", current_emotions["anger"])
    client.send_message("/emotions/contempt", current_emotions["contempt"])
    client.send_message("/emotions/disgust", current_emotions["disgust"])
    client.send_message("/emotions/fear", current_emotions["fear"])
    client.send_message("/emotions/happiness", current_emotions["happiness"])
    client.send_message("/emotions/neutral", current_emotions["neutral"])
    client.send_message("/emotions/sadness", current_emotions["sadness"])
    client.send_message("/emotions/surprise", current_emotions["surprise"])


def process_faces(args):
    faces = fetch_faces()
    current_emotions = faces2emotions(faces)

    print(current_emotions)

    client.send_message("/emotions/anger", current_emotions["anger"])
    client.send_message("/emotions/contempt", current_emotions["contempt"])
    client.send_message("/emotions/disgust", current_emotions["disgust"])
    client.send_message("/emotions/fear", current_emotions["fear"])
    client.send_message("/emotions/happiness", current_emotions["happiness"])
    client.send_message("/emotions/neutral", current_emotions["neutral"])
    client.send_message("/emotions/sadness", current_emotions["sadness"])
    client.send_message("/emotions/surprise", current_emotions["surprise"])


    # Update distance
    d = emodistance(current_emotions, target_emotions, target_mask)

    if d > 0.1:
        mood2spotify(target_emotions)

    print("distance = {0}".format(d))



# MAIN==================================================================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port",
                        type=int, default=8888, help="The port to listen on")
    args = parser.parse_args()

    #track_ids = getRecommendations(['jazz'], 1)
    #audio_features = getAudioFeatures(track_ids)
    #print(audio_features)

    # Set up OSC client
    client = udp_client.SimpleUDPClient("127.0.0.1", 9001)
    # client2 = udp_client.SimpleUDPClient("10.11.2.47", 1337)


    # Set up OSC server
    # /moodtarget happy, energized, chill, party, sad
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/moodtarget", moodtarget)
    dispatcher.map("/getemotions", getemotions)
    dispatcher.map("/faces", process_faces)


    server = osc_server.BlockingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
