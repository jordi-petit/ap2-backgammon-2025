from __future__ import annotations
from PIL import Image, ImageDraw
from random import randint, random
from board import Board, WHITE, BLACK


def draw(b: Board, path: str, style: int = 1) -> None:

    # coordinates carefully and patiently computed by jpetit

    def get_region(image: Image.Image) -> Image.Image:
        box = (0, 0, image.size[0] - 1, image.size[1] - 1)
        return image.crop(box)

    # load individual images
    assert style in [1, 2, 3]
    background = Image.open(f"images/B{style}-BG.png")
    board = Image.open(f"images/B{style}.png")
    black_checker = Image.open(f"images/CS{style}-B.png")
    white_checker = Image.open(f"images/CS{style}-W.png")
    dice = [
        Image.open("images/d1.png"),
        Image.open("images/d2.png"),
        Image.open("images/d3.png"),
        Image.open("images/d4.png"),
        Image.open("images/d5.png"),
        Image.open("images/d6.png"),
    ]

    background = get_region(background)
    board = get_region(board)
    black_checker = get_region(black_checker)
    white_checker = get_region(white_checker)
    dices = [get_region(die) for die in dice]

    # create image
    image = background.copy()

    # draw board
    image.paste(board, (0, 0), board)

    # draw checkers
    coordsX = [135, 200, 265, 330, 395, 460, 603, 668, 733, 798, 862, 927, 992]
    coordTop = 45
    coordBottom = 530
    checkerH = 43

    for i in range(1, 25):
        checker = black_checker if b.cell(i - 1) < 0 else white_checker
        for j in range(abs(b.cell(i - 1))):
            if abs(b.cell(i - 1)) <= 5:
                h = checkerH
            else:
                h = checkerH * 5 // abs(b.cell(i - 1))
            if i <= 12:
                x = coordsX[12 - i]
                y = coordTop + j * h
            else:
                x = coordsX[i - 13]
                y = coordBottom - j * h
            image.paste(checker, (x, y), checker)

    # write points
    drawer = ImageDraw.Draw(image)
    if b.current() == WHITE:
        for i in range(12):
            drawer.text((coordsX[i] + 15, coordTop - 22), str(12 - i), align="center")
        for i in range(12):
            drawer.text((coordsX[i] + 15, coordBottom + 58), str(13 + i), align="center")
    if b.current() == BLACK:
        for i in range(12):
            drawer.text((coordsX[i] + 15, coordTop - 22), str(13 + i), align="center")
        for i in range(12):
            drawer.text((coordsX[i] + 15, coordBottom + 58), str(12 - i), align="center")

    # draw checkers on bar
    coordX = 530
    n = b.bar(WHITE)
    h = checkerH if n <= 4 else checkerH * 4 // n
    for i in range(n):
        image.paste(white_checker, (coordX, checkerH + coordTop + (i + 1) * h), white_checker)
    n = b.bar(BLACK)
    h = checkerH if n <= 4 else checkerH * 4 // n
    for i in range(b.bar(BLACK)):
        image.paste(black_checker, (coordX, coordBottom - checkerH - (i + 1) * h), white_checker)

    # draw checkers off
    coordX = 1015
    n = b.off(WHITE)
    h = checkerH * 4.75 // 15
    for i in range(n):
        image.paste(white_checker, (coordX, int(coordBottom - i * h)), white_checker)
    n = b.off(BLACK)
    for i in range(n):
        image.paste(black_checker, (coordX, int(coordTop + i * h)), black_checker)

    # draw dice with a random rotation and position according to the current player
    a1 = random() * 360
    a2 = random() * 360
    rx1 = randint(-10, 10)
    ry1 = randint(-10, 10)
    rx2 = randint(-10, 10)
    ry2 = randint(-10, 10)
    die1 = dices[b.dice().die1 - 1].rotate(a1, expand=1)
    die2 = dices[b.dice().die2 - 1].rotate(a2, expand=1)
    if b.current() == WHITE:
        image.paste(die1, (810 + rx1, 270 + ry1), die1)
        image.paste(die2, (900 + rx2, 270 + ry2), die2)
    else:
        image.paste(die1, (130 + rx1, 270 + ry1), die1)
        image.paste(die2, (220 + rx2, 270 + ry2), die2)

    image.save(path, "PNG")


def show(b: Board) -> None:

    def nice_die(n: int) -> str:
        return str(n)
        return "⚀⚁⚂⚃⚄⚅"[n - 1]  # maco però massa petit

    red_checker = "🔴"
    grn_checker = "🟢"
    if b.current() == WHITE:
        current = "(" + red_checker + ")"
    elif b.current() == BLACK:
        current = "(" + grn_checker + ")"
    else:
        current = ""

    h = max(5, max([abs(c) for c in b.cells()]))
    for i in range(h):
        for j in range(24):
            n = b.cell(j)
            if n == 0:
                print("    ", end="")
            elif n > 0:
                if n < h - i:
                    print("    ", end="")
                else:
                    print(f" {red_checker} ", end="")
            else:
                if -n < h - i:
                    print("    ", end="")
                else:
                    print(f" {grn_checker} ", end="")
        print()
    if b.current() == WHITE:
        print(" ".join(f" {i+1:02d}" for i in range(24)))
    elif b.current() == BLACK:
        print(" ".join(f" {i+1:02d}" for i in range(23, -1, -1)))
    print()

    print("-" * 95)

    print(
        " " * 24,
        f"Turn: {b.turn()}{current}   Dice: {nice_die(b.dice().die1)}-{nice_die(b.dice().die2)}   Bar: {b.bar(WHITE)}{red_checker} {b.bar(BLACK)}{grn_checker}   Off: {b.off(WHITE)}{red_checker} {b.off(BLACK)}{grn_checker}",
    )

    if b.winner() == WHITE:
        print(f"Winner: {red_checker}")
    elif b.winner() == BLACK:
        print(f"Winner: {grn_checker}")

    print("-" * 95)
    print()
    print()
