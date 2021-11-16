from . import legQuad


class LegBack(legQuad.LegQuad):
    def __init__(self, side, name, distance=1.5, height=0.2):

        legQuad.LegQuad.__init__(self, side, name, distance, height, is_front=0)
        self._rtype = 'back'
