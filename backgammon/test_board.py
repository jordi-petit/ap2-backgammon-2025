from board import Dice

# these are just some sample tests


def test_dice_is_valid():
    """Check if dice.is_valid works."""

    assert Dice(1, 1).is_valid()
    assert Dice(6, 6).is_valid()
    assert Dice(1, 6).is_valid()
    assert Dice(6, 1).is_valid()
    assert not Dice(0, 1).is_valid()
    assert not Dice(1, 0).is_valid()
    assert not Dice(7, 1).is_valid()
    assert not Dice(1, 7).is_valid()


def test_dice_is_double():
    """Check if dice.is_double works."""

    assert Dice(1, 1).is_double()
    assert Dice(6, 6).is_double()
    assert not Dice(1, 2).is_double()
    assert not Dice(3, 4).is_double()
