class Designator:
    def __init__(self, designator, x, y):
        self.designator = designator
        self.x = x
        self.y = y

    def to_dict(self):
        return {
            'designator': self.designator,
            'x': self.x,
            'y': self.y
        }
