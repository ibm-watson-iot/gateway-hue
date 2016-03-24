import sys
import json
import time
import ibmiotf.application
from ibmiotf import APIException

import requests
import signal

import argparse
import logging
from logging.handlers import RotatingFileHandler


class Server():

	def __init__(self, args):
		# Setup logging - Generate a default rotating file log handler and stream handler
		fhFormatter = logging.Formatter('%(asctime)-25s %(levelname)-7s %(message)s')
		sh = logging.StreamHandler()
		sh.setFormatter(fhFormatter)
		
		self.logger = logging.getLogger("server")
		self.logger.addHandler(sh)
		self.logger.setLevel(logging.DEBUG)
		
		self.options = ibmiotf.application.ParseConfigFile(args.config)
				
		# Init IOTF client
		self.client = ibmiotf.application.Client(self.options, logHandlers=[rfh])
		
		# Internal State
		self.knownDeviceTypes = {}
		self.knownDevices = {}
		
		# Init Hue properties
		self.hueAddress = args.ip
		self.hueUsername = args.username
			
	
	def _poll(self):
		# See: http://www.developers.meethue.com/documentation/lights-api
		r = requests.get("http://%s/api/%s/lights" % (self.hueAddress, self.hueUsername))
		lights = r.json();
		if isinstance(lights, list) and "error" in lights[0]:
			self.logger.critical("Error querying Hue Hub (%s) with username %s: %s" % (self.hueAddress, self.hueUsername, lights[0]['error']['description']))
		else:
			for id, light in lights.items():
				# Properties of the IoTF Device Type
				typeId = light['modelid']
				typeDescription = light['type']
				typeManufacturer = light['manufacturername']
				typeModel = light['modelid']
				
				# Properties of the IoTF Device
				deviceId = light['uniqueid'].replace(":", "-")
				deviceSwVersion = light['swversion']
				deviceManufacturer = light['manufacturername']
				deviceModel = light['modelid']
				
				state = light['state']
				
				# Register the device type if we need to
				if typeId not in self.knownDeviceTypes:
					try:
						deviceType = self.client.api.getDeviceType(typeId)
						self.knownDeviceTypes[typeId] = deviceType
					except APIException as e:
						self.logger.debug("ERROR [" + str(e.httpCode) + "] " + e.message)
						self.logger.info("Registering new device type: %s" % (typeId))
						
						deviceTypeInfo = { "manufacturer": typeManufacturer, "model": typeModel, "description": typeDescription, }
						deviceType = self.client.api.addDeviceType(deviceType=typeId, description=typeDescription, deviceInfo=deviceTypeInfo)
						self.knownDeviceTypes[typeId] = deviceType
					
				# Register the device if we need to
				if deviceId not in self.knownDevices:
					try:
						device = self.client.api.getDevice(typeId, deviceId)
						self.knownDevices[deviceId] = device
					except APIException as e:
						self.logger.debug("ERROR [" + str(e.httpCode) + "] " + e.message)
						self.logger.info("Registering new device: %s:%s" % (typeId, deviceId))
						
						deviceMetadata = {"customField1": "customValue1", "customField2": "customValue2"}
						deviceInfo = {"manufacturer": deviceManufacturer, "model": deviceModel, "fwVersion" : deviceSwVersion}
						device = self.client.api.registerDevice(typeId, deviceId, authToken=None, deviceInfo=deviceInfo, location=None, metadata=deviceMetadata)
						self.knownDevices[deviceId] = device
				
				# Publish the current state of the light
				self.client.publishEvent(typeId, deviceId, "state", "json", state)
	
	
	def start(self):
		self.client.connect()
		
		while True:
			self._poll()
			time.sleep(10)
		
		
	def stop(self):
		self.client.disconnect()
		

def interruptHandler(signal, frame):
	server.stop()
	sys.exit(0)


if __name__ == "__main__":
	signal.signal(signal.SIGINT, interruptHandler)

	# Initialize the properties we need
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--config', required=False)
	parser.add_argument('-i', '--ip', required=True)
	parser.add_argument('-u', '--username', required=True)

	args, unknown = parser.parse_known_args()

	print("(Press Ctrl+C to disconnect)")

	server = Server(args)
	server.start()