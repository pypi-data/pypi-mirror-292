from .generators.opamp_generator import opamp_generator
from .generators.rectangular_symbol_generator import rectangular_symbol_generator
from .generators.default_generator import default_generator
from .exporters.svg.svg_exporter import export as svg_exporter

supported_pin_functions = ['In', 'Out', 'InAnalog', 'InDigital', 'InDigital;ActiveLow', 'InDigital;ActiveHigh',
                           'OutDigital', 'OutDigital;ActiveLow', 'OutDigital;OpenDrain',
                           'OutDigital;OpenDrain;ActiveLow',
                           'OutAnalog', 'OutAnalog;ActiveLow',
                           'InOut',
                           'PwrIn', 'PwrOut', 'PwrGND',
                           'NC', 'NC-GND', 'NC-Float']


def validate(component_data):
    if component_data is not None:
        if 'designator' not in component_data:
            raise ValueError('designator is missing')
        if 'part' not in component_data:
            raise ValueError('part number is missing')
        if 'pins' not in component_data:
            raise ValueError('pins are missing')
        for pin in component_data['pins']:
            pin_data = component_data['pins'][pin]

            if 'func' not in pin_data:
                raise ValueError('pin function is missing')
            if 'no' not in pin_data:
                raise ValueError('pin number is missing')
            if pin_data['func'] not in supported_pin_functions:
                raise ValueError('pin function is not supported: {}'.format(pin_data['func']))


def generate_file_name(component_data, generator_name):
    manufacturer_name = component_data['manufacturer'].replace(' ', '_')
    part = component_data['part'].replace('#', '')
    return f"{manufacturer_name}_{part}_{generator_name}"


def generate(data):
    generator_map = {'default': default_generator,
                     'rectangle': rectangular_symbol_generator,
                     'opamp': opamp_generator}

    validate(data)
    if 'symbol_generator' not in data:
        symbol = default_generator(data, {})
        filename = generate_file_name(data, 'generic')
        return [(symbol, filename)]
    else:
        symbols = []
        for generator in data['symbol_generator']:
            generator_data = data['symbol_generator'][generator]
            filename = generate_file_name(data, generator)
            symbol = generator_map[generator](data, generator_data)
            symbols.append((symbol, filename))
        return symbols


def export_symbol(symbol, filename):
    exporters = [svg_exporter]
    for exporter in exporters:
        exporter(symbol, filename)
