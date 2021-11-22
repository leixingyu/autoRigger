from . import legQuad


class LegFront(legQuad.LegQuad):
    def __init__(self, side, name, distance=1.5, height=0.2):
        legQuad.LegQuad.__init__(self, side, name, distance, height, 1)
        self._rtype = 'front'
