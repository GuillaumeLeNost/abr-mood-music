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
current_emotions = np.array([0.1, 0.5, 0.3, 0.2, 0.8, 0.1, 0.2, 0.01])
target_emotions = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
target_mask = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
target_mood = "party"

lookup = {}
with open('lookup.json') as f:
    lookup = json.load(f)


# Functions ------------------------------------------------------------------------------------------------------------
def mood2targetemotions(mood):
    # Return weighted
    target_mood = mood

    targets = lookup[target_mood]["target"]

    # Emotions: anger, contempt, disgust, fear, happiness, neutral, sadness, surprise
    for t in targets:

        if t == "anger":
            target_emotions[0] = 1.0;
        elif t == "contempt":
            target_emotions[1] = 1.0;
        elif t == "disgust":
            target_emotions[2] = 1.0;
        elif t == "fear":
            target_emotions[3] = 1.0;
        elif t == "happiness":
            target_emotions[4] = 1.0;
        elif t == "neutral":
            target_emotions[5] = 1.0;
        elif t == "sadness":
            target_emotions[6] = 1.0;
        elif t == "surprise":
            target_emotions[7] = 1.0;
        else:
            raise("unknown mood {0}".format(t))

def emotions2spotify(emo):
    print("TODO")


def fetch_faces():
    img_url = 'https://raw.githubusercontent.com/Microsoft/Cognitive-Face-Windows/master/Data/detection1.jpg'
    # img_url = 'C:\img\son.jpg'
    result = CF.face.detect(img_url, attributes='emotion')

    return result

def faces2emotions(faces):

    emotions = [0, 0, 0, 0, 0, 0, 0, 0]

    for face in faces:
        emotions_dict = face["faceAttributes"]["emotion"]
        emotions[0] = emotions_dict["anger"]
        emotions[1] = emotions_dict["contempt"]
        emotions[2] = emotions_dict["disgust"]
        emotions[3] = emotions_dict["fear"]
        emotions[4] = emotions_dict["happiness"]
        emotions[5] = emotions_dict["neutral"]
        emotions[6] = emotions_dict["sadness"]
        emotions[7] = emotions_dict["surprise"]

    print(emotions)
    return emotions


def emodistance(a,b,mask):

    mask_sum = np.sum(mask)
    a = a * mask
    b = b * mask
    delta = abs(a - b)
    sum = np.sum(delta) / mask_sum
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
    # print(target_emotions)

    d = emodistance(current_emotions,target_emotions,target_mask)

    if d > 0.1:
        emotions2spotify(target_emotions)

    print("distance = {0}".format(d))

def getemotions(args):
    client.send_message("/emotions/anger", current_emotions[0])
    client.send_message("/emotions/contempt", current_emotions[1])
    client.send_message("/emotions/disgust", current_emotions[2])
    client.send_message("/emotions/fear", current_emotions[3])
    client.send_message("/emotions/happiness", current_emotions[4])
    client.send_message("/emotions/neutral", current_emotions[5])
    client.send_message("/emotions/sadness", current_emotions[6])
    client.send_message("/emotions/surprise", current_emotions[7])

def process_faces(args):
    faces = fetch_faces()
    current_emotions = faces2emotions(faces)
    print(current_emotions)


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
