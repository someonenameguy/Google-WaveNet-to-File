#!/usr/bin/env python3
import os
import re
import sys
import ffmpeg
import multiprocessing
import requests
import base64

# speak stuff
speak_rate = 1
AudioEncoding = "OGG_OPUS"
effectsProfileId = "headphone-class-device"
pitch = 0

def synthesize_text(text, token):
  # Synthesizes speech from the input string of text.
  url = 'https://texttospeech.googleapis.com/v1beta1/text:synthesize&token=' + str(token)
  mainJson = {
      "input": {
        "text": text
      },
      "voice": {
        "languageCode": "en-US",
        "name": "en-US-Journey-O"
      },
      "audioConfig": {
        "audioEncoding": AudioEncoding,
        "pitch": pitch,
        "speakingRate": speak_rate,
        "effectsProfileId": [
          effectsProfileId
        ]
      }
    }
  
  # Note: the voice can also be specified by name.
  # Names of voices can be retrieved with client.list_voices().
  
  responseJson = requests.post(url, json = mainJson)
  
  return base64.b64decode(str(responseJson.audioContent))

def synth_text_speech(args):
    i,line = args
    audio = synthesize_text(line, token)
    write_to_file(audio, str(i))

def write_to_file(audio, name):
    # The response's audio_content is binary.
    if not os.path.exists('RAW'):
      os.makedirs('RAW')
    os.chdir('RAW')
    with open(str(name) + '.ogg', 'wb') as out:
      print('Audio content written to file', name)
      out.write(audio)
    os.chdir('..')

def concat_oggs(oggs, output):
    input_args = []
    for ogg in oggs:
      input_args.append(ffmpeg.input('RAW/'+ogg))
    ffmpeg.concat(*input_args, v=0, a=1).output(output).run()

if __name__ == '__main__':

  # get the credentials
  pwd = os.getcwd()

  # open text file as a list of lines
  textFile=input("Enter Filename: ")
  textFile = re.sub("\.te*?xt","",textFile) + ".txt"
  with open(textFile) as f:
    content = f.readlines()

  # remove whitespace characters like `\n` at the end of each line
  content = [x.strip() for x in content]

  # remove empty lines
  content = [x for x in content if len(x) > 0]
  
  # Chunks of 2500 char
  tent, length, contemp
  for x in content:
    length += len(x)
    if length > 2500:
      tent.append(contemp)
      contemp = x
      length = len(x)
    else:
      contemp += " " + x
  tent.append(contemp)
  content = contemp
  contemp, tent, length = None,None,None
  

  # enter/create an output folder
  if not os.path.exists('Outputs'):
    os.makedirs('Outputs')
  os.chdir('Outputs')
  
  # values to be used later
  oggsname=[]
  title=input("Enter Title: ")
  
  # create and move in a new folder
  if not os.path.exists(title):
    os.makedirs(title)
  os.chdir(title)
  
  # download every line of text into a numbered ogg
  for i, line in enumerate(content):
    oggsname.append(str(i) + '.ogg')
  
  global token = input("Enter Token: ")
  
  with multiprocessing.Pool() as pool:
    pool.map(synth_text_speech, enumerate(content))
    
  concat_oggs(oggsname, title+'.ogg')
  
  
