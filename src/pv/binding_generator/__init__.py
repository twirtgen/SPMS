import subprocess
import tempfile
import tarfile
import shutil
import io
import os
import json

import cbor

def parse_manifest(manifest_path: str) -> dict:
    """ Takes the path toward a manifest and outputs a dict of plugins
    """
    with open(manifest_path, 'r') as fd:
        manifest = json.load(fd)
    return {plugin: [obj_content['obj'] for obj_name, obj_content in content['obj_code_list'].items()] for plugin, content in manifest['plugins'].items()}

def generate_binding(tar_archive: bytes, plugin: str) -> list:
    """ Takes a tar.bz2 compressed archive containing a plugin's source 
    code and outputs the plugin binding
    """

    """ Create temporary directory serving as compilation root """
    tmp_dir = tempfile.mkdtemp(dir='/tmp')

    """ Decompress plugin's source code in the temporary directory """
    with io.BytesIO(tar_archive) as tar_stream:
        with tarfile.open(fileobj=tar_stream, mode='r:bz2') as tar:
            tar.extractall(path=tmp_dir)

    """ Compile plugin """
    plugin_dir = os.path.join(tmp_dir, plugin)
    subprocess.run(['make', '-C', plugin_dir])

    """ Generate plugin's binding """
    manifest_path = os.path.join(plugin_dir, 'manifest.json')
    plugins = parse_manifest(manifest_path)
    binaries = [i for i in os.listdir(plugin_dir) if i[len(i)-2:] == '.o']

    out_plugins = []
    for plugin, pluglets in plugins.items():
        binding_name = '%s.binding' % plugin 
        binding_path = os.path.join(plugin_dir, binding_name)
        with open(manifest_path, 'rb') as fd:
            binding = {'manifest': fd.read()}
        
        for pluglet in pluglets:
            if pluglet in binaries:
                with open(os.path.join(plugin_dir, pluglet), 'rb') as pluglet_fd:
                    binding[pluglet] = pluglet_fd.read()
            else:
                # TODO: handle error
                pass

        out_plugins.append(cbor.dumps(binding))

    """ Cleanup """
    shutil.rmtree(tmp_dir)

    return out_plugins[0]

if __name__ == '__main__':
    plugin = "hello_world"
    tarfile_name = "%s.tar.bz2" % plugin
    with open(tarfile_name, 'rb') as fd:
        binding = generate_binding(fd.read(), plugin)
        print(binding)
