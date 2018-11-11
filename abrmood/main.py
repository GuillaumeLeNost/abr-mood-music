""" Abbey Road Studio Hackathon
"""
import argparse
import math
import spotipy
import json
import numpy as np
import cognitive_face as CF

from enum import Enum

from spotipy.oauth2 import SpotifyClientCredentials
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

# CONSTANTS
SPOTIPY_CLIENT_ID='869dafb8a8b64759a0886ebc473ee6cb'
SPOTIPY_CLIENT_SECRET='12b5f9739bd247e6bfedf76dfe55393f'
SPOTIPY_REDIRECT_URI='https://www.getpostman.com/oauth2/callback'
MICROSOFT_KEY = '73a3cd9b370c4744b57d11e25c14ffee'  # Replace with a valid Subscription Key here.
BASE_URL = 'https://uksouth.api.cognitive.microsoft.com/face/v1.0'  # Replace with your regional Base URL

# Initialise credentials
CF.Key.set(MICROSOFT_KEY)
CF.BaseUrl.set(BASE_URL)

client_credentials_manager = SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Model
# anger, contempt, disgust, fear, happiness, neutral, sadness, surprise
current_emotions = {"anger": 0.0, "contempt": 0.0, "disgust": 0.0, "fear": 0.0, "happiness": 0.0, "neutral": 0.0, "sadness": 0.0, "surprise": 0.0}
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

    target_mask = lookup[target_mood]["target"]
    print(target_mask)

    # re-init target_emotions
    for emo in target_emotions:
        emo = 0.0

    for prop in target_mask:
        target_emotions[prop] = 1.0

    print(target_emotions)
    print(target_mask)


def emotions2spotify(emo):
    print("TODO")

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

    sum = 0

    for prop in mask:
        sum = sum + abs(t[prop] - c[prop])

    sum = sum / mask_sum

    return sum


def getRecommendations(seed_genre, happiness):
   recom_tracks = sp.recommendations(seed_genres=seed_genre,target_valence=happiness)['tracks']
   result=[]
   for track in recom_tracks:
       result.append(track['id'])
   return result


def getAudioFeatures(track_ids):
   audio_features=sp.audio_features(tracks=track_ids)
   return audio_features

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

    client2.send_message("/emotions/anger", current_emotions["anger"])
    client2.send_message("/emotions/contempt", current_emotions["contempt"])
    client2.send_message("/emotions/disgust", current_emotions["disgust"])
    client2.send_message("/emotions/fear", current_emotions["fear"])
    client2.send_message("/emotions/happiness", current_emotions["happiness"])
    client2.send_message("/emotions/neutral", current_emotions["neutral"])
    client2.send_message("/emotions/sadness", current_emotions["sadness"])
    client2.send_message("/emotions/surprise", current_emotions["surprise"])


def process_faces(args):
    faces = fetch_faces()
    current_emotions = faces2emotions(faces)

    print(current_emotions)


    # update distance
    d = emodistance(current_emotions, target_emotions, target_mask)

    if d > 0.1:
        emotions2spotify(target_emotions)

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
    client2 = udp_client.SimpleUDPClient("10.11.2.47", 1337)


    # Set up OSC server
    # /moodtarget happy, energized, chill, party, sad
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/moodtarget", moodtarget)
    dispatcher.map("/getemotions", getemotions)
    dispatcher.map("/faces", process_faces)

    server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
