import pygame
from pygame import Surface


class AssetsManager:
    _ASSETS_PATH = "assets/"
    _IMAGES_PATH = "images/"
    _SOUNDS_PATH = "sounds/"
    _FONTS_PATH = "fonts/"

    _images: dict[str, Surface] = {}
    _sounds = {}
    _fonts = {}

    @staticmethod
    def load_image(name, path, scale_factor: float | None = None):
        image = pygame.image.load(AssetsManager._ASSETS_PATH + AssetsManager._IMAGES_PATH + path).convert_alpha()

        if scale_factor:
            w, h = image.get_size()
            image = pygame.transform.scale(image, (int(w * scale_factor), int(h * scale_factor)))

        AssetsManager._images[name] = image
        return image

    @staticmethod
    def get_image(name):
        return AssetsManager._images[name]

    @staticmethod
    def load_sound(name, path):
        AssetsManager._sounds[name] = pygame.mixer.Sound(AssetsManager._ASSETS_PATH + AssetsManager._SOUNDS_PATH + path)

    @staticmethod
    def get_sound(name):
        return AssetsManager._sounds[name]

    @staticmethod
    def load_font(name, size, path):
        font = pygame.font.Font(AssetsManager._ASSETS_PATH + AssetsManager._FONTS_PATH + path, size)
        AssetsManager._fonts[name] = font
        return font

    @staticmethod
    def get_font(name):
        return AssetsManager._fonts[name]
