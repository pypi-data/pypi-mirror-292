class Rectangle:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.x = x
        self.y = y

    def to_dict(self):
        return {
            self.width: self.width,
            self.height: self.height,
            self.x: self.x,
            self.y: self.y
        }
