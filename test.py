
import os
import yaml
import subprocess as sub
from collections import OrderedDict




#!/usr/bin/env python
try:
	# for python newer than 2.7
    from collections import OrderedDict
except ImportError:
	# use backport from pypi
    from ordereddict import OrderedDict

import yaml

# try to use LibYAML bindings if possible
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from yaml.representer import SafeRepresenter
_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


def dict_representer(dumper, data):
    return dumper.represent_dict(data.iteritems())


#def dict_constructor(loader, node):
    #return OrderedDict(loader.construct_pairs(node))

Dumper.add_representer(OrderedDict, dict_representer)
#Loader.add_constructor(_mapping_tag, dict_constructor)

Dumper.add_representer(str,
                       SafeRepresenter.represent_str)

#Dumper.add_representer(unicode,
                       #SafeRepresenter.represent_unicode)





def get_data_from_yaml(filepath):
    """
    Get dictionary out of yaml file and return it.

    - **parameters**, **types**, **return** and **return types**::

	  :param filepath: Yaml file path
	  :type filepath: String
	  :return: Returns data of yaml file as dictionary
	  :rtype: dictionary
    """
    if os.path.exists(filepath):
	with open(filepath, 'r') as yaml_file:
	    data = yaml.load(yaml_file)
	return data
    else:
	raise Exception("file does not exists")
def dump_data_into_yaml(filepath, data, mode="w"):
    """
    Get dictionary out of yaml file and return it.

    - **parameters**, **types**, **return** and **return types**::

          :param filepath: Yaml file path
          :param data: Data which needs to be added into Yaml file
          :param mode: In which mode file should be opened.
          :type filepath: String
          :type data: Dictionary
          :type mode: String
    """
    with open(filepath, mode) as yamlfile:

	yaml.dump(data, yamlfile, Dumper = Dumper)
	#yaml.safe_dump(data, yamlfile,)
	#yaml.dump(data)

def execute(command):
    """
	Generic method to execute command
    """
    process = sub.Popen([command], stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE, shell =True)
    process.stdin.write('Y')
    stdoutput, stderror = process.communicate()
    if stderror:
	return stderror
    else:
	return stdoutput

path = 'inventory.yaml'
#data = get_data_from_yaml(filepath)
#import pdb;pdb.set_trace()
#cmd = "ansible all -m setup | grep -i ansible_os_family"
inventory = get_data_from_yaml(path)
for item in inventory:
    hosts = item['hosts']
    filepath = item['inventory_file_path']
    repo = item['repository']
    conf = get_data_from_yaml(filepath)
    softwares = conf['softwares']
    patches = conf['patches']
    configurations = conf['configurations']
    host_file =  filepath.split('/')[-1][:-5]
    host_info = ''
    for host in hosts:
	host_info = host_info  + host['ip'] + '\t' +'ansible_ssh_user='+ host['user'] + '\t' +'ansible_ssh_pass='+ host['pwd'] + '\n'
    host_info='[' + host_file + ']\n' + host_info
    with open('hosts','w') as fp:
	fp.write(host_info)

    soft_wares = []
    for sw in softwares:
	sw_dict = OrderedDict([('name', "Installing " + sw), ('package', OrderedDict([('name', sw), ('state', 'present')]))])
	soft_wares.append(sw_dict)
    play_book = OrderedDict([('hosts', host_file), ('become', 'yes'), ('tasks', soft_wares), ])
    #play_book.update(OrderedDict({'tasks': soft_wares,}))
    play_book_list = [play_book]
    pb_name="{}playbook.yaml".format(host_file)
    dump_data_into_yaml(pb_name, play_book_list)


cmd = "ansible-playbook {}".format(pb_name)
#execute(cmd)
os.system(cmd)

#'name=' + sw + ' state=present'
    #import pdb;pdb.set_trace()











