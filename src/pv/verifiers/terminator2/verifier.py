import tempfile
import os
from re import sub

import docker

REGISTRY = os.environ.get('REGISTRY', 'localhost:5000/')
# init docker client
client = docker.DockerClient(base_url='unix://var/run/docker.sock', version='auto')

def verify(logger, tmpdir: str, plugin_name: str) -> str:

    plugin_dir = '%s/%s' % (tmpdir, plugin_name)
    failure = {}

    for pluglet in [i[:-2] for i in os.listdir(plugin_dir) if i[len(i)-2:] == '.c']:
        # convert C source code into LLVM IR bitcode
        logger.info('<llvm-3.4> <%s:%s> Processing pluglet.' % (plugin_name, pluglet))
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
            error_log = '<%s> <%s:%s> %s' % (e.image, plugin_name, e.command, e.stderr.decode('utf-8'))
            failure[pluglet] = error_log
            logger.error(error_log)
            continue
        logger.info('<llvm-3.4> <%s:%s> Successfully processed.' % (plugin_name, pluglet))

        # convert LLVM IR bitcode to T2 instructions
        logger.info('<llvm2kittel> <%s:%s> Processing pluglet.' % (plugin_name, pluglet))
        try:
            result = client.containers.run(
                image='%sterminator2_llvm2kittel_service' % REGISTRY,
                command=pluglet,
                volumes={plugin_dir: {'bind': '/mount', 'type': 'rw'}}
            )
        except docker.errors.ContainerError as e:
            error_log = '<%s> <%s:%s> %s' % (e.image, plugin_name, e.command, e.stderr.decode('utf-8'))
            failure[pluglet] = error_log
            logger.error(error_log)
            continue
        logger.info('<llvm2kittel> <%s:%s> successfully processed.' % (plugin_name, pluglet))

        # perform some cleanup of the T2 instructions file. Sometimes LLVM2KITTEL produces files
        # with only one comment which means the program trivially ends. T2 is unable to handle 
        # such files so we remove all the comments and check for empty files, if it is the case,
        # T2 is not launched and the verification is successful.
        logger.info('<llvm2kittel> <%s:%s> Post-processing pluglet.' % (plugin_name, pluglet))
        with open('%s/%s.t2' % (plugin_dir, pluglet), 'r') as fp:
            content = fp.read()
            new_content = sub('^///\*\*\* [0-9a-z_]* \*\*\*///\n', '', content)

        if new_content.isspace() or new_content == '':
            logger.info('<llvm2kittel> <%s:%s> Output is empty after cleanup.' % (plugin_name, pluglet))
            continue

        with open('%s/%s.t2' % (plugin_dir, pluglet), 'w') as fp:
            content = fp.write(new_content)
        logger.info('<llvm2kittel> <%s:%s> Successfully post-processed.' % (plugin_name, pluglet))
        
        # execute T2 on previously generated instructions
        logger.info('<terminator2> <%s:%s> Processing pluglet.' % (plugin_name, pluglet))
        try:
            result = client.containers.run(
                image='%sterminator2_t2_service' % REGISTRY,
                command=pluglet,
                volumes={plugin_dir: {'bind': '/mount', 'type': 'rw'}}
            )

            if not result.contains(b'Termination proof succeeded\n'):
                failure[pluglet] = result.decode('ascii')
                logger.error('<terminator2> <%s:%s> %s' % (plugin_name, pluglet, failure[pluglet]))
            else:
                logger.info('<terminator2> <%s:%s> Successfully processed.' % (plugin_name, pluglet))

        except docker.errors.ContainerError as e:
            error_log = '<%s> <%s:%s> %s' % (e.image, plugin_name, e.command, e.stderr.decode('utf-8'))
            failure[pluglet] = error_log
            logger.error(error_log)
            logger.error(new_content)
            continue

    return None if len(failure) == 0 else failure
