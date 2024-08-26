import drawsvg as svg
from drawsvg import Circle

from .pin import generate_symbol_pin
from ...generators.components.rectangle import Rectangle
from ...generators.components.line import Line
from ...generators.components.lines import Lines


def export(symbol, filename=None):
    d = svg.Drawing(symbol.width, symbol.height, origin='center')

    for element in symbol.body:
        if isinstance(element, Rectangle):
            d.append(svg.Rectangle(element.x,
                                   element.y,
                                   element.width,
                                   element.height,
                                   stroke_width=3,
                                   fill='yellow',
                                   stroke='black'))
        if isinstance(element, Lines):
            points = [element.x, element.y]
            for point in element.points:
                points += list(point)
            d.append(svg.Lines(*points,
                               stroke_width=4,
                               fill='yellow',
                               stroke='black'))
        if isinstance(element, Line):
            d.append(svg.Line(element.x1, element.y1, element.x2, element.y2, stroke_width=4, stroke='black'))

    for pin in symbol.pins:
        d.append(generate_symbol_pin(pin))

    d.append(svg.Text(symbol.designator.designator,
                      40,
                      symbol.designator.x,
                      symbol.designator.y))

    d.append(svg.Text(symbol.part_number.text,
                      40,
                      symbol.part_number.x,
                      symbol.part_number.y))

    if filename:
        d.save_svg(f"{filename}.svg")
    return d.as_svg()
