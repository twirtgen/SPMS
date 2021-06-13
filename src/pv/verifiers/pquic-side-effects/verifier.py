import tempfile
import os

import docker

# init docker client
client = docker.DockerClient(base_url='unix://var/run/docker.sock', version='auto')

BMC = os.environ['BMC'] if 'BMC' in os.environ else 'mono'

def verify(tmpdir: str, plugin_name: str) -> str:

    plugin_dir = '%s/%s' % (tmpdir, plugin_name)
    failure = {}

    for pluglet in [i[:-2] for i in os.listdir(plugin_dir) if i[len(i)-2:] == '.c']:
        # convert C source code into LLVM IR bitcode
        try:
            result = client.containers.run(
                image='pquic-formal_seahorn_service',
                command='%s %s' % (plugin_name, pluglet),
                volumes={
                    tmpdir: {'bind': '/mount', 'type': 'rw'},
                },
                environment={
                    'BMC': BMC
                }
            )
            log = result.decode('utf-8')
            #unsat = log.split('\n')[-2] == 'unsat'
            unsat = 'unsat' in log
            if not unsat:
                failure[pluglet] = log

        except docker.errors.ContainerError as e:
            error_log = '[ERROR] <%s> : <%s> : %s' % (e.image, e.command, e.stderr.decode('utf-8'))
            failure[pluglet] = error_log
            print(error_log)

    return None if len(failure) == 0 else failure
