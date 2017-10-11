import os, sys
import fileinput
import yaml

def get_data_from_yaml(filepath):
    if os.path.exists(filepath):
	with open(filepath, 'r') as yaml_file:
	    data = yaml.load(yaml_file)
	return data
    else:
	raise Exception("file does not exists")

def ModConfig(File, Variable, Setting):
    """
    Modify Config file variable with new setting
    """
    VarFound = False
    AlreadySet = False
