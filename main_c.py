import serial
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import json
import cgi
from logzero import logger
from pathlib import Path
from datetime import datetime
import multiprocessing as mp
import csv
# parallel save data into mongo db
# send them on server every 24 hours

# config
script_path = Path(__file__, '..').resolve()
path_config = 'config.json'

# server ip
server_host = "localhost"
server_port = 8015

# serial port
serial_port = "/dev/ttyS0"
serial_spd = 115200
timeout = 1
command = "GET\r\n"

# logger
logData = {
	'logPath': 'logs',
	'logMaxBytes': 1000000,
	"logBackupCount": 3,
}

# station name
station_name = "test station"

def get_data():
	ser = serial.Serial(serial_port, serial_spd, timeout=timeout)
	try:
		ser.close()
		ser.open()
		# logger.info('start on port: {}'.format(serial_port))
		while ser.isOpen():
			time.sleep(0.1)
			if ser.in_waiting == 0:
				ser.write(command.encode())
			elif ser.in_waiting > 0:
				data_raw = ser.readline().decode()
				if data_raw:
					ser.close()
					return data_raw
	except Exception as e:
		logger.error("Unexpected exception: {}".format(e))
	finally:
		ser.close()

	return {}
	# 	print("\nexit")


class HttpGetHandler(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()

	def _set_error(self):
		self.send_response(404)
		self.send_header('Content-type', 'application/json')
		self.end_headers()

	def do_HEAD(self):
		self._set_headers()

	# GET sends back a Hello world message
	def do_GET(self):
		json_data = get_data()
		logger.info('request from: {}'.format(self.client_address[0]))

		if self.path == '/':
			self._set_headers()
			self.wfile.write(bytes(json_data.encode()))
			# save it into DATABASE
		elif self.path == "/filter":
			self._set_headers()
			self.wfile.write(bytes(json_data.encode()))
		else:
			self.send_error(404)


	# POST echoes the message adding a JSON field
	def do_POST(self):
		ctype, pdict = cgi.parse_header(self.headers.get('content-type'))

		# refuse to receive non-json content
		if ctype != 'application/json':
			self.send_response(400)
			self.end_headers()
			return

		# read the message and convert it into a python dictionary
		length = int(self.headers.get('content-length'))
		message = json.loads(self.rfile.read(length))

		# add a property to the object, just to mess with data
		message['received'] = 'ok'

		# send the message back
		self._set_headers()
		self.wfile.write(json.dumps(message))

def get_ip():
	time.sleep(5)
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.settimeout(5)
	try:
		# doesn't even have to be reachable
		s.connect(('10.254.254.254', 1))
		IP = s.getsockname()[0]
	except Exception:
		IP = get_ip()
		#IP = '127.0.0.1'
	finally:
		s.close()
	return IP


def run(host, port, server_class=HTTPServer, handler_class=HttpGetHandler):
	server_address = (host, port)
	httpd = server_class(server_address, handler_class)
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		httpd.server_close()


def create_filename():
	now = datetime.now()
	return 'data_{}.csv'.format(now.strftime('%Y_%m_%d'))


def create_new_csv(filename=create_filename()):
	with open(filename, mode='w', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(['station', 'datetime', 'sensPm25', 'sensPressure', 'sensDhtTemp', 'sensDhtHumidity', 'sens18b20Temp'])


def meteo_data(delay):
	filename = create_filename()
	create_new_csv(filename)
	while True:
		time.sleep(delay)
		with open(filename, mode='a', newline='') as file:
			writer = csv.writer(file)

			data = json.loads(get_data())
			new_filename = create_filename()
			local_current_time = datetime.now() #.strftime('%Y-%m-%d_%H:%M:%S')
			print(data)

			if new_filename != filename:
				file.close()
				create_new_csv(new_filename)
				with open(new_filename, mode='a', newline='') as file:
					writer2 = csv.writer(file)
					writer2.writerow([station_name, local_current_time, data['sensPm25'], data['sensPressure'], data['sensDhtTemp'], data['sensDhtHumidity'], data['sens18b20Temp']])
			else:
				writer.writerow([station_name, local_current_time, data['sensPm25'], data['sensPressure'], data['sensDhtTemp'], data['sensDhtHumidity'], data['sens18b20Temp']])



if __name__ == '__main__':
	from sys import argv

	#log_path = logData['logPath']
	#os.makedirs(log_path, exist_ok=True)
	#log_full_path = log_path + "/logfile.log"
	#logg = [log_full_path, logData['logMaxBytes'], logData['logBackupCount']]
	#logfile(log_full_path, maxBytes=logData['logMaxBytes'], backupCount=logData['logBackupCount'])

	p1 = mp.Process(target=meteo_data, args=(2,))
	p1.start()

	try:
		server_host = get_ip()
		# get public host
		# from subprocess import check_output
		# public_ip = check_output(['hostname', '-I']).decode().strip().split(' ')[1]
		if len(argv) == 2:
			server_port = int(argv[1])
		logger.info('serving at {}:{}'.format(server_host, server_port))
		# logger.info(get_data())
		# run(server_host, server_port)
		p2 = mp.Process(target=run, args=(server_host, server_port))
		p2.start()

	except Exception as e:
		logger.error('Unexpected error: {}'.format(e))
		raise SystemExit

# add csv file for saving