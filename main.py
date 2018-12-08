#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import tableauserverclient as tsc
import json
import os
import sys

if (not os.path.exists("/data/config.json")) and (not os.path.exists("/code/config.json")):
	print("Cannot run without configuration")
	sys.exit(0)

with open("/data/config.json" if os.path.exists("/data/config.json") else "/code/config.json", "r") as conf_file:
	conf = json.load(conf_file)["parameters"]


auth = tsc.TableauAuth(conf["user"], conf["#pass"])
server = tsc.Server(conf["server"])

with server.auth.sign_in(auth):
    datasources, pitem = server.datasources.get()
    print("\nThere are {} datasources on site: ".format(pitem.total_available))
    print([datasource.name for datasource in datasources])