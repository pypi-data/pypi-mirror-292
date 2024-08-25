class Pin:
    def __init__(self, name, number, function, description: str, x: int, y: int, length: int, rotation: int,
                 name_visible=True):
        self.name = name
        self.name_visible = name_visible
        self.number = number
        self.number_visible = True
        self.function = function
        self.description = description
        self.x = x
        self.y = y
        self.length = length
        self.rotation = rotation


