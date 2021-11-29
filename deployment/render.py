#! /usr/bin/python3

# Ignore missing doc
# pylint: disable=C0114, C0116

from os import getcwd, environ, listdir
from copy import deepcopy
from json import load
from re import sub
from sys import argv

from jinja2 import Environment, FileSystemLoader

CERTS = ['pv', 'root_ca', 'pr']
SRC_DIR = '%s/../src' % getcwd()

# We dump all the filled templates in RAM as they are volatile files
DST_DIR = '/dev/shm/build'
UTILS =  [i for i in listdir('%s/util' % SRC_DIR) if i not in ['__pycache__', '__init__.py']]
BASE_LAYERS = listdir('../src/common_layers')

ENV = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)

def render_containerfiles(context, kind):
    for service in context['services']:

        # Load service configuration file
        with open('%s/%s/%s/config.json' % (context['src_dir'], kind, service), 'r') as config_fd:
            config = load(config_fd)

        # Prepare Dockerfile template context
        ctx = {}

        # Set µservice src directory
        ctx['service_dir'] = 'pv/%s' % service
        ctx['util_dir'] = 'util'

        # Set registry if any
        if 'REGISTRY' in context:
            ctx['registry'] = context['registry']

        # Set base_layer of the µservice
        ctx['base_layer'] = '%s_layer' % config['layer'] if config['layer'] in BASE_LAYERS else ''
        ctx['pkg_manager'] = 'DEBIAN_FRONTEND=noninteractive apt-get install -y' if 'ubuntu' in config['layer'] else 'apk add'

        # Set container CMD
        ctx['cmd'] = ''

        # Set utils scripts to copy in the container
        if 'utils' in config:
            ctx['utils'] = ['%s.py' % util for util in config['utils'] if '%s.py' % util in context['utils']]
            if 'load_cert' in config['utils']:
                ctx['cmd'] = 'python3 %s/load_cert.py && ' % ctx['util_dir']

        ctx['cmd'] += 'PYTHONUNBUFFERED=TRUE gunicorn -b 0.0.0.0:80 pv.%s.api:app' % service

        if 'packages' in config:
            ctx['packages'] = ' '.join(config['packages'])

        # Load template and render it
        template = ENV.get_template('%s/templates/layer.template' % kind)
        result = template.render(ctx)

        # Dump filled template
        layer_dump = '%s/%s_service.containerfile' % (DST_DIR, service)
        with open(layer_dump, 'w') as layer_fd:
            layer_fd.write(result)


def render_makefile(kind, context):

    # Update context with makefile specific variables
    context['builder'] = environ['BUILDER'] if 'BUILDER' in environ else 'buildah'
    context['cmd'] = 'bud --layers' if context['builder'] == 'buildah' else 'build'
    if 'REGISTRY' in environ:
        context['registry'] = environ['REGISTRY']

    # tmp fix to have 'python' layer first for common_layer
    tmp = ['build_%s_service' % name for name in context['services']]
    context['build_services'] = ' '.join(tmp)

    # Prepare verifiers
    if kind == 'pv':
        context['verifiers'] = [i for i in listdir('%s/pv/verifiers' % SRC_DIR) if i != 'controller.py']
        context['build_verifiers'] = ' '.join(['build_%s_verifier' % name for name in context['verifiers']])

        context['vservices'] = {}
        for verifier in context['verifiers']:
            containers = ['.'.join(i.split('.')[:-1]) for i in listdir('%s/pv/verifiers/%s' % (SRC_DIR, verifier)) if '.containerfile' in i]
            try:
                containers.remove('verifier')
            except ValueError:
                pass
            if len(containers) > 0:
                context['vservices'][verifier] = containers

    # Get makefile's template and render it
    template = ENV.get_template('%s/templates/makefile.template' % kind)
    result = template.render(context)

    # Dump makefile
    with open('%s/%s.makefile' % (DST_DIR, kind), 'w') as makefile_fd:
        makefile_fd.write(result)


def render(kind):
    context = {
        'src_dir': SRC_DIR,
        'services': [i for i in listdir('%s/%s' % (SRC_DIR, kind)) if i not in ['__pycache__', 'verifiers']],
        'utils': UTILS
    }

    # TEMP
    # Currently common_layers and pr containerfiles are hardcoded in src
    if kind == 'pv':
        render_containerfiles(context, kind)

    render_makefile(kind, context)


if __name__ == '__main__':
    render('common_layers')
    render('pv')
    render('pr')

