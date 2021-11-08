from autoRigger.chain import chainFKIK


class Tail(chainFKIK.ChainFKIK):

    def __init__(self, side, name, segment=6, length=4.0, direction=[0, -1, 0]):

        chainFKIK.ChainFKIK.__init__(self, side, name, segment, length, direction)
