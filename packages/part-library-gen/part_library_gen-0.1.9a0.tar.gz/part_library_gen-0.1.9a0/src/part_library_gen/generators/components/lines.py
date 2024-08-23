
class Lines:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.points = []

    def add_point(self, x, y):
        self.points.append((x, y))
