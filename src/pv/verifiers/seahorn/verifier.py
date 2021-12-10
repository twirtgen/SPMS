import tempfile
import os

import docker

# init docker client
client = docker.DockerClient(base_url='unix://var/run/docker.sock', version='auto')

BMC = os.environ['BMC'] if 'BMC' in os.environ else 'mono'
REGISTRY = os.environ.get('REGISTRY', 'localhost:5000/')

def verify(logger, tmpdir: str, plugin_name: str) -> dict:

    plugin_dir = os.path.join(tmpdir, plugin_name)
    failure = {}

    for pluglet in [i[:-2] for i in os.listdir(plugin_dir) if i[len(i)-2:] == '.c']:
        logger.info('<seahorn> <%s:%s> Processing pluglet.' % (plugin_name, pluglet))
        try:
            result = client.containers.run(
                image='%sseahorn_seahorn_service' % REGISTRY,
                command='%s %s' % (plugin_name, pluglet),
                volumes={
                    tmpdir: {'bind': '/mount', 'type': 'rw'},
                },
                environment={
                    'BMC': BMC
                },
                stdout=True,
                stderr=True
            )
            log = result.decode('utf-8')
            unsat = 'unsat' in log
            if not unsat:
                failure[pluglet] = log
                logger.error('<seahorn> <%s:%s> %s' % (plugin_name, pluglet, log))
            else:
                logger.info('<seahorn> <%s:%s> Successfully processed.' % (plugin_name, pluglet))

        except docker.errors.ContainerError as e:
            error_log = '<%s> <%s:%s> %s' % (e.image, plugin_name, e.command, e.stderr.decode('utf-8'))
            failure[pluglet] = error_log
            logger.error(error_log)

    return None if len(failure) == 0 else failure
