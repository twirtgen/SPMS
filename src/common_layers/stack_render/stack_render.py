#! /usr/bin/python3

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from json import load, dumps
from os import getcwd, listdir

with open('/tmp/stack.config') as fp:
    config = load(fp)

if 'type' not in config or config['type'] not in ['pv', 'pr']:
    exit(1)

context = {}

if config['type'] == 'pv':
    try:
        context['exp'] = config['exp']
    except KeyError:
        pass

    try:
        context['verifiers'] = {key: value['verifier'] for key, value in config['verifiers'].items()}
        context['verifier_list'] = dumps(list(config['verifiers'].keys()))
    except KeyError:
        print('Config malformed: <verifiers> not found')
        exit(1)

env = Environment(loader=FileSystemLoader('/cwd'))

try:
    template = env.get_template('%s.template' % config['type'])
    result = template.render(context)

    with open('/output/docker-compose.yml', 'w') as fp:
        fp.write(result)

except TemplateNotFound:
    print('Template not found <%s>' % path)
    exit(1)


