import json
import re

class dssToJson:
	def convert(self):
		result = {}
		previous_type = ''
		result['common'] = {}
		result['radials'] = []
		radials = {}
		# result['radials'] = {}
		radials['regcontrol'] = []
		radials['transformer'] = []
		radials['linecode'] = []
		radials['loads'] = []
		radials['capacitor'] = []
		radials['powerLines'] = []

		with open('IEEE13Nodeckt.dss', 'r') as f:
			for cnt, line in enumerate(f):
				
				words = line.strip().split(" ")
				for word in words:
					if 'BaseFreq' in word:
						result['common']['base_frequency'] = int(word.split('=')[1])
					if 'Voltagebases' in word:
						result['common']['VoltageBases'] = []
						values = re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', line)
						for value in values:
							result['common']['VoltageBases'].append(float(value))
				print("Count {}: {}".format(cnt, words))
				if (words[0] != '~'):
					previous_type = ''
				if '.' in line:
					split_words_key_value = line.split("=")
					split_words = split_words_key_value[0].split(".")
					if len(split_words) > 2:
						if(split_words[0]=="Transformer"):
							for reg in radials['transformer']:
								if reg['id'] == split_words[1]:
									reg[split_words[2].lower()] = []
									values = re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', split_words_key_value[1])
									for value in values:
										reg[split_words[2].lower()].append(float(value))
									
				if str(words[0]).lower() == 'new':
					type = words[1].split('.')[0]
					if (type == 'circuit'):
						value = words[1].split('.')[1]
						
						result['common']['id'] = value
						previous_type = 'circuit'
						continue
					if (type == 'Transformer'):
						count = 0
						trans = {}
						trans['id'] = words[1].split('.')[1]
						closed = False
						for index in range(len(words)):
							value_set = False
							word = words[index]
							split_word = word.split("=")
							operation_word = ''
							if len(split_word) > 1:
								operation_word = split_word[1]
							if (word.split('=')[0] == 'XHL' or word.split('=')[0] == '%r'):
								if "(" in operation_word:
									first = int(re.findall(r'\d+', operation_word)[0])
									# while ")" not in operation_word:
									second_word = words[index + 1]
									second = int(re.findall(r'\d+', second_word)[0])
									index = index + 1
								
								if (word.split('=')[0] == 'XHL'):
									trans['xsc_array'] = []
									if "(" in operation_word:
										trans['xsc_array'].append(first / second)
									else:
										trans['xsc_array'].append(float(split_word[1]))
									continue
								elif (word.split('=')[0] == '%r'):
									trans['percent_rs'] = (first / second)
								word = words[index]
							if '[' in operation_word:
								elements = []
								# operation_word = split_word[1]
								elements.append(float(re.findall(r'\d+', operation_word)[0]))
								second_word = ''
								while ']' not in operation_word:
									operation_word = words[index + 1]
									if operation_word != '':
										elements.append(float(re.findall(r'\d+', operation_word)[0]))
									index = index + 1
								value_set = True
								value = elements
							
							if word != ' ' and word != '~' and word != '' and word != '/':
								split_word = word.split('=')
								if (len(split_word) > 1):
									key = split_word[0].lower()
									if not value_set:
										value = split_word[1]
										if re.compile('^\s*\d+\s*$').search(value)and key!= 'bus':
											value = int(value)
										elif re.compile('^\s*(\d*\.\d+)|(\d+\.\d*)\s*$').search(value)and key!= 'bus':
											value = float(value)
									trans[key] = value
						radials['transformer'].append(trans)
						previous_type = 'Transformer'
						previous_index = len(radials['transformer'])
						# previous_index = 1
					if (type == "linecode" or type == "Linecode"):
						# linecode = []
						linecode = {}
						linecode['id'] = words[1].split('.')[1]
						for word in words[1:]:
							if word != ' ' and word != '~' and word != '':
								split_word = word.split('=')
								if len(split_word) > 1:
									value = split_word[1]
								key = split_word[0]
								if key == 'Units':
									key = 'units'
								if key == 'nphases':
									value = int(value)
								if len(split_word) > 1 and key!= 'BaseFreq':
									linecode[key] = value
						previous_type = "linecode"
						radials['linecode'].append(linecode)
					if (type == "Load"):
						# linecode = []
						load = {}
						load['id'] = words[1].split('.')[1]
						for word in words[1:]:
							if word != ' ' and word != '~' and word != '':
								split_word = word.split('=')
								if (len(split_word) > 1):
									key = split_word[0].lower()
									if key == 'conn':
										key = "connection_type"
									if key == 'bus1':
										key = 'bus'
									if key == 'kv':
										key = 'kV'
									if key == 'kw':
										key = 'kW'
									if key == 'kvar':
										key = 'kVar'
									if key == 'pf':
										key = 'powerfactor'
									value = split_word[1]
									if re.compile('^\s*\d+\s*$').search(value) and key!= 'bus':
										value = int(value)
									elif re.compile('^\s*(\d*\.\d+)|(\d+\.\d*)\s*$').search(value)and key!= 'bus':
										value = float(value)
									load[key] = value
						previous_type = "load"
						radials['loads'].append(load)
					if (type == "Capacitor"):
						# linecode = []
						capacitator = {}
						capacitator['id'] = words[1].split('.')[1]
						for word in words[1:]:
							if word != ' ' and word != '~' and word != '':
								split_word = word.split('=')
								if (len(split_word) > 1):
									key = split_word[0].lower()
									if key == 'bus1':
										key = 'bus'
									if key == 'kv':
										key = 'kV'
									if key == 'kvar':
										key = 'kVar'
									value = split_word[1]
									if re.compile('^\s*\d+\s*$').search(value) and key!= 'bus':
										value = int(value)
									elif re.compile('^\s*(\d*\.\d+)|(\d+\.\d*)\s*$').search(value) and key!= 'bus':
										value = float(value)
									capacitator[key] = value
						previous_type = "capacitor"
						radials['capacitor'].append(capacitator)
					if (type == "regcontrol"):
						# linecode = []
						regcontrol = {}
						regcontrol['id'] = words[1].split('.')[1]
						for word in words[1:]:
							if word != ' ' and word != '~' and word != '':
								split_word = word.split('=')
								if (len(split_word) > 1):
									key = split_word[0].lower()
									value = split_word[1]
									if key == 'ptratio':
										key = 'ptration'
									if re.compile('^\s*\d+\s*$').search(value):
										value = int(value)
									elif re.compile('^\s*(\d*\.\d+)|(\d+\.\d*)\s*$').search(value):
										value = float(value)
									regcontrol[key] = value
						previous_type = "regcontrol"
						radials['regcontrol'].append(regcontrol)
					if (type == "Line"):
						# linecode = []
						powerline = {}
						powerline['id'] = words[1].split('.')[1]
						for word in words[1:]:
							if word != ' ' and word != '~' and word != '':
								split_word = word.split('=')
								if (len(split_word) > 1):
									key = split_word[0].lower()
									if key == 'kv':
										key = 'kV'
									if key == 'kvar':
										key = 'kVAR'
									if key == 'units':
										key = 'unitlength'
									value = split_word[1]
									if 'e' in value:
										value = float(value)
									elif key == 'switch':
										if value in ['y', 'Y', 'Yes', 'yes', 't', 'true', 'T', 'True']:
											value = True
										if value in ['f', 'F', 'No', 'no', 'f', 'false', 'F', 'False']:
											value = False
									elif re.compile('^\s*\d+\s*$').search(value) and key != 'bus1' and key != 'bus2':
										value = int(value)
									elif re.compile('^(\d*\.\d+)|(\d+\.\d*)\s*$').search(value) and key != 'bus1' and key != 'bus2':
										value = float(value)
									powerline[key] = value
						previous_type = "powerLines"
						radials['powerLines'].append(powerline)
				if (words[0] == '~' and previous_type == 'linecode'):
					word_set = ""
					previous_set = False
					val = []
					previous_set_square = False
					key = ""
					for index in range(len(words)):
						word = words[index]
						# operation_word = ''
						# value_set = False
						split_word = word.split('=')
						# line_dict = {}
						to_check = split_word[0]
						if (to_check == "Rmatrix" or to_check == "Xmatrix" or to_check == "Cmatrix" or previous_set_square == True):
							previous_set_square = True
							if (to_check == "Rmatrix" or to_check == "Xmatrix" or to_check == "Cmatrix"):
								key = to_check.lower()
								linecode[to_check.lower()] = []
							if ('|' in word):
								linecode[key].append(val)
								val = []
							value = re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', word)
							if (len(value) != 0):
								val.append(float(value[0]))
							if (']' in word):
								previous_set_square = False
								if (len(val) != 0):
									linecode[key].append(val)
									val = []
							continue
						
						if (word == "rmatrix" or word == "xmatrix" or word == "cmatrix"):
							linecode[word] = []
							word_set = word
						if (len(split_word) > 1 and "" not in split_word):
							key = split_word[0]
							linecode[key] = split_word[1]
						if "(" in word or "[" in word or previous_set:
							previous_set = True
							if word == "|":
								linecode[word_set].append(val)
								val = []
							if (word == ')' or word == ']'):
								linecode[word_set].append(val)
								val = []
								previous_set = False
							if (not word == '|' and not word == ')'):
								value = re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', word)
								if (len(value) != 0):
									val.append(float(value[0]))
							if (']' in word and len(val)!=0):
								linecode[word_set].append(val)
								val = []
				
				if (words[0] == '~' and previous_type == 'circuit'):
					for word in words[1:]:
						split_word = word.split('=')
						key = split_word[0].lower()
						if (key == 'pu'):
							result['common']['per_unit'] = float(word.split('=')[1])
						elif (key == 'basekv'):
							result['common']['base_kV'] = float(word.split('=')[1])
						elif (key == 'mvasc3'):
							result['common']['MVAsc3'] = int(word.split('=')[1])
						elif (key == 'mvasc1'):
							result['common']['MVAsc1'] = int(word.split('=')[1])
						elif word != ' ' and word != '~' and word != '':
							if (len(split_word) > 1):
								value = split_word[1]
								if re.compile('^\s*\d+\s*$').search(value):
									value = int(value)
								elif re.compile('^\s*(\d*\.\d+)|(\d+\.\d*)\s*$').search(value):
									value = float(value)
								result['common'][key] = value
					previous_type = 'circuit'
				if (words[0] == '~' and previous_type == 'Transformer'):
					# previous_index = previous_index + 1
					print("Hello")
					for index in range(len(words)):
						word = words[index]
						operation_word = ''
						value_set = False
						if word != ' ' and word != '~' and word != '':
							split_word = word.split('=')
							key = split_word[0].lower()
							if (len(split_word) > 1):
								operation_word = split_word[1]
							if "(" in operation_word:
								first = float(re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', operation_word)[0])
								# while ")" not in operation_word:
								second_word = words[index + 1]
								second = float(re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', second_word)[0])
								index = index + 1
								value = first / second
								value_set = True
							if '[' in operation_word:
								elements = []
								operation_word = split_word[1]
								if key == "buses":
									elements.append((re.findall(r'[-+]?(?:(?:\w*\d*\.\d+)|(?:\w*\d+\.?))', operation_word)[0]))
								else:
									elements.append(float(re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', operation_word)[0]))
								second_word = ''
								while ']' not in operation_word:
									operation_word = words[index + 1]
									if operation_word != '':
										if key == "buses":
											elements.append((re.findall(r'[-+]?(?:(?:\w*\d*\.\d+)|(?:\w*\d+\.?))', operation_word)[0]))
										else:
											elements.append(float(re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', operation_word)[0]))
									index = index + 1
								value_set = True
								value = elements
								count = len(elements)
							if (len(split_word) > 1):
								if not value_set:
									value = split_word[1]
									if re.compile('^\s*\d+\s*$').search(value)and key!= 'bus' and key!= 'buses':
										value = int(value)
									elif re.compile('^\s*(\d*\.\d+)|(\d+\.\d*)\s*$').search(value)and key!= 'bus' and key!= 'buses':
										value = float(value)
								if key in ['conn', 'kv', 'kva']:
									key = key +'s'
								if key == 'conns':
									value = value.lower()
								if key == 'bus':
									key = 'buses'
								if key == '%r':
									key = 'percent_rs'
								if key == '%loadloss':
									key = 'percent_load_loss'
								if not key in radials['transformer'][previous_index - 1].keys() and key != "wdg" and key != "xht" and key != "xlt" and key != "percent_load_loss":
									radials['transformer'][previous_index - 1][key] = []
								if not 'windings' in radials['transformer'][previous_index - 1].keys():
									radials['transformer'][previous_index - 1]['windings'] = count
								# result['radials']['transformer'][previous_index - 1]['windings'] = count
								if isinstance(value, list) and key != 'wdg'and key != "xht" and key != "xlt":
									for v in value:
										radials['transformer'][previous_index - 1][key].append(v)
								elif key != 'wdg'and key != "xht" and key != "xlt":
									radials['transformer'][previous_index - 1][key].append(value)
					previous_type = 'Transformer'
				# previous_index = previous_index + 1
				# previous_index = previous_index + 1
				cnt = len(words)
		result['common']["url_storage_controller"] = "http://localhost:9090"
		result['common']["city"] = "Fur"
		result['common']["country"] = "Denmark"
		result['common']["max_real_power_in_kW_to_grid"] = 6
		result['common']["max_reactive_power_in_kVar_to_grid"] = 6
		result['radials'].append(radials)
		with open("Result.json", 'w') as file:
			json.dump(result, file, ensure_ascii=False, indent=4)
		# print(json.dumps(result))
		print(result)
		

ob = dssToJson()
ob.convert()
