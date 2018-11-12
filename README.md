# abr-mood-music
at Abbey Road Hackathon 2018

# Audio Mirror
Sensing a crowd's mood and steering it through audio

Created by: Victoria, Leon, Guillaume and Fred. Mentored by Rosanna and Ruwen


## How to use music to change a crowd's mood?

We are organizing many workshops for our colleagues, e.g. scrum trainings incl. agile games. 

Feedback: the training is great, but the background music sucks! There are just two of us and we would prefer to focus on the training instead of looking for a good playlist. We would like a machine to take over this job for us! We need a tool which help us to change the mood of the participants using music in order to motivate the teams during agile games.

## Other use cases

* EVENT VENUES Using music we could make sure to set the crowd in the right mood according to the venue style and purpose.

* YOUTUBERS Based on the mood of the people visible in your vlog, we could automatically create the perfect soundtrack for your clip.

* REDUCE VIOLENCE Play the right music to prevent certain behaviour. e.g. underground stations.

## How we built it

* MICROSOFT FACE RECOGNITION API Using Microsoft API face recognition we can predict the mood of the crowd. We focused on happy, neutral and sad.

* UI AND LOGIC IN PYTHON / MAX MSP The user can set the targeted mood of the crowd and the genre, and decide whether they would like to use a Spotify playlist or generate music.

* SPOTIFY MUSIC METADATA We use information like energy, danceability, key, valance.

* MODULAR SYNTHESIZERS To dynamically generate soundscapes.

## Challenges we ran into

Getting the Microsoft API to work, refreshing on Python on the fly, defining smart mappings between Microsoft and Spotify APIs.
Accomplishments that we're proud of

A full working system with two different audio engines, completing our scope, and roadmap for improvements.

## What we learned

How to work as a team, how to translate mood into sonic landscapes and track selection, working with APIs

## What's next for Audio Mirror

* LEARNING MECHANISM Learning what type of music best influences the mood change.

* MULTICAMERA We could integrate multiple visual sources.

* MULTIZONE For multipurpose venues, e.g. to set different music in each zone in a venue.
