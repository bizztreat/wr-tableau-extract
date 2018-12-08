#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import tableauserverclient as tsc
import json
import os
import sys
import time
from xml.etree import ElementTree as ET

conf_path = ("/data/config.json" if os.path.exists("/data/config.json") else ("/code/config.json" if os.path.exists("/code/config.json") else "config.json"))


if (not os.path.exists(conf_path)):
	print("Cannot run without configuration")
	sys.exit(0)

with open(conf_path, "r") as conf_file:
	conf = json.load(conf_file)["parameters"]


auth = tsc.TableauAuth(conf["user"], conf["#pass"])
server = tsc.Server(conf["server"])

with server.auth.sign_in(auth):
	# use server API version
	server.use_server_version()
	
	followed_tasks = {}
	
	# tasks
	tasks, pitem = server.tasks.get()
	for task in tasks:
		if task.target.type!="datasource": continue
		ds = server.datasources.get_by_id(task.target.id)
		refresh_type = ("increment" if "increment" in task.task_type.lower() else "full")
		if ds.name in conf["datasources"] and refresh_type==conf["type"]:
			print("Starting {0} refresh of {1}".format(refresh_type,ds.name))
			response = server.tasks.run(task)
			root = ET.fromstring(response)
			for chld in root:
				print(chld.tag,chld.attrib)
			followed_tasks[ds] = task
			#sched = server.schedules.get()
			#print(sched)
	
	while True:
		time.sleep(5)
		for ds in followed_tasks:
			t = server.tasks.get_by_id(followed_tasks[ds].id)
			print("{0} is currently {1}".format(ds,t.state))