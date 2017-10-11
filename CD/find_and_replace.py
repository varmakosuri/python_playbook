import os, sys
import fileinput
import yaml
import ast

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
    V=str(Variable)
    S=str(Setting)
    # use quotes if setting has spaces #
    if ' ' in S:
        S = '"%s"' % S

    for line in fileinput.input(File, inplace = 1):
        # process lines that look like config settings #
        if not line.strip().startswith('#') and line.strip() or '=' in line.strip() or ':' in line.strip() or ' ' in line.strip():
            #import pdb;pdb.set_trace()
	    if '=' in line:
		_infile_var = str(line.split('=')[0].strip())
		_infile_set = str(line.split('=')[1].strip())
		split_str = '='
	    elif ':' in line:
		_infile_var = str(line.split(':')[0].strip())
		_infile_set = str(line.split(':')[1].strip())
		split_str = ':'
	    elif ' ' in line:
		_infile_var = str(line.split()[0].strip())
		_infile_set = str(line.split()[1].strip())
            # only change the first matching occurrence #
            if VarFound == False and _infile_var.strip(' ') == V:
                VarFound = True
                # don't change it if it is already set #
                if _infile_set.strip(' ') == S:
                    AlreadySet = True
                else:
		    if split_str == '=':
			line = "%s = %s\n" % (V, S)
		    elif split_str == ':':
			line = "%s : %s\n" % (V, S)
		    else:
			line = "%s  %s\n" % (V, S)
        sys.stdout.write(line)

    # Append the variable if it wasn't found #
    if not VarFound:
        print "Variable '%s' not found.  Adding it to %s" % (V, File)
        with open(File, "a") as f:
            f.write("%s = %s\n" % (V, S))
    elif AlreadySet == True:
        print "Variable '%s' unchanged" % (V)
    else:
        print "Variable '%s' modified to '%s'" % (V, S)

    return
def main():
    if sys.argv:
	var_dict = ast.literal_eval(sys.argv[1])
	filepath = var_dict.get('filepath')
	var_dict.pop('filepath')
    else:
	print "arguments are not passed"
    for k, v in var_dict.items():
	ModConfig(filepath, k, v)

if __name__ == '__main__':
    main()
