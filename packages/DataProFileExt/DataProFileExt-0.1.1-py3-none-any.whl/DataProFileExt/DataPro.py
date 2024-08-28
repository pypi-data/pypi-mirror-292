import datetime
import os
import math
import random


class File:
	global dont
	dont = False

	# init method or constructor
	def __init__(self, file):
		global dont
		self.file = file
		if os.path.exists(file):
			file_in_text = str(self.file)
			if file_in_text.endswith('.DataPro'):
				pass
			else:
				print("File anit a .DataPro")
				dont = True
		else:
			print(f"{self.file} doesnt exist.")
			dont = True


	def load(self, key, data):
		if dont:
			print("nuh uh")
			return
		else:
			date = datetime.datetime.now()
			formatted_now = date.strftime('%Y-%m-%d %H:%M:%S.%f')
			__id__ = f"ID:{date} {len(str(key))}::{len(str(data))}"

			with open (self.file,'w') as file:
				data_format = "{{Data:{}}}".format(str(data))
				file.write(f"{__id__}\nKey:{str(key)}\n{str(data_format)}")
				print(f"Successfully loaded {self.file} with an ID of {__id__}")

	def unload(self):
		with open (self.file,'r') as file:
			# Gets file content
			file_data = file.read()
			#gets date
			date = file_data[slice(3,13)]
			time_of_date = file_data[slice(13,22)]
			both = (f"{date} {time_of_date}")
			#Find num of key chars
			stop = 32
			num_of_key_chars = file_data[slice(30,stop)]
			while num_of_key_chars.isdigit():
				stop += 1
				num_of_key_chars = file_data[slice(30,stop)]

			num_of_key_chars = file_data[slice(30, stop - 1)]
			#print(fixed)
			#Find num of data cars
			stop2 = 36
			num_of_data_chars = file_data[slice(stop + 1, stop2)]
			while num_of_data_chars.isdigit():
				stop2 += 1
				num_of_data_chars = file_data[slice(stop + 1, stop2)]

			num_of_data_chars = file_data[slice(stop + 1, stop2 - 1)]
			#convert
			num_of_data_chars = int(num_of_data_chars)
			num_of_key_chars = int(num_of_key_chars)

			#make life a lil bit more easy
			short = int(len(str(num_of_data_chars)))
			#gets key

			key = file_data[slice(stop + short + 6, stop + short + 6 + num_of_key_chars)]

			#gets data key
			data = file_data[slice(stop + short + 6 + num_of_key_chars + 7,stop + short + 6 + num_of_key_chars + 7 + num_of_data_chars)]


		last_load = (f"Last Load: {date}, Time Of day when load:{time_of_date}")
		#gonna do id bc i couldnt get the first one to be global
		__id__ = file_data[slice(3,34 + len(str(num_of_key_chars)))].strip()
		return  last_load, key, data, __id__