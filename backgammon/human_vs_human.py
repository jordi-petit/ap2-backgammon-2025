from board import Board, WHITE, DiceCup, Move
from show import show


def read_move() -> Move:
    """..."""
    ...


def main() -> None:
    """..."""

    seed = 123456
    cup = DiceCup(seed)
    board = Board(cup.roll())
    show(board)
    while not board.over():
        print("White move?")
        move = read_move()
        board = board.play(move)
        board = board.next(cup.roll())
        show(board)
        if not board.over():
            print("Black move?")
            move = read_move()
            board = board.play(move)
            board = board.next(cup.roll())
            show(board)
    print(f"Winner: {'W' if board.winner() == WHITE else 'B'}")
    print(f"Seed: {seed}")
