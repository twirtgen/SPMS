import tempfile
import os
from re import sub

import docker

REGISTRY = os.environ.get('REGISTRY', 'localhost:5000/')
# init docker client
client = docker.DockerClient(base_url='unix://var/run/docker.sock', version='auto')

def verify(tmpdir: str, plugin_name: str) -> str:

    plugin_dir = '%s/%s' % (tmpdir, plugin_name)
    failure = {}

    for pluglet in [i[:-2] for i in os.listdir(plugin_dir) if i[len(i)-2:] == '.c']:
        # convert C source code into LLVM IR bitcode
        try:
            # TODO : mount PQUIC somewhere
            result = client.containers.run(
                image='%sterminator2_llvm-3.4_compile_service' % REGISTRY,
                command='%s/%s' % (plugin_name, pluglet),
                volumes={
                    tmpdir: {'bind': '/mount', 'type': 'rw'},
                    plugin_dir: {'bind': '/output', 'type': 'rw'}
                }
            )
        except docker.errors.ContainerError as e:
            error_log = '[ERROR] <%s> : <%s> : %s' % (e.image, e.command, e.stderr.decode('utf-8'))
            failure[pluglet] = error_log
            print(error_log)
            continue

        print("LLVM-3.4 successfully finished")

        # convert LLVM IR bitcode to T2 instructions
        try:
            result = client.containers.run(
                image='%sterminator2_llvm2kittel_service' % REGISTRY,
                command=pluglet,
                volumes={plugin_dir: {'bind': '/mount', 'type': 'rw'}}
            )
        except docker.errors.ContainerError as e:
            error_log = '[ERROR] <%s> : <%s> : %s' % (e.image, e.command, e.stderr.decode('utf-8'))
            failure[pluglet] = error_log
            print(error_log)
            continue

        print("LLVM2KITTEL successfully finished")

        # perform some cleanup of the T2 instructions file. Sometimes LLVM2KITTEL produces files
        # with only one comment which means the program trivially ends. T2 is unable to handle 
        # such files so we remove all the comments and check for empty files, if it is the case,
        # T2 is not launched and the verification is successful.
        with open('%s/%s.t2' % (plugin_dir, pluglet), 'r') as fp:
            content = fp.read()
            new_content = sub('^///\*\*\* [0-9a-z_]* \*\*\*///\n', '', content)

        if not new_content.isspace():
            print('LLVM2KITTEL output is empty after cleanup.')
            continue

        with open('%s/%s.t2' % (plugin_dir, pluglet), 'w') as fp:
            content = fp.write(new_content)
        
        # execute T2 on previously generated instructions
        try:
            result = client.containers.run(
                image='%sterminator2_t2_service' % REGISTRY,
                command=pluglet,
                volumes={plugin_dir: {'bind': '/mount', 'type': 'rw'}}
            )

            if result != b'Termination proof succeeded\n':
                failure[pluglet] = result.decode('ascii')
            
            print('from terminator : %s' % result)

        except docker.errors.ContainerError as e:
            error_log = '[ERROR] <%s> : <%s> : %s' % (e.image, e.command, e.stderr.decode('utf-8'))
            failure[pluglet] = error_log
            print(error_log)
            continue

        print("T2 successfully finished")

    return None if len(failure) == 0 else failure
