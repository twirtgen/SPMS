import tempfile
import os

import docker

# init docker client
client = docker.DockerClient(base_url='unix://var/run/docker.sock', version='auto')
REGISTRY = os.environ.get('REGISTRY', 'localhost:5000/')
print(REGISTRY)

def verify(tmpdir: str, plugin_name: str) -> str:

    plugin_dir = '%s/%s' % (tmpdir, plugin_name)
    failure = {}

    for pluglet in [i[:-2] for i in os.listdir(plugin_dir) if i[len(i)-2:] == '.c']:
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

        except docker.errors.ContainerError as e:
            error_log = '[ERROR] <%s> : <%s> : %s' % (e.image, e.command, e.stderr.decode('utf-8'))
            failure[pluglet] = error_log
            print(error_log)

    return None if len(failure) == 0 else failure
