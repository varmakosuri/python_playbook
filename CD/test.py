import os
import yaml
import subprocess as sub
try:
	# for python newer than 2.7
    from collections import OrderedDict
except ImportError:
	# use backport from pypi
    from ordereddict import OrderedDict

# try to use LibYAML bindings if possible
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from yaml.representer import SafeRepresenter
_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
def dict_representer(dumper, data):
    return dumper.represent_dict(data.iteritems())

Dumper.add_representer(OrderedDict, dict_representer)
Dumper.add_representer(str, SafeRepresenter.represent_str)


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

def gen_host_file(filepath, hosts):
    """
    Genarates host file with given host inforamation in inventory.yaml file.

    - **parameters**, **types**, **return** and **return types**::

          :param filepath: Yaml file path
          :param data: Data which needs to be added into Yaml file
          :param mode: In which mode file should be opened.
          :type filepath: String
          :type data: Dictionary
          :type mode: String
    """
    host_file =  filepath.split('/')[-1][:-5]
    host_info = ''
    for host in hosts:
	host_info = host_info  + host['ip'] + '\t' +'ansible_ssh_user='+ host['user'] + '\t' +'ansible_ssh_pass='+ host['pwd'] + '\n'
    host_info='[' + host_file + ']\n' + host_info
    with open('hosts','w') as fp:
	fp.write(host_info)
    return host_file

def main():
    path = 'inventory.yaml'
    inventory = get_data_from_yaml(path)
    for item in inventory:
	hosts = item['hosts']
	filepath = item['inventory_file_path']
	repo = item['repository']
	conf = get_data_from_yaml(filepath)
	softwares = conf['softwares']
	patches = conf['patches']
	configurations = conf['configurations']
	host_file = gen_host_file(filepath, hosts)
	soft_wares = []

	for sw in softwares:
	    if isinstance(sw, dict):
		for k, v in sw.items():
		    sw_dict = OrderedDict([('name', "Installing " + k), ('package', OrderedDict([('name', k), ('state', 'present')]))])
		    soft_wares.append(sw_dict)
		    for ser in v:
			if 'enabled' in ser:
			    if ser['enabled'] == True:
				enabled = 'yes'
			    else:
				enabled = 'no'
			    sw_dict = OrderedDict([('name', ser['state'][:-2].capitalize() + "ing... " + ser['service_name'] + " service."), ('service', OrderedDict([('name', ser['service_name']), ('state', ser['state']), ('enabled', enabled)]))])
			    soft_wares.append(sw_dict)

			else:
			    sw_dict = OrderedDict([('name', ser['state'][:-2].capitalize() + "ing... " + ser['service_name'] + " service."), ('service', OrderedDict([('name', ser['service_name']), ('state', ser['state'])]))])
			    soft_wares.append(sw_dict)
	    else:
		sw_dict = OrderedDict([('name', "Installing " + sw), ('package', OrderedDict([('name', sw), ('state', 'present')]))])
		soft_wares.append(sw_dict)

	count = 0
	for conf in configurations:
	    if isinstance(conf, dict):
		src_filepath = conf.get('filepath')
		filepath = conf.get('filepath').split('/')[-1]
		vars_dict = conf.get('vars')
		test_dict = OrderedDict()
		test_dict.update([('filepath', filepath)])
		for k, v in vars_dict.items():
		    test_dict.update([(k,v)])
		sw_dict = OrderedDict([('name', "fetching the file from remote host "), ('fetch', OrderedDict([('src', src_filepath), ('dest', '/etc/ansible/CD/'), ('flat', 'yes')]))])
		soft_wares.append(sw_dict)
		dicts = 'dict{}'.format(count)
		sw_dict = OrderedDict([('set_fact',  OrderedDict([(dicts, test_dict)]))])
		soft_wares.append(sw_dict)
		sw_dict = OrderedDict([('command', 'sudo python /etc/ansible/CD/find_and_replace.py "{{'+dicts+'}}"')])
		soft_wares.append(sw_dict)
		sw_dict = OrderedDict([('name', "copying the file to remote host "), ('copy', OrderedDict([('src', '/etc/ansible/CD/' + filepath), ('dest', src_filepath)]))])
		soft_wares.append(sw_dict)
		count = count + 1

	play_book = OrderedDict([('hosts', host_file), ('become', 'yes'), ('tasks', soft_wares), ])
	play_book_list = [play_book]
	pb_name="{}playbook.yaml".format(host_file)
	dump_data_into_yaml(pb_name, play_book_list)
    cmd = "ansible-playbook {}".format(pb_name)
    os.system(cmd)

if __name__ == "__main__":
    main()
