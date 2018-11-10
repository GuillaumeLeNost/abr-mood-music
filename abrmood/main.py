""" Abbey Road Studio Hackathon

"""
import argparse
import math
import spotipy
import numpy as np

from spotipy.oauth2 import SpotifyClientCredentials
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import osc_message_builder
from pythonosc import udp_client

SPOTIPY_CLIENT_ID='869dafb8a8b64759a0886ebc473ee6cb'
SPOTIPY_CLIENT_SECRET='12b5f9739bd247e6bfedf76dfe55393f'
SPOTIPY_REDIRECT_URI='https://www.getpostman.com/oauth2/callback'

client_credentials_manager = SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# Model
current_emotions = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
target_emotions = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

# Functions ------------------------------------------------------------------------------------------------------------

def mood2emotions(mood):
    # Return weighted
    # Emotions: anger, contempt, disgust, fear, happiness, neutral, sadness, surprise
    if (mood == "party"):
        return np.array([0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    elif (mood == "energized"):
        return np.array([0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0])

def emotions2spotify(emo):
    print("emo 2 spo")



def emodistance(a,b):
    m = np.abs(np.add(a,np.negative(b)))
    sum = np.sum(m)
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
    target_emotions = mood2emotions(mood)
    print(target_emotions)

    d = emodistance(target_emotions,current_emotions)
    print("distance = {0}".format(d))

def getemotions(args):
    print("Get emotions...")
    # anger, contempt, disgust, fear, happiness, neutral, sadness, surprise
    client.send_message("/emotions/anger", current_emotions[0])
    client.send_message("/emotions/contempt", current_emotions[1])
    client.send_message("/emotions/disgust", current_emotions[2])
    client.send_message("/emotions/fear", current_emotions[3])
    client.send_message("/emotions/happiness", current_emotions[4])
    client.send_message("/emotions/neutral", current_emotions[5])
    client.send_message("/emotions/sadness", current_emotions[6])
    client.send_message("/emotions/surprise", current_emotions[7])

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

    server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()