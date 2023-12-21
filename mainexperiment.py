import json
import random
import os

import numpy as np

from psychopy import visual, core, event
from pylsl import StreamInfo, StreamOutlet
from PIL import Image

subgroup_dict = {
    1 : "Hand-flat",
    2 : "OK",
    3 : "thumbs-down",
    4 : "thumbsup"
}

files_dict = {}

def get_keypress():
    keys = event.getKeys()
    if keys:
        return keys[0]
    else:
        return None

iterations = 3 # Number of times to repeat the word list

full_path = os.getcwd() #os.path.join(os.getcwd(), "fnirsTest")

# Create a new LSL stream
info = StreamInfo('Trigger', 'Markers', 1, 0, 'int32', 'wordstream')
outlet = StreamOutlet(info)


# Load words from a JSON file
with open(os.path.join(full_path, "words.json"), 'r') as file:
    data = json.load(file)
    words = data["words"]

init_win = visual.Window(fullscr=False, color=(0, 0, 0), size=(1200, 800))
init_small_text = visual.TextStim(init_win, text="Set up LabRecorder, and press Enter to start.", color=(1, 1, 1))

while True:
    init_small_text.draw()
    init_win.flip()

    keypress = get_keypress()

    if keypress == "return":
        break
    elif keypress == "escape":
        exit()

# Set up a PsychoPy window
win = visual.Window(fullscr=False, color=(0, 0, 0), size = (1200, 800), screen=0, units='pix', allowGUI=True)

init_text = visual.TextStim(win, text="Please focus on each word as it appears on the screen. Keep focused on it until you see the rest screen appear. When you see the word rest appear, feel free to think about whatever you want.", color=(1,1,1))
init_text.draw()
win.flip()

core.wait(6) # Wait 6 seconds before starting

# Main loop for displaying words and sending markers
for i in range(iterations):
    # Randomize the order of the words
    random.shuffle(words)

    for word_info in words:
        # Check for keypresses
        keypress = get_keypress()

        if keypress:
            if keypress == "escape":
                exit()
            else:
                continue

        # Display the image 
        img_index = np.ceil(word_info["index"] / 2).astype(int)
        img_path = os.path.join(full_path, "images", subgroup_dict[img_index] + ".jpg")
        img = visual.ImageStim(win, image=img_path, units="pix", size=(800, 600))

        # Display the word
        text = visual.TextStim(win, text=word_info["word"], color=(0, 0, 0), pos=(0, 350), colorSpace='rgb255')
                
        img.draw()
        text.draw()
        win.flip()

        # Send the index as a marker
        outlet.push_sample([word_info["index"]])
        print(word_info["index"]) # Print the index to the console for debugging purposes

        # Keep the word on screen for 11 seconds
        core.wait(11)

        # Show a rest screen for 8 seconds
        rest_text = visual.TextStim(win, text="Rest", color=(245, 222, 179))
        rest_text.draw()
        win.flip()
        core.wait(8)

# Close the window
win.close()
