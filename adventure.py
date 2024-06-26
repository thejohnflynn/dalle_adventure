import sys
import os
import pygame
import hashlib
import urllib.request
from gtts import gTTS
from openai import OpenAI

# Game locations
locations = [
    {
        "answer": "",
        "prompt": "You are in a place with lollipops all around you. There is a fountain of tree lollipops.",
    },
    {
        "answer": "l",
        "prompt": "The lollipop on the left is a big rainbow. The lollipop on the right is a love heart shape. Which lollipop will you choose?",
    },
    {
        "answer": "",
        "prompt": "You arrive at Santa and his reindeers house. You see lots of presents.",
    },
    {
        "answer": "r",
        "prompt": "Santa offers you a choice. The present on the left is covered with chocolate and marmalade. The present on the right is covered with strawberries and blackcurrant. Which present do you choose?",
    },
    {
        "answer": "l",
        "prompt": "Now you are transported to a cat land with loads of cats and poops. You wee and you poo there. A cat on the left is covered with strawberries and the right cat is covered with ants. Which one do you take home?",
    },
    # {
    #     "answer": "l",
    #     "prompt": "You see a bunny rabbit with a magic wand. They zap you with the wand and now you are under the sea. There is a fire mermaid on the left or an electric mermaid on the right. Which mermaid do you want to be?",
    # },
    # {
    #     "answer": "r",
    #     "prompt": "Now you are a mermaid. Two seahorses ask you for a ride. The seahorse on the left is silver and the seahorse on the right has go fast power. Which seahorse do you want to ride?",
    # },
    # {
    #     "answer": "r",
    #     "prompt": "The seahorse drops you off and you see two mermaid cats. The one on the left has the head of a mermaid and the body of a cat. The one on the right has the opposite, they have the head of a cat and the tail of a mermaid! Which mermaid cat do you want to cuddle?",
    # },
    {
        "answer": "end",
        "prompt": "Amazing work, you have won a golden medal and a big enormous rainbow lollipop with silver and gold. I hope you will play again. Goodbye.",
    },
]


# Image generation config
IMAGE_MODEL = "dall-e-3"
IMAGE_SIZE = "1024x1024"
IMAGE_QUALITY = "standard"
IMAGE_DIR = "images"
CHILD_AGE_TARGET = 3

# Colours and fonts config
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 1024
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT_SIZE = 26
LINE_SPACING = 1.38

# Game global variables
loc_idx = 0
game_state = "intro"
next_game_state = game_state
last_said_text = ""
running = True
holding = True
bg_image = None
client = OpenAI()

# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Adventure Game")
font = pygame.font.SysFont("timesnewroman", FONT_SIZE)


def generate_all_images(locations):
    """Generate images for all locations if they do not already exist."""
    print("Generating images, this might take a few minutes...")
    os.makedirs("images", exist_ok=True)
    for location in locations:
        prompt = location["prompt"]
        md5 = hashlib.md5(prompt.encode()).hexdigest()
        filename = os.path.join("images", f"{md5}.png")
        if os.path.isfile(filename):
            print(f"Skipping {filename}, already exists.")
        else:
            if generate_image(prompt):
                print(f"Saved to {filename}.")
            else:
                print(f"Failed to generate image for {prompt}.")
        location["image"] = filename
    print("Done.")


def generate_image(prompt):
    """Generate an image using the OpenAI API and save it to a file."""
    try:
        response = client.images.generate(
            model=IMAGE_MODEL,
            prompt=f"Please make a cute image suitable for {CHILD_AGE_TARGET} year old kids, with no writing, based on: {prompt}",
            size=IMAGE_SIZE,
            quality=IMAGE_QUALITY,
            n=1,
        )
        md5 = hashlib.md5(prompt.encode()).hexdigest()
        filename = os.path.join("images", f"{md5}.png")
        urllib.request.urlretrieve(response.data[0].url, filename)
        return True
    except Exception as e:
        print(f"Error generating image for prompt '{prompt}': {e}")
        return False


def split_text(text, max_length=50):
    """Split text on whitespace into lines of specified maximum length."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= max_length:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return "\n".join(lines)


def get_filename(prompt):
    """Use md5 of prompt to create a filename."""
    md5 = hashlib.md5(prompt.encode()).hexdigest()
    return os.path.join("images", f"{md5}.png")


def draw_text(text, x, y, color=WHITE):
    """Draw text on top of a white background with long lines word wrapped."""
    lines = split_text(text).splitlines()
    rect_surface = pygame.Surface(
        (SCREEN_WIDTH, len(lines) * LINE_SPACING * FONT_SIZE + 20), pygame.SRCALPHA
    )
    rect_surface.fill((0, 0, 0, 160))
    screen.blit(rect_surface, (0, y - 10))
    for i, line in enumerate(lines):
        line_surface = font.render(line, True, color)
        screen.blit(line_surface, (x, y + i * FONT_SIZE * LINE_SPACING))


def say(text):  # TODO: Remove global state
    """Convert text to speech and play it using pygame."""
    global last_said_text
    if text != last_said_text:
        md5 = hashlib.md5(text.encode()).hexdigest()
        filename = os.path.join("sounds", f"{md5}.mp3")
        if not os.path.isfile(filename):
            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(filename)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        last_said_text = text


def draw_text_and_say(text, x, y, color=WHITE):
    """Draw text and say it using text-to-speech."""
    draw_text(text, x, y, color)
    say(text)


def handle_choice_events(event_key, correct_answer, curr_idx):
    """Handle user choice input and update the game state accordingly."""
    if (correct_answer == "l" and event_key == pygame.K_l) or (
        correct_answer == "r" and event_key == pygame.K_r
    ):
        # game_state = "correct"
        curr_idx += 1
    else:
        # game_state = "incorrect"
        curr_idx = 0  # All the way back to the start :*(
    return curr_idx


def is_choice_or_scene(locations, idx):
    if locations[idx]["answer"] in ["l", "r"]:
        return "choice"
    else:
        return "scene"


def handle_game_events():
    """Process pygame events and update the game state."""
    global running, game_state, holding, loc_idx
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.mixer.music.stop()
            game_state = "hard_quit"
        elif event.type == pygame.KEYDOWN:
            pygame.mixer.music.stop()
            if event.key == pygame.K_q:
                game_state = "quit"
            elif event.key == pygame.K_c and game_state not in ["choice", "scene"]:
                holding = False
            elif event.key == pygame.K_c and game_state == "scene":
                loc_idx += 1
                game_state = is_choice_or_scene(locations, loc_idx)
            elif game_state == "choice" and event.key in [pygame.K_l, pygame.K_r]:
                loc_idx = handle_choice_events(
                    event.key, locations[loc_idx]["answer"], loc_idx
                )
                game_state = "correct" if loc_idx > 0 else "incorrect"
            else:
                game_state = "help"
    return game_state != "hard_quit"


# State changes and handling
def handle_intro():
    global next_game_state, bg_image
    bg_image = None
    draw_text_and_say(
        "Hi, welcome to the best game in the world! Press c to continue...",
        100,
        100,
    )
    next_game_state = is_choice_or_scene(locations, loc_idx)


def handle_scene():
    global bg_image
    filename = get_filename(locations[loc_idx]["prompt"])
    bg_image = pygame.image.load(filename).convert()
    draw_text_and_say(
        f"{locations[loc_idx]['prompt']} Press c to continue...", 100, 100
    )


def handle_choice():
    global bg_image
    filename = get_filename(locations[loc_idx]["prompt"])
    bg_image = pygame.image.load(filename).convert()
    draw_text_and_say(f"{locations[loc_idx]['prompt']} Press l for left or r for right...", 100, 100)


def handle_correct():
    global next_game_state, bg_image
    bg_image = None
    draw_text_and_say(
        "Correct! How will you remember the right answer? Press c to continue...",
        100,
        100,
    )
    next_game_state = (
        "win"
        if loc_idx >= len(locations) - 1
        else is_choice_or_scene(locations, loc_idx)
    )


def handle_incorrect():
    global next_game_state, bg_image
    bg_image = None
    draw_text_and_say(
        "Wrong! You go all the way back to the start! Press c to continue...", 100, 100
    )
    next_game_state = is_choice_or_scene(locations, loc_idx)


def handle_win():
    global next_game_state, bg_image
    filename = get_filename(locations[-1]["prompt"])
    bg_image = pygame.image.load(filename).convert()
    draw_text_and_say(f"{locations[-1]['prompt']} Press c...", 100, 100)
    next_game_state = "hard_quit"


def handle_quit():
    global next_game_state, bg_image
    bg_image = None
    draw_text_and_say("Thanks for playing, goodbye. Press c...", 100, 100)
    next_game_state = "hard_quit"


def handle_help():
    global next_game_state, bg_image
    bg_image = None
    draw_text_and_say(
        "Please press l for left, r for right or press q to quit! Press c to continue...",
        100,
        100,
    )
    next_game_state = is_choice_or_scene(locations, loc_idx)


state_handlers = {
    "intro": handle_intro,
    "scene": handle_scene,
    "choice": handle_choice,
    "correct": handle_correct,
    "incorrect": handle_incorrect,
    "win": handle_win,
    "quit": handle_quit,
    "help": handle_help,
}

generate_all_images(locations)

for i, l in enumerate(locations):
    print(f"{i} {is_choice_or_scene(locations, i)}")

# Main game loop
while running:
    screen.fill(BLACK)
    if bg_image:
        screen.blit(bg_image, (0, 0))

    if game_state in state_handlers:
        state_handlers[game_state]()

    running = handle_game_events()

    pygame.display.flip()

    if next_game_state != game_state and not holding:
        game_state = next_game_state
        holding = True

pygame.quit()
sys.exit()
