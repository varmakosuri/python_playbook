import re
def IPvar(var):
	if var==re.findall("[/d{0-3}./d{0-3}./d{0-3}./d{0-3}]",var):
		print "ip is valid"
	else:
		print "invalid"
IPvar(var=raw_input("enter theip addr"))
