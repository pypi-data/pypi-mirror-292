class Symbol:
    def __init__(self, part_number, designator):
        self.part_number = part_number
        self.designator = designator
        self.pins = []
        self.body = []
        self.width = 0
        self.height = 0

    def add_pin(self, pin):
        self.pins.append(pin)

    def add_body(self, element):
        self.body.append(element)