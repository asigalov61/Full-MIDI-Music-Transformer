# -*- coding: utf-8 -*-
"""Full_MIDI_Music_Transformer_Training_Dataset_Maker.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/asigalov61/Full-MIDI-Music-Transformer/blob/main/Training-Data/Full_MIDI_Music_Transformer_Training_Dataset_Maker.ipynb

# Full MIDI Music Transformer Training Dataset Maker (ver. 1.0)

***

Powered by tegridy-tools: https://github.com/asigalov61/tegridy-tools

***

#### Project Los Angeles

#### Tegridy Code 2023

***

# (SETUP ENVIRONMENT)
"""

#@title Install all dependencies (run only once per session)

!git clone https://github.com/asigalov61/tegridy-tools
!pip install tqdm

#@title Import all needed modules

print('Loading needed modules. Please wait...')
import os

import math
import statistics
import random

from tqdm import tqdm

if not os.path.exists('/content/Dataset'):
    os.makedirs('/content/Dataset')

print('Loading TMIDIX module...')
os.chdir('/content/tegridy-tools/tegridy-tools')

import TMIDIX

print('Done!')

os.chdir('/content/')
print('Enjoy! :)')

"""# (DOWNLOAD SOURCE MIDI DATASET)"""

# Commented out IPython magic to ensure Python compatibility.
#@title Download original LAKH MIDI Dataset

# %cd /content/Dataset/

!wget 'http://hog.ee.columbia.edu/craffel/lmd/lmd_full.tar.gz'
!tar -xvf 'lmd_full.tar.gz'
!rm 'lmd_full.tar.gz'

# %cd /content/

#@title Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

"""# (FILE LIST)"""

#@title Save file list
###########

print('Loading MIDI files...')
print('This may take a while on a large dataset in particular.')

dataset_addr = "/content/Dataset"
# os.chdir(dataset_addr)
filez = list()
for (dirpath, dirnames, filenames) in os.walk(dataset_addr):
    filez += [os.path.join(dirpath, file) for file in filenames]
print('=' * 70)

if filez == []:
    print('Could not find any MIDI files. Please check Dataset dir...')
    print('=' * 70)

print('Randomizing file list...')
random.shuffle(filez)

TMIDIX.Tegridy_Any_Pickle_File_Writer(filez, '/content/drive/MyDrive/filez')

#@title Load file list
filez = TMIDIX.Tegridy_Any_Pickle_File_Reader('/content/drive/MyDrive/filez')

"""# (PROCESS)"""

#@title Process MIDIs with TMIDIX MIDI processor

print('=' * 70)
print('TMIDIX MIDI Processor')
print('=' * 70)
print('Starting up...')
print('=' * 70)

###########

START_FILE_NUMBER = 0
LAST_SAVED_BATCH_COUNT = 0

input_files_count = START_FILE_NUMBER
files_count = LAST_SAVED_BATCH_COUNT

melody_chords_f = []

stats = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

print('Processing MIDI files. Please wait...')
print('=' * 70)

for f in tqdm(filez[START_FILE_NUMBER:]):
    try:

      input_files_count += 1

      fn = os.path.basename(f)

      # Filtering out giant MIDIs
      file_size = os.path.getsize(f)

      if file_size < 250000:

        #=======================================================
        # START PROCESSING

        # Convering MIDI to ms score with MIDI.py module
        score = TMIDIX.midi2ms_score(open(f, 'rb').read())

        # INSTRUMENTS CONVERSION CYCLE
        events_matrix = []
        itrack = 1

        events_types = ['note',
                        'patch_change',
                        'control_change',
                        'key_after_touch',
                        'channel_after_touch',
                        'pitch_wheel_change']

        while itrack < len(score):
            for event in score[itrack]:
                if event[0] in events_types:
                    events_matrix.append(event)
            itrack += 1

        events_matrix.sort(key = lambda x: x[1])

        if len(events_matrix) > 0:
            if min([e[1] for e in events_matrix]) >= 0 and min([e[2] for e in events_matrix if e[0] == 'note']) >= 0:

                #=======================================================
                # PRE-PROCESSING

                # recalculating timings
                for e in events_matrix:
                    e[1] = int(e[1] / 16) # Max 2 seconds for start-times
                    if e[0] == 'note':
                        e[2] = int(e[2] / 32) # Max 4 seconds for durations

                #=======================================================
                # FINAL PRE-PROCESSING

                melody_chords = []

                pe = events_matrix[0]

                for e in events_matrix:

                    if e[0] == 'note':

                        # Cliping all values...
                        time = max(0, min(127, e[1]-pe[1]))
                        dur = max(1, min(127, e[2]))
                        cha = max(0, min(15, e[3]))
                        ptc = max(1, min(127, e[4]))
                        vel = max(1, min(127, e[5]))

                        # Writing final note
                        melody_chords.append(['note', time, dur, cha, ptc, vel])

                    if e[0] == 'patch_change':

                        # Cliping all values...
                        time = max(0, min(127, e[1]-pe[1]))
                        cha = max(0, min(15, e[2]))
                        ptc = max(0, min(127, e[3]))

                        melody_chords.append(['patch_change', time, cha, ptc])

                    if e[0] == 'control_change':

                        # Cliping all values...
                        time = max(0, min(127, e[1]-pe[1]))
                        cha = max(0, min(15, e[2]))
                        con = max(0, min(127, e[3]))
                        cval = max(0, min(127, e[4]))

                        melody_chords.append(['control_change', time, cha, con, cval])

                    if e[0] == 'key_after_touch':

                        # Cliping all values...
                        time = max(0, min(127, e[1]-pe[1]))
                        cha = max(0, min(15, e[2]))
                        ptc = max(1, min(127, e[3]))
                        vel = max(1, min(127, e[4]))

                        melody_chords.append(['key_after_touch', time, cha, ptc, vel])

                    if e[0] == 'channel_after_touch':

                        # Cliping all values...
                        time = max(0, min(127, e[1]-pe[1]))
                        cha = max(0, min(15, e[2]))
                        vel = max(1, min(127, e[3]))

                        melody_chords.append(['channel_after_touch', time, cha, vel])

                    if e[0] == 'pitch_wheel_change':

                        # Cliping all values...
                        time = max(0, min(127, e[1]-pe[1]))
                        cha = max(0, min(15, e[2]))
                        wheel = max(-8192, min(8192, e[3])) // 128

                        melody_chords.append(['pitch_wheel_change', time, cha, wheel])

                    pe = e


                #=======================================================

                # Adding SOS/EOS, intro and counters

                if len(melody_chords) < (127 * 100) and ((events_matrix[-1][1] * 16) < (8 * 60 * 1000)): # max 12700 MIDI events and max 8 min per composition

                    melody_chords1 = [['start', 0, 0, 0, 0, 0]]

                    events_block_counter = 0
                    time_counter = 0

                    for i in range(len(melody_chords)):
                        melody_chords1.append(melody_chords[i])

                        time_counter += melody_chords[i][1]

                        if i != 0 and (len(melody_chords) - i == 100):
                            melody_chords1.append(['outro', 0, 0, 0, 0, 0])

                        if i != 0 and (i % 100 == 0) and (len(melody_chords) - i >= 100):
                            melody_chords1.append(['counters_seq', ((time_counter * 16) // 3968), events_block_counter, 0, 0, 0])
                            events_block_counter += 1

                    melody_chords1.append(['end', 0, 0, 0, 0, 0])

                    #=======================================================

                    melody_chords2 = []

                    for m in melody_chords1:

                        if m[0] == 'note':

                            if m[3] == 9:
                                ptc = m[4] + 128
                            else:
                                ptc = m[4]

                            # Writing final note
                            melody_chords2.extend([m[3], m[1]+16, m[2]+16+128, ptc+16+128+128, m[5]+16+128+128+256])

                        # Total tokens so far 656

                        if m[0] == 'patch_change': # 656

                            melody_chords2.extend([1425, m[1]+16, m[2], m[3]+16+128+128+256+128, 1424])

                        # Total tokens so far 784

                        if m[0] == 'control_change': # 784

                            melody_chords2.extend([1426, m[1]+16, m[2], m[3]+16+128+128+256+128+128, m[4]+16+128+128+256+128+128+128])

                        # Total tokens so far 1040

                        if m[0] == 'key_after_touch': # 1040

                            if m[2] == 9:
                                ptc = m[3] + 128
                            else:
                                ptc = m[3]

                            melody_chords2.extend([1427, m[1]+16, m[2], ptc+16+128+128, m[4]+16+128+128+256])

                        # Total tokens so far 1040

                        if m[0] == 'channel_after_touch': # 1040

                            melody_chords2.extend([1428, m[1]+16, m[2], m[3]+16+128+128+256, 1424])

                        # Total tokens so far 1040

                        if m[0] == 'pitch_wheel_change': # 1040

                            melody_chords2.extend([1429, m[1]+16, m[2], m[3]+16+128+128+256+128+128+128+128, 1424])

                        # Total tokens so far 1168

                        if m[0] == 'counters_seq': # 1168

                            melody_chords2.extend([1430, m[1]+16+128+128+256+128+128+128+128+128, m[2]+16+128+128+256+128+128+128+128+128+128, 1424, 1424])

                        # Total tokens so far: 1424

                        #=======================================================

                        # 1424 - pad token

                        # 1425 - patch change token
                        # 1426 - control change token
                        # 1427 - key after touch token
                        # 1428 - channel after touch token
                        # 1429 - pitch wheel change token
                        # 1430 - counters seq token

                        # 1431 - outro token
                        # 1432 - end token
                        # 1433 - start token

                        if m[0] == 'outro':
                            melody_chords2.extend([1431, 1431, 1431, 1431, 1431])

                        if m[0] == 'end':
                            melody_chords2.extend([1432, 1432, 1432, 1432, 1432])

                        if m[0] == 'start':
                            melody_chords2.extend([1433, 1433, 1433, 1433, 1433])

                    #=======================================================

                    # FINAL TOTAL TOKENS: 1433

                    #=======================================================

                    melody_chords_f.append(melody_chords2)

                    #=======================================================

                    # Processed files counter
                    files_count += 1

                    # Saving every 5000 processed files
                    if files_count % 5000 == 0:
                      print('SAVING !!!')
                      print('=' * 70)
                      print('Saving processed files...')
                      print('=' * 70)
                      print('Processed so far:', files_count, 'out of', input_files_count, '===', files_count / input_files_count, 'good files ratio')
                      print('=' * 70)
                      count = str(files_count)
                      TMIDIX.Tegridy_Any_Pickle_File_Writer(melody_chords_f, '/content/drive/MyDrive/LAKH_INTs_'+count)
                      melody_chords_f = []
                      print('=' * 70)

    except KeyboardInterrupt:
        print('Saving current progress and quitting...')
        break

    except Exception as ex:
        print('WARNING !!!')
        print('=' * 70)
        print('Bad MIDI:', f)
        print('Error detected:', ex)
        print('=' * 70)
        continue

# Saving last processed files...
print('SAVING !!!')
print('=' * 70)
print('Saving processed files...')
print('=' * 70)
print('Processed so far:', files_count, 'out of', input_files_count, '===', files_count / input_files_count, 'good files ratio')
print('=' * 70)
count = str(files_count)
TMIDIX.Tegridy_Any_Pickle_File_Writer(melody_chords_f, '/content/drive/MyDrive/LAKH_INTs_'+count)

# Displaying resulting processing stats...
print('=' * 70)
print('Done!')
print('=' * 70)

print('Resulting Stats:')
print('=' * 70)
print('Total good processed MIDI files:', files_count)
print('=' * 70)

"""# (TEST INTS)"""

#@title Test INTs

train_data1 = random.choice(melody_chords_f)

print('Sample INTs', train_data1[:15])

out = train_data1[:200000]

if len(out) != 0:

    song = out
    song_f = []
    time = 0
    dur = 0
    vel = 90
    pitch = 0
    channel = 0

    son = []
    song1 = []
    for s in song: # creating penta seqs...

        if s > 15 and s < 1425:

            son.append(s)
        else:
            if len(son) == 5:
                song1.append(son)
                son = []
            son.append(s)

    for s in song1: # decoding...

        if s[0] < 16: # Note

            channel = s[0]
            time += (s[1]-16) * 16
            dur = (s[2]-16-128) * 32
            pitch = (s[3]-16-128-128) % 128
            vel = (s[4]-16-128-128-256)

            song_f.append(['note', time, dur, channel, pitch, vel])

        if s[0] == 1425: # patch change

            time += (s[1]-16) * 16
            channel = s[2]
            patch = (s[3]-(16+128+128+256+128))

            song_f.append(['patch_change', time, channel, patch])

        if s[0] == 1426: # control change

            time += (s[1]-16) * 16
            channel = s[2]
            controller = (s[3]-(16+128+128+256+128+128))
            controller_value = (s[4]-(16+128+128+256+128+128+128))

            song_f.append(['control_change', time, channel, controller, controller_value])

        if s[0] == 1427: # key after touch

            time += (s[1]-16) * 16
            channel = s[2]
            pitch = (s[3]-16-128-128) % 128
            vel = (s[4]-16-128-128-256)

            song_f.append(['key_after_touch', time, channel, pitch, vel])

        if s[0] == 1428: # channel after touch

            time += (s[1]-16) * 16
            channel = s[2]
            vel = (s[3]-16-128-128-256)

            song_f.append(['channel_after_touch', time, channel, vel])

        if s[0] == 1429: # pitch wheel change

            time += (s[1]-16) * 16
            channel = s[2]
            pitch_wheel = (s[3]-(16+128+128+256+128+128+128+128)) * 128

            song_f.append(['pitch_wheel_change', time, channel, pitch_wheel])

detailed_stats = TMIDIX.Tegridy_SONG_to_Full_MIDI_Converter(song_f,
                                                    output_signature = 'Full MIDI Music Transformer',
                                                    output_file_name = '/content/Full-MIDI-Music-Transformer-Composition',
                                                    track_name='Project Los Angeles'
                                                    )

"""# Congrats! You did it! :)"""