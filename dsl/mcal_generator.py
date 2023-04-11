import os
from posixpath import dirname
import jinja2
from textx.metamodel import metamodel_from_file

this_folder = '.'

mcal_metamodel = metamodel_from_file('mcal.tx', debug=False)


def mcal_generator():
    "Generate vFLS from MCAL model."

    def format_hex(value):
        return f'0x{value:x}'

  # Initialize the template engine.
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader( os.path.join(this_folder, 'templates')),
        trim_blocks=True,
        lstrip_blocks=True)

    jinja_env.filters['format_hex'] = format_hex

    # Create model for vFLS
    mcal_model = mcal_metamodel.model_from_file('mcal.config')
    # Generate Java code
    for module in mcal_model.module:
    # generate C code first
        # Load C template
        template = jinja_env.get_template('%s.c_template'% module.name)
         # For each entity generate java file
        with open(os.path.join('..', 'src_gen',
                      "%s.c" % module.name), 'w') as f:
            f.write(template.render(module=module))
    # generate python code
        # Load the Py template
        template = jinja_env.get_template('%s.p_template'% module.name)
         # For each entity generate java file
        with open(os.path.join('..', 'src_gen',
                      "%s.py" % module.name), 'w') as f:
            f.write(template.render(module=module))

mcal_generator()