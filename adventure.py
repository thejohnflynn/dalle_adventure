import sys
import os
import pygame
import hashlib
import urllib.request
from gtts import gTTS
from openai import OpenAI

# Game locations
# locations = [
#     {
#         "answer": "",
#         "prompt": "You are in a place with lollipops all around you. There is a fountain of tree lollipops.",
#     },
#     {
#         "answer": "l",
#         "prompt": "The lollipop on the left is a big rainbow. The lollipop on the right is a love heart shape. Which lollipop will you choose?",
#     },
#     {
#         "answer": "",
#         "prompt": "You arrive at Santa and his reindeers house. You see lots of presents.",
#     },
#     {
#         "answer": "r",
#         "prompt": "Santa offers you a choice. The present on the left is covered with chocolate and marmalade. The present on the right is covered with strawberries and blackcurrant. Which present do you choose?",
#     },
#     {
#         "answer": "l",
#         "prompt": "Now you are transported to a cat land with loads of cats and poops. You wee and you poo there. A cat on the left is covered with strawberries and the right cat is covered with ants. Which one do you take home?",
#     },
#     {
#         "answer": "l",
#         "prompt": "You see a bunny rabbit with a magic wand. They zap you with the wand and now you are under the sea. There is a fire mermaid on the left or an electric mermaid on the right. Which mermaid do you want to be?",
#     },
#     {
#         "answer": "r",
#         "prompt": "Now you are a mermaid. Two seahorses ask you for a ride. The seahorse on the left is silver and the seahorse on the right has go fast power. Which seahorse do you want to ride?",
#     },
#     {
#         "answer": "r",
#         "prompt": "The seahorse drops you off and you see two mermaid cats. The one on the left has the head of a mermaid and the body of a cat. The one on the right has the opposite, they have the head of a cat and the tail of a mermaid! Which mermaid cat do you want to cuddle?",
#     },
#     {
#         "answer": "end",
#         "prompt": "Amazing work, you have won a golden medal and a big enormous rainbow lollipop with silver and gold. I hope you will play again. Goodbye.",
#     },
# ]

locations = [
    {
        "answer": "",
        "prompt": "You are in the sea, up ahead you see lots of beautiful whales swimming.",
    },
    {
        "answer": "r",
        "prompt": "You get closer. There are two whales. The whale on the left is a humpback whale with skateboards. The whale on the right is a blue whale with roller skates. Which whale do you want to ride?",
    },
    {
        "answer": "",
        "prompt": "You are now transported by a fairy godmother into the sky.",
    },
    {
        "answer": "",
        "prompt": "You jump onto a unicorn and are riding high in the clouds.",
    },
    {
        "answer": "r",
        "prompt": "There are two more unicorns above your head. The unicorn on the left is covered with unicorn dust. The unicorn on the right is covered with wee wee and poo poo. Which unicorn do you choose?",
    },
    {
        "answer": "l",
        "prompt": "Suddenly, you land in front of two fairy godmothers. The fairy godmother on the left is drinking two beers. The fairy godmother on the right is covered with rock and roll band guitars. Which fairy godmother do you speak to?",
    },
    {
        "answer": "",
        "prompt": "Now a giant poo brush comes along. It transports you to a new place.",
    },
    {
        "answer": "l",
        "prompt": "You are now playing video games with one big finger. There is a game controller. The joystick on the left is silver. The buttons on the right are rainbow. Which control do you press?",
    },
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


def generate_all_images(locations):
    """Generate images for all locations if they do not already exist."""
    print("Generating images, this might take a few minutes...")
    os.makedirs("images", exist_ok=True)
    client = OpenAI
    for location in locations:
        prompt = location["prompt"]
        md5 = hashlib.md5(prompt.encode()).hexdigest()
        filename = os.path.join("images", f"{md5}.png")
        if os.path.isfile(filename):
            print(f"Skipping {filename}, already exists.")
        else:
            if generate_image(prompt, client):
                print(f"Saved to {filename}.")
            else:
                print(f"Failed to generate image for {prompt}.")
        location["image"] = filename
    print("Done.")


def generate_image(prompt, client):
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
    """Split text on whitespace into lines of specified maximum length, preserving existing newline characters."""
    paragraphs = text.split("\n")
    lines = []

    for paragraph in paragraphs:
        words = paragraph.split(" ")
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
        lines.append("")  # Add an empty line to space out the paragraphs

    # Remove the last empty line added
    if lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)


def get_filename(prompt):
    """Use md5 of prompt to create a filename."""
    md5 = hashlib.md5(prompt.encode()).hexdigest()
    return os.path.join("images", f"{md5}.png")


def draw_text_and_say(text, x, y, color=WHITE):
    """Draw text and say it using text-to-speech."""
    draw_text(text, x, y, color)
    say(text)


def is_choice_or_scene(locations, idx):
    if locations[idx]["answer"] in ["l", "r"]:
        return "choice"
    else:
        return "scene"


# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.SysFont("timesnewroman", FONT_SIZE)
pygame.display.set_caption("Adventure Game")


def draw_text(text, x, y, color=WHITE):  # TODO: screen and font are globals
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


last_said_text = ""


def say(text):  # TODO: Remove global last_said_text
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


# Game global variables
loc_idx = 0
game_state = "intro"
running = True
bg_image = None
current_prompt = ""
generate_all_images(locations)

# Main game loop
while running:
    screen.fill(BLACK)
    if bg_image:
        screen.blit(bg_image, (0, 0))

    # Do stuff based on state
    if game_state == "intro":
        bg_image = None
        draw_text_and_say(
            "Hi, welcome to the best game in the world!\nPress c to continue...",
            100,
            100
        )
    elif game_state == "scene":
        filename = get_filename(locations[loc_idx]["prompt"])
        bg_image = pygame.image.load(filename).convert()
        draw_text_and_say(
            f"{locations[loc_idx]['prompt']}\nPress c to continue...", 100, 100, screen
        )
    elif game_state == "correct":
        bg_image = None
        draw_text_and_say(
            "Correct! How will you remember the right answer?\nPress c to continue...",
            100,
            100
        )
    elif game_state == "incorrect":
        bg_image = None
        draw_text_and_say(
            "Wrong! You go all the way back to the start!\nPress c to continue...",
            100,
            100
        )
    elif game_state == "choice":
        filename = get_filename(locations[loc_idx]["prompt"])
        bg_image = pygame.image.load(filename).convert()
        draw_text_and_say(
            f"{locations[loc_idx]['prompt']}\nPress l for left or r for right...",
            100,
            100
        )
    elif game_state == "help":
        bg_image = None
        draw_text_and_say(
            "Please press l for left, r for right or press q to quit!\nPress c to continue...",
            100,
            100
        )
    elif game_state == "win":
        filename = get_filename(locations[-1]["prompt"])
        bg_image = pygame.image.load(filename).convert()
        draw_text_and_say(
            f"{locations[-1]['prompt']}\nPress c to quit...", 100, 100, screen
        )

    # On input, transition to a different state if needed & do one-time-only actions
    for event in pygame.event.get():
        pygame.mixer.music.stop()
        if event.type == pygame.QUIT:
            running = False

        if game_state == "intro":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    loc_idx = 0
                    game_state = is_choice_or_scene(locations, loc_idx)
        elif game_state == "scene":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    loc_idx += 1
                    game_state = is_choice_or_scene(locations, loc_idx)
        elif game_state == "correct":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    loc_idx += 1
                    game_state = (
                        "win"
                        if loc_idx >= len(locations) - 1
                        else is_choice_or_scene(locations, loc_idx)
                    )
        elif game_state == "incorrect":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    loc_idx = 0
                    game_state = is_choice_or_scene(locations, loc_idx)
        elif game_state == "choice":
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_l, pygame.K_r]:
                    answer = locations[loc_idx]["answer"]
                    if (answer == "l" and event.key == pygame.K_l) or (
                        answer == "r" and event.key == pygame.K_r
                    ):
                        game_state = "correct"
                    else:
                        game_state = "incorrect"
                elif event.key == pygame.K_s:
                    game_state = "say_again"
        elif game_state == "win":
            if event.type == pygame.KEYDOWN:
                running = False

    pygame.display.flip()

    # Debug
    # print(f"game_state {game_state}")
    # print(f"loc_idx {loc_idx}")

pygame.quit()
sys.exit()
