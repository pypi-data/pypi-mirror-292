class PartNumber:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y

    def to_dict(self):
        return {
            'text': self.text,
            'x': self.x,
            'y': self.y
        }
