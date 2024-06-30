#!/usr/bin/env python3
import os
import re
import sys
import ffmpeg
import string
import multiprocessing

# speak stuff
speak_rate = 1.3


def synthesize_text(text, client):
  """Synthesizes speech from the input string of text."""

  # input format
  input_text = texttospeech.SynthesisInput(text=text)

  # Note: the voice can also be specified by name.
  # Names of voices can be retrieved with client.list_voices().
  voice = texttospeech.VoiceSelectionParams(
    language_code='en-GB',
    name='en-GB-Neural2-B')

  audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.OGG_OPUS,
    speaking_rate=speak_rate)

  response = client.synthesize_speech(
    request={"input": input_text, "voice": voice, "audio_config": audio_config})

  return response.audio_content

def synth_text_speech(args):
    i,line = args
    client = texttospeech.TextToSpeechClient()
    audio = synthesize_text(line, client)
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

def trim_to_nearest_punctuation(input_str):
    # Set of punctuation marks
    punctuation_set = set(string.punctuation)
    if len(input_str.split()) < 20:
        return input_str
    # Iterate through the characters to find the nearest punctuation
    for i, char in enumerate(input_str):
        if char in punctuation_set:
            return input_str[:i]

    # If no punctuation is found, return the original string
    return input_str

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
  
  with multiprocessing.Pool() as pool:
    pool.map(synth_text_speech, enumerate(content))
    
  concat_oggs(oggsname, title+'.ogg')
  
  
