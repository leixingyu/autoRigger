import math

class Vector(object):

    def __init__(self, *args):
        self._vector = [0, 0, 0]
        if len(args) == 3:
            self._vector = args

    def normal(self):
        if self._vector:
            length = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
            return Vector(
                self.x / length,
                self.y / length,
                self.z / length
            )
        else:
            return Vector(0, 0, 0)

    @property
    def x(self):
        return self._vector[0]

    @property
    def y(self):
        return self._vector[1]

    @property
    def z(self):
        return self._vector[2]

    @property
    def list(self):
        return self._vector


class World(object):

    def __init__(self, vector=None):
        self.vector = vector

    @property
    def origin(self):
        return Vector(0, 0, 0)

    @property
    def x_positive(self):
        return Vector(1, 0, 0)

    @property
    def x_negative(self):
        return Vector(-1, 0, 0)

    @property
    def y_positive(self):
        return Vector(0, 1, 0)

    @property
    def y_negative(self):
        return Vector(0, -1, 0)

    @property
    def z_positive(self):
        return Vector(0, 0, 1)

    @property
    def z_negative(self):
        return Vector(0, 0, -1)