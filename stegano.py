from PIL import Image
from string import ascii_lowercase
from itertools import product
from typing import Dict, Tuple


def create_alphabet():
    pass

def create_table():
    ascii = ascii_lowercase + "*"
    code = list(product((0, -1, 1), repeat=3))
    return dict(list(zip(ascii, code)))


def convert(pixel: Tuple[int], char: str, table: Dict) -> Tuple:
    assert len(char) == 1
    assert char in (ascii_lowercase + "*")
    tmp = table.get(char, "*")
    tmp_pixel = [0, 0, 0]
    for i in range(3):
        tmp_pixel[i] = (pixel[i] + tmp[i]) % 256
    result: Tuple = tuple(tmp_pixel)
    return result


def encode(image_filename, secret_filename) -> str:
    # Codierungstabelle erstellen
    table: Dict = create_table()

    # Klartext einlesen
    with open(secret_filename, "r") as file_obj:
        secret = ""
        char = "1"
        while char:
            char = file_obj.read(1)
            # Nur Kleinbuchstaben akzeptieren!
            if char in (ascii_lowercase + "*"):
                secret += char
            elif char.lower() in (ascii_lowercase + "*"):
                secret += char.lower()
            else:
                secret += "*"

        length = len(secret)

    # Bild öffnen
    with Image.open(image_filename) as im:
        width, height = im.size
        counter = 0
        # Spalten durchlaufen
        for x in range(width):
            # Zeilen durchlaufen
            for y in range(height):
                if counter >= length:
                    break

                old_pixel = im.getpixel((x, y))
                # Es sollen keine Übergänge stattfinden
                if 0 in old_pixel or 255 in old_pixel:
                    continue

                char = secret[counter]
                new_pixel = convert(old_pixel, char, table)
                im.putpixel((x, y), new_pixel)
                counter += 1

        # Erzeugtes Bild abspeichern
        new_filename = f"{image_filename}_secret.png"
        im.save(new_filename, mode="png")
        print(f"filename: {new_filename}")
        im.show()
        return new_filename


if __name__ == "__main__":
    image_filename = "/home/dodo/dev/testtexte/Bild.jpg"
    secret_filename = "/home/dodo/dev/testtexte/rp-online.html"
    encode(image_filename, secret_filename)
