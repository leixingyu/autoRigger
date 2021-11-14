from ..chain import chainFKIK


class Tail(chainFKIK.ChainFKIK):
    """
    Rig module for FKIK Tail
    """

    def __init__(self, side, name, segment=6, length=4.0, direction=None):

        if not direction:
            direction = [0, -1, 0]

        chainFKIK.ChainFKIK.__init__(self, side, name, segment, length, direction)
