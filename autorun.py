import os

try:
	service = "meteostation"
	path = os.path.abspath(".")
	user = os.getlogin()

	with open("/lib/systemd/system/{}.service".format(service), "w") as f:
		text = "[Unit]\n" \
		       "Description=Meteostation Service\n" \
		       "[Service]\n" \
		       "WorkingDirectory={}\n" \
		       "Type=idle\n" \
		       "User={}\n" \
		       "ExecStart=/usr/bin/python3 {}/main.py\n" \
		       "[Install]\n" \
		       "WantedBy=multi-user.target".format(path, user, path)

		f.write(text)
		print('{}.service was successfully created'.format(service))
		os.system("sudo chmod 644 /lib/systemd/system/{}.service".format(service))
		os.system("sudo systemctl daemon-reload")
		#os.system("sudo systemctl enable {}.service".format(service))
		#os.system("sudo systemctl start {}.service".format(service))
		#os.system("sudo systemctl status {}.service".format(service))
		raise SystemExit
except PermissionError as e:
	print(e.args, "Execute: sudo python3 autorun.py")
except Exception as e:
	print(e)

