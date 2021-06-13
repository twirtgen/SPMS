import tempfile
import tarfile
import shutil
import subprocess
import os

# picoquic expected into /tmp

def generate_binding(tar_archive, plugin):
    # creates temporary dir
    directory = tempfile.mkdtemp(dir='/tmp')
    pwd = os.getcwd()

    # untar plugin's archive into temporary directory
    with tarfile.open(fileobj=tar_archive, mode='r:bz2') as tar:
        tar.extractall(path=directory)

    # produce BPF bytecode
    os.chdir('%s/%s' % (directory, plugin))
    subprocess.run(['make'], env={'CLANG': 'clang', 'LLC': 'llc'})

    # load pluglets to store in binding
    # TODO : call manifest's parser
    manifest_file = '%s.plugin' % plugin.split('.')[-1]
    manifest = open(manifest_file).read()
    pluglets = [line.split(' ')[-1] for line in manifest.split('\n')[1:]]

    # get available binaries
    binaries = [i for i in os.listdir() if i[len(i)-2:] == '.o']

    # generate binding of <plugin>
    binding = tarfile.open(name='%s.binding' % plugin, mode='w', format=tarfile.GNU_FORMAT)
    binding.add(manifest_file)
    for pluglet in pluglets:
        if pluglet in binaries:
            binding.add(pluglet)
        else:
            # TODO : handle error
            pass
    binding.close()

    # binding has been dumped into tar archive, load it into buffer to return it
    binding = open('%s.binding' % plugin, 'rb')

    os.chdir(pwd)

    # remove temporary directory
    shutil.rmtree(directory)

    return binding
