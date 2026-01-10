from PIL import Image
import os

os.makedirs('./assets/characters', exist_ok=True)
os.makedirs('./assets/backgrounds', exist_ok=True)

img = Image.new('RGBA', (256, 256), (200, 150, 100, 255))
img.save('./assets/characters/character1.png')

img = Image.new('RGBA', (256, 256), (220, 160, 110, 255))
img.save('./assets/characters/character2.png')

img = Image.new('RGB', (1920, 1080), (30, 60, 120))
img.save('./assets/backgrounds/bg1.png')

img = Image.new('RGB', (1920, 1080), (60, 40, 100))
img.save('./assets/backgrounds/bg2.png')

print("? All assets created!")



