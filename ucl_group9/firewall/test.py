import os, inspect, sys, subprocess

# Those tests aren't totally pertinent and aren't discussed in the report, they were just usefull
# for some tests during the developpment of the firewall, they also need the limit on the echo-request
# to be ignored.

routers_ip = [
		"fd00:200:9:2100::",
		"fd00:200:9:2200::",
		"fd00:200:9:2300::",
		"fd00:200:9:2400::",
		"fd00:200:9:2500::",
		"fd00:200:9:2600::",
		"fd00:300:9:2100::",
		"fd00:300:9:2200::",
		"fd00:300:9:2300::",
		"fd00:300:9:2400::",
		"fd00:300:9:2500::",
		"fd00:300:9:2600::"
	]
routers_name = [
		"Halles",
		"SH1C",
		"Michotte",
		"Carnoy",
		"Stevin",
		"Pythagore"
	]
admin_ip = ["fd00:200:9:0300::1", "fd00:300:9:0300::1"]
admin_name = ["ART"]
visitor_ip = ["fd00:200:9:5600::1", "fd00:300:9:5600::1"]
visitor_name = ["GUI"]
student_ip = ["fd00:200:9:4500::1", "fd00:300:9:4500::1"]
student_name = ["LUC"]
staff_ip = ["fd00:200:9:1200::1", "fd00:200:9:1200::2", "fd00:300:9:1200::1", "fd00:300:9:1200::2"]
staff_name = ["SH1", "SH2"]
iot_ip = ["fd00:200:9:3400::1", "fd00:300:9:3400::1"]
iot_name = ["TOM"]
monitors_ip = [
		"fd00:200:9:2101::1", 
		"fd00:200:9:2401::1",
		"fd00:300:9:2101::1",
		"fd00:300:9:2401::1"
	]
monitors_name = ["MO1", "MO2"]
nss_ip = [
		"fd00:200:9:2101::2",
		"fd00:200:9:2401::2",
		"fd00:300:9:2101::2",
		"fd00:300:9:2401::2"
	]
nss_name = ["NS1", "NS2"]
extern_ip = ["2a00:1450:400e:80d::2004", "2a03:2880:f121:83:face:b00c:0:25de"]

	
def execute(command):
	p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	output, err = p.communicate()
	return output.decode("utf-8")
	

def is_good_ping(ping_res):
	ping_res = ping_res.split("\n")
	if len(ping_res) > 1 and "rtt" in ping_res[-2]:
		return True
	return False


def try_ping(src, dst, expected=True, debug_full=False):
	res = execute("sudo ip netns exec " + src + " ping6 -c 1 -W 1 " + dst)
	if is_good_ping(res) == expected:
		if debug_full and expected:
			print("[SUCCESS] " + src + " did succesfully ping " + dst + " !")
		elif debug_full:
			print("[SUCCESS] " + src + " was blocked succesfuly toward " + dst + " !")
		return True
	else:
		if expected:
			print("[FAILED] " + src + " should have ping " + dst + " but didn't")
		else:
			print("[FAILED] " + src + " shouldn't have ping " + dst + " but did")
		return False
	

class FirewallTest():
	
	def test_ping_routers_to_anyone(self):
		print("###################################")
		print("# Testing routers to routers ping #")
		print("###################################")
		dests = []
		dests.extend(routers_ip)
		dests.extend(admin_ip)
		dests.extend(visitor_ip)
		dests.extend(student_ip)
		dests.extend(staff_ip)
		dests.extend(iot_ip)
		dests.extend(monitors_ip)
		dests.extend(nss_ip)
		dests.extend(extern_ip)
		count = 0
		total = len(routers_name) * len(dests)
		for router_a in routers_name:
			for dest in dests:
				if try_ping(router_a, dest):
					count += 1
		dests = []
		total += len(routers_name) * len(dests)
		for student in student_name:
			for user in dests:
				if try_ping(student, user, False):
					count += 1
		print("\tSucceeded " + str(count) + "/" + str(total))
		print("")
				
	def test_ping_admin_to_anyone(self):
		print("###############################")
		print("# Testing traffic from admins #")
		print("###############################")
		dests = []
		dests.extend(routers_ip)
		dests.extend(admin_ip)
		dests.extend(visitor_ip)
		dests.extend(student_ip)
		dests.extend(staff_ip)
		dests.extend(iot_ip)
		dests.extend(monitors_ip)
		dests.extend(nss_ip)
		dests.extend(extern_ip)
		count = 0
		total = len(admin_name) * len(dests)
		for admin in admin_name:
			for user in dests:
				if try_ping(admin, user):
					count += 1
		print("\tSucceeded " + str(count) + "/" + str(total))
		print("")
	
	def test_ping_staff_to_anyone(self):
		print("##############################")
		print("# Testing traffic from staff #")
		print("##############################")
		dests = []
		dests.extend(routers_ip)
		dests.extend(admin_ip)
		dests.extend(staff_ip)
		dests.extend(nss_ip)
		dests.extend(extern_ip)
		dests.extend(iot_ip)
		count = 0
		total = len(student_name) * len(dests)
		for student in student_name:
			for user in dests:
				if try_ping(student, user):
					count += 1
		dests = []
		dests.extend(monitors_ip)
		dests.extend(visitor_ip)
		dests.extend(student_ip)
		total += len(student_name) * len(dests)
		for student in student_name:
			for user in dests:
				if try_ping(student, user, False):
					count += 1
		print("\tSucceeded " + str(count) + "/" + str(total))
		print("")
		
	def test_ping_student_to_anyone(self):
		print("#################################")
		print("# Testing traffic from students #")
		print("#################################")
		dests = []
		dests.extend(routers_ip)
		dests.extend(admin_ip)
		dests.extend(staff_ip)
		dests.extend(nss_ip)
		dests.extend(extern_ip)
		count = 0
		total = len(student_name) * len(dests)
		for student in student_name:
			for user in dests:
				if try_ping(student, user):
					count += 1
		dests = []
		dests.extend(iot_ip)
		dests.extend(monitors_ip)
		dests.extend(visitor_ip)
		dests.extend(student_ip)
		total += len(student_name) * len(dests)
		for student in student_name:
			for user in dests:
				if try_ping(student, user, False):
					count += 1
		print("\tSucceeded " + str(count) + "/" + str(total))
		print("")
		
	def test_ping_visitor_to_anyone(self):
		print("#################################")
		print("# Testing traffic from visitors #")
		print("#################################")
		dests = []
		dests.extend(routers_ip)
		dests.extend(admin_ip)
		dests.extend(nss_ip)
		count = 0
		total = len(visitor_name) * len(dests)
		for visitor in visitor_name:
			for user in dests:
				if try_ping(visitor, user):
					count += 1
		dests = []
		dests.extend(iot_ip)
		dests.extend(monitors_ip)
		dests.extend(visitor_ip)
		dests.extend(student_ip)
		dests.extend(staff_ip)
		dests.extend(extern_ip)
		total += len(visitor_name) * len(dests)
		for visitor in visitor_name:
			for user in dests:
				if try_ping(visitor, user, False):
					count += 1
		print("\tSucceeded " + str(count) + "/" + str(total))
		print("")
		
	def test_ping_iot_to_anyone(self):
		print("############################")
		print("# Testing traffic from iot #")
		print("############################")
		dests = []
		dests.extend(routers_ip)
		dests.extend(admin_ip)
		dests.extend(nss_ip)
		count = 0
		total = len(iot_name) * len(dests)
		for iot in iot_name:
			for user in dests:
				if try_ping(iot, user):
					count += 1
		dests = []
		dests.extend(iot_ip)
		dests.extend(monitors_ip)
		dests.extend(visitor_ip)
		dests.extend(student_ip)
		dests.extend(staff_ip)
		dests.extend(extern_ip)
		total += len(iot_name) * len(dests)
		for iot in iot_name:
			for user in dests:
				if try_ping(iot, user, False):
					count += 1
		print("\tSucceeded " + str(count) + "/" + str(total))
		print("")
			
if __name__ == '__main__':
	tests = FirewallTest()
	tests.test_ping_routers_to_anyone()
	tests.test_ping_admin_to_anyone()
	tests.test_ping_staff_to_anyone()
	tests.test_ping_student_to_anyone()
	tests.test_ping_visitor_to_anyone()
	tests.test_ping_iot_to_anyone()

