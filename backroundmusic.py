import pygame
import os
from time import sleep

def PlayMusic(path):  # Fix: Added a valid parameter name
    pygame.mixer.init()
    pygame.mixer.music.load(path)  # Fix: Removed position-only argument separator
    pygame.mixer.music.play()

if __name__ == "__main__":
    path = "C:\Users\denis\Desktop\LandLenderUS\LandLender\Audio"
    sleep(10)
