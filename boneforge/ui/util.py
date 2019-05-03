"""my.skeleton.boneforge.ui.util
"""

class Orientation(int):
    
    names = ("up", "right", "down", "left")

    def __new__(cls, value=0):
        if isinstance(value, basestring):
            value = cls.names.index(value)
        return super(Orientation, cls).__new__(cls, value % 4)

    def __repr__(self):
        return "{0}({1!r})".format(self.__class__.__name__, self.name())

    def next(self):
        return Orientation(self + 1)

    def previous(self):
        return Orientation(self - 1)
    
    def sides(self):
        return self.previous(), self.next()

    def opposite(self):
        return Orientation(self + 2)

    def name(self):
        return self.names[self]

Orientation.up = Orientation(0)
Orientation.right = Orientation(1)
Orientation.down = Orientation(2)
Orientation.left = Orientation(3)