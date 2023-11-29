import json
import random
from psychopy import visual, core, event
from pylsl import StreamInfo, StreamOutlet


def get_keypress():
    keys = event.getKeys()
    if keys:
        return keys[0]
    else:
        return None

# Create a new LSL stream
info = StreamInfo('WordMarkers', 'Markers', 1, 0, 'int32', 'wordstream')
outlet = StreamOutlet(info)

# Load words from a JSON file
with open('words.json', 'r') as file:
    data = json.load(file)
    words = data["words"]

# Randomize the order of the words
random.shuffle(words)

# Set up a PsychoPy window
win = visual.Window(fullscr=True, color=(0, 0, 0))

core.wait(2.5) # Wait 2.5 seconds before starting

# Main loop for displaying words and sending markers
for word_info in words:
    # Check for keypresses
    keypress = get_keypress()

    if keypress:
        if keypress == "escape":
            exit()
        else:
            continue

    # Display the word
    text = visual.TextStim(win, text=word_info["word"], color=(1, 1, 1))
    text.draw()
    win.flip()

    # Send the index as a marker
    outlet.push_sample([word_info["index"]])
    print(word_info["index"]) # Print the index to the console for debugging purposes

    # Keep the word on screen for 3 seconds
    core.wait(3)

    # Show a blank screen for 6 seconds
    win.flip()
    core.wait(6)

# Close the window
win.close()
