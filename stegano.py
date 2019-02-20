from PIL import Image
from string import printable
from itertools import product
from typing import Dict, Tuple

__all__ = ["encode", "decode", "image_diff"]

def _create_alphabet() -> str:
    """Erstellt ein String aller erlaubter Zeichen."""
    return printable

def _create_table():
    """Erstelle die Codierungstabelle."""
    alphabet = _create_alphabet()
    code = list(product((-2, -1, 1, 2, 3), repeat=3))
    len_a = len(alphabet)
    len_c = len(code)
    if len_a > len_c:
        alphabet = alphabet[:len_c]
    elif len_c > len_a:
        code = code[:len_a]
    return dict(list(zip(alphabet, code)))


def _single_encode(pixel: Tuple[int], char: str, table: Dict) -> Tuple:
    alphabet = "".join(list(table.keys()))
    assert len(char) == 1
    assert char in alphabet
    code = table.get(char, "*")
    tmp_pixel = [0, 0, 0]
    for i in range(3):
        tmp_pixel[i] = (pixel[i] + code[i]) % 256
    result: Tuple = tuple(tmp_pixel)
    return result


def _single_decode(code: Tuple[int], table: Dict) -> str:
    table = dict(zip(table.values(), table.keys()))
    char = table[code]
    return char


def image_diff(image1, image2):
    with Image.open(image1) as im1:
        with Image.open(image2) as im2:
            assert im1.size == im2.size
            width, height = im1.size
            diff = {}
            for x in range(width):
                for y in range(height):
                    pixel1 = im1.getpixel((x,y))
                    pixel2 = im2.getpixel((x,y))
                    if pixel1 != pixel2:
                        r = pixel1[0] - pixel2[0]
                        g = pixel1[1] - pixel2[1]
                        b = pixel1[2] - pixel2[2]
                        diff[(x, y)] = (r, g, b)
                    else:
                        continue
    return diff


def encode(image_filename, secret_filename) -> str:
    
    # Alphabet erstellen
    alphabet = _create_alphabet()

    # Codierungstabelle erstellen
    table: Dict = _create_table()

    # Klartext einlesen
    with open(secret_filename, "r") as file_obj:
        secret = ""
        for line in file_obj:
            for char in line:
                if char in alphabet:
                    secret += char
                else:
                    secret += "*"

    # Anzahl benutzbarer Pixel zählen
    pixels = []
    with Image.open(image_filename) as im:
        width, height = im.size
        # Spalten durchlaufen
        for x in range(width):
            # Zeilen durchlaufen
            for y in range(height):
                pixel = im.getpixel((x, y))
                r, g, b = pixel
                if r < 2 or r > 253:
                    continue
                elif g < 2 or g > 253:
                    continue
                elif b < 2 or b > 253:
                    continue
                else:
                    pixels.append((x, y))
    
    length_text = len(secret)
    length_image = len(pixels)

    # Längen vergleichen
    if length_text > length_image:
        raise Exception("Text zu lang!")
    elif length_image > length_text:
        pixels = pixels[:length_text]

    length = min(length_image, length_text)

    # Bild öffnen
    with Image.open(image_filename) as im:
        counter = 0
        while counter < length:
            (x, y) = pixels[counter]
            pixel = im.getpixel((x,y))
            char = secret[counter]
            new_pixel = _single_encode(pixel, char, table)
            im.putpixel((x,y), new_pixel)
            counter += 1
    
        # Bild abspeichern
        result_filename = f"{image_filename}_secret.png"
        im.save(result_filename, "png")
        print(result_filename)


def decode(orig, new):
    table = _create_table()
    diff = image_diff(new, orig)
    text = ""
    for coor in diff:
        pixel = diff[coor]
        char = _single_decode(pixel, table)
        text += char
    print(text)
    return text
