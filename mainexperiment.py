import json
import random
import os

from psychopy import visual, core, event
from pylsl import StreamInfo, StreamOutlet
from PIL import Image

subgroup_dict = {
    "Thumbs-up": 1,
    "Thumbs-down": 2,
    "Hand-flat": 3,
    "OK": 4,
    "Peace": 5,
    "None": 6
}

def get_keypress():
    keys = event.getKeys()
    if keys:
        return keys[0]
    else:
        return None

iterations = 1 # Number of times to repeat the word list

full_path = os.getcwd() #os.path.join(os.getcwd(), "fnirsTest")

# Image paths
image_path = os.path.join(full_path, "images")
image_path_arr = []
for filename in os.listdir(image_path):
    full_name = os.path.join(image_path, filename)
    if os.path.isfile(full_name):
        image_path_arr.append(full_name)

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

core.wait(4) # Wait 4 seconds before starting

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
        if(word_info["sub-group"] != "None"):
            img = visual.ImageStim(win, image=image_path_arr[subgroup_dict[word_info["sub-group"]] - 1], units="pix", size=(800, 600))

        # Display the word
        text = visual.TextStim(win, text=word_info["word"], color=(0, 0, 0), pos=(0, 350), colorSpace='rgb255')
                
        img.draw()
        text.draw()
        win.flip()

        # Send the index as a marker
        outlet.push_sample([word_info["index"]])
        print(word_info["index"]) # Print the index to the console for debugging purposes

        # Keep the word on screen for 3 seconds
        core.wait(3)

        # Show a blank screen for 8 seconds
        win.flip()
        core.wait(8)

        # Show a rest screen for 6 seconds
        rest_text = visual.TextStim(win, text="Rest", color=(245, 222, 179))
        rest_text.draw()
        win.flip()
        core.wait(6)

# Close the window
win.close()
