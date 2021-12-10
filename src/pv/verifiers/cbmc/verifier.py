import tempfile
import os

import docker

# init docker client
client = docker.DockerClient(base_url='unix://var/run/docker.sock', version='auto')
REGISTRY = os.environ.get('REGISTRY', 'localhost:5000/')

def verify(logger, tmpdir: str, plugin_name: str) -> str:

    plugin_dir = '%s/%s' % (tmpdir, plugin_name)
    failure = {}

    for pluglet in [i[:-2] for i in os.listdir(plugin_dir) if i[len(i)-2:] == '.c']:
        logger.info('<cbmc> <%s:%s> Processing pluglet' % (plugin_name, pluglet))
        try:
            result = client.containers.run(
                image='%scbmc_cbmc_service' % REGISTRY,
                command='%s %s' % (plugin_name, pluglet),
                volumes={
                    tmpdir: {'bind': '/mount', 'type': 'rw'},
                },
                stdout=True,
                stderr=True
            )
            log = result.decode('utf-8')
            success = 'VERIFICATION SUCCESSFUL' in log
            if not success:
                failure[pluglet] = log
                logger.error('<cbmc> <%s:%s> %s.' % (plugin_name, pluglet, log))
            else:
                logger.info('<cbmc> <%s:%s> Pluglet successfully processed.' % (plugin_name, pluglet))

        except docker.errors.ContainerError as e:
            error_log = '<%s> : <%s> : %s' % (e.image, e.command, e.stderr.decode('utf-8'))
            failure[pluglet] = error_log
            logger.error(error_log)

    return None if len(failure) == 0 else failure
