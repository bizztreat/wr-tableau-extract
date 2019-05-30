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

print("Connecting to server {0} using username \'{1}\'".format(conf["server"],conf["user"]))

with server.auth.sign_in(auth):
	print("Connection established.")
	# use server API version
	server.use_server_version()
	
	server_info = server.server_info.get()
	print("Server REST API version: {0}".format(server_info.rest_api_version))
	if (server_info.rest_api_version < '3.1'):
		nopoll_mode = True
		print("Running in no-poll mode, only servers using REST API version 3.1 and higher support that.")
	else:
		nopoll_mode = False
		print("Running in poll mode.")
		
	followed_tasks = {}
	
	print("Getting tasks list.")
	# tasks
	tasks, pitem = server.tasks.get()
	for task in tasks:
		if task.target.type!="datasource": continue
		ds = server.datasources.get_by_id(task.target.id)
		refresh_type = ("increment" if "increment" in task.task_type.lower() else "full")
		if ds.name in conf["datasources"] and refresh_type==conf["type"]:
			print("Starting {0} refresh of {1}".format(refresh_type,ds.name))
			response = ""
			response = server.tasks.run(task)
			if not nopoll_mode:
				try: root = ET.fromstring(response)
				except Exception as m:
					print("Error parsing response the refresh task might not have been run, no way to know :/.\nSkipping poll-check for datasource {0}\nOriginal error: {1}".format(ds.name,str(m)))
					continue
				for chld in root:
					try:
						jid = chld.attrib["id"]
						followed_tasks[ds.name] = jid
					except Exception as e:
						print("Job not found, skipping poll-check for datasource \'{0}\'.".format(ds.name))
				#sched = server.schedules.get()
				#print(sched)
	if nopoll_mode or len(followed_tasks.keys()):
		print("Nothing to poll or nowhere to poll from. Finished.")
		sys.exit(0)
	print("Continue in poll mode")
	while True:
		time.sleep(5)
		for ds in followed_tasks:
			#j = server.jobs.get_by_id(followed_tasks[ds])
			#print(dir(j))
			print("I would normally poll job for datasource {0}, but this is only a debug.".format(ds))