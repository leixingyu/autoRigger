from . import chainFK


class LimbFK(chainFK.ChainFK):

    def __init__(self, side, name, length, ltype='null'):
        segment = 3
        self.ltype = ltype
        self.direction = [0, -1, 0]
        self._rtype = ltype

        if ltype == 'arm' and side == 'l':
            self.direction = [1, 0, 0]
        elif ltype == 'arm' and side == 'r':
            self.direction = [-1, 0, 0]

        chainFK.ChainFK.__init__(self, side, name, segment, length, self.direction)
