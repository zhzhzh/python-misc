from jinja2 import Template
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('tpl.html')

print(template.render(rows=['tt', 'bb']))
