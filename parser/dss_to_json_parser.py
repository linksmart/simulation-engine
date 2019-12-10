import json
import re


class dssToJson:
	def convert_dss_to_json(self):
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
		result['common']['angle'] = 30
		result['common']['MVAsc3'] = 20000
		result['common']['base_frequency'] = 60
		result['common']['phases'] = 3
		unit_linecode = None
		
		rel_path = "Check.dss"
		cur_path = '/opt/project/tests/data/13Bus' + '/' + rel_path
		
		with open(cur_path, 'r') as f:
			for cnt, line in enumerate(f):
				
				words = line.strip().split(" ")
				if words[0] == "!":
					continue
				for word in words:
					if 'basefreq' in word.lower():
						result['common']['base_frequency'] = int(word.split('=')[1])
					if word.lower() == 'voltagebases':
						result['common']['VoltageBases'] = []
						values = re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', line)
						for value in values:
							result['common']['VoltageBases'].append(float(value))
				# print("Count {}: {}".format(cnt, words))
				# if (words[0] != '~'):
				# 	previous_type = ''
				if '.' in line:
					split_words_key_value = line.split("=")
					split_words = split_words_key_value[0].split(".")
					if len(split_words) > 2:
						if (split_words[0] == "Transformer"):
							for reg in radials['transformer']:
								if reg['id'] == split_words[1]:
									reg[split_words[2].lower()] = []
									values = re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', split_words_key_value[1])
									for value in values:
										reg[split_words[2].lower()].append(float(value))
				
				if str(words[0]).lower() == 'new':
					type = (words[1].split('.')[0]).lower()
					if ('circuit' in words[1]):
						value = words[1].split('.')[1]
						
						result['common']['id'] = value
						previous_type = 'circuit'
						continue
					if (type == 'transformer'):
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
							if ((word.split('=')[0]).lower() == 'xhl' or word.split('=')[0] == '%r'):
								if "(" in operation_word:
									first = int(re.findall(r'\d+', operation_word)[0])
									# while ")" not in operation_word:
									second_word = words[index + 1]
									second = int(re.findall(r'\d+', second_word)[0])
									index = index + 1
								
								if ((word.split('=')[0]).lower() == 'xhl'):
									trans['xsc_array'] = []
									if "(" in operation_word:
										trans['xsc_array'].append(first / second)
									else:
										trans['xsc_array'].append(float(split_word[1]))
									continue
								elif (word.split('=')[0] == '%r'):
									trans['percent_rs'] = (first / second)
								word = words[index]
							if '[' in operation_word or '(' in operation_word or '"' in operation_word or "'" in operation_word:
								elements = []
								# operation_word = split_word[1]
								if "buses" in word:
									elements.append((re.findall(r'[-+]?(?:(?:\w*\d*\.\d+)|(?:\w*\d+\.?))', operation_word)[0]))
								elif "conns" in word:
									elements.append((re.findall(r'[a-z]*', operation_word)[1]))
								else:
									elements.append(float(re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', operation_word)[0]))
								second_word = ''
								while True:
									index = index + 1
									operation_word = words[index]
									if operation_word != '':
										if "buses" in word:
											elements.append((re.findall(r'[-+]?(?:(?:\w*\d*\.\d+)|(?:\w*\d+\.?))', operation_word)[0]))
										elif "conns" in word:
											elements.append((re.findall(r'[a-z]*', operation_word)[0]))
										else:
											elements.append(float(re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', operation_word)[0]))
									if (']' in operation_word) or (')' in operation_word) or ( '"' in operation_word) or "'" in operation_word:
										break
									
								value_set = True
								value = elements
								key = split_word[0].lower()
								
								trans[key] = value
							
							elif word != ' ' and word != '~' and word != '' and word != '/':
								split_word = word.split('=')
								set = False
								if (len(split_word) > 1):
									key = split_word[0].lower()
									if not value_set:
										value = split_word[1]
										if key == 'like':
											for tr in radials['transformer']:
												if tr['id'] == value:
													for key in tr.keys():
														if key not in trans:
															trans[key] = tr[key]
											set = True
										if re.compile('^\s*\d+\s*$').search(value) and key != 'bus':
											value = int(value)
										elif re.compile('^\s*(\d*\.\d+)|(\d+\.\d*)\s*$').search(value) and key != 'bus':
											value = float(value)
									if key == "%loadloss":
										key = "percent_load_loss"
									if key != 'like' and not set:
										trans[key] = value
						radials['transformer'].append(trans)
						previous_type = 'Transformer'
						previous_index = len(radials['transformer'])
					# previous_index = 1
					if (type == "linecode"):
						# linecode = []
						linecode = {}
						linecode['id'] = words[1].split('.')[1]
						if unit_linecode is not None:
							linecode['units'] = unit_linecode
						else:
							linecode['units'] = 'mi'
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
								if len(split_word) > 1 and key.lower() != 'basefreq':
									linecode[key] = value
						previous_type = "linecode"
						radials['linecode'].append(linecode)
					if (type == "load"):
						# linecode = []
						load = {}
						load['id'] = words[1].split('.')[1]
						for i in range(len(words)):
							word = words[i]
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
									if value == " " or value == '':
										while value == '':
											i = i + 1
											value = words[i]
									if re.compile('^\s*\d+\s*$').search(value) and key != 'bus':
										value = int(value)
									elif re.compile('^\s*(\d*\.\d+)|(\d+\.\d*)\s*$').search(value) and key != 'bus':
										value = float(value)
									load[key] = value
						previous_type = "load"
						radials['loads'].append(load)
					if (type == "capacitor"):
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
									if re.compile('^\s*\d+\s*$').search(value) and key != 'bus':
										value = int(value)
									elif re.compile('^\s*(\d*\.\d+)|(\d+\.\d*)\s*$').search(value) and key != 'bus':
										value = float(value)
									capacitator[key] = value
						previous_type = "capacitor"
						radials['capacitor'].append(capacitator)
					if (type == "regcontrol"):
						# linecode = []
						regcontrol = {}
						regcontrol['id'] = words[1].split('.')[1]
						for word in words[1:]:
							set = False
							if word != ' ' and word != '~' and word != '':
								split_word = word.split('=')
								if (len(split_word) > 1):
									key = split_word[0].lower()
									value = split_word[1]
									if key == 'like':
										for reg in radials['regcontrol']:
											if reg['id'] == value:
												for key in reg.keys():
													if key not in regcontrol:
														regcontrol[key] = reg[key]
										set = True
									if key == 'ptratio':
										key = 'ptration'
									if re.compile('^\s*\d+\s*$').search(value):
										value = int(value)
									elif re.compile('^\s*(\d*\.\d+)|(\d+\.\d*)\s*$').search(value):
										value = float(value)
									if key!= 'like' and set==False:
										regcontrol[key] = value
						previous_type = "regcontrol"
						radials['regcontrol'].append(regcontrol)
					if (type == "line"):
						# linecode = []
						powerline = {}
						powerline['id'] = words[1].split('.')[1]
						powerline['phases'] = 3
						for index in range(len(words)):
							word = words[index]
							if word != ' ' and word != '~' and word != '':
								split_word = word.split('=')
								if (len(split_word) > 1):
									key = split_word[0].lower()
									value = split_word[1]
									if '(' in value:
										first = float(re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', value)[0])
										# while ")" not in operation_word:
										second_word = words[index + 1]
										second = float(re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', second_word)[0])
										index = index + 1
										value = first/second
									if key == 'kv':
										key = 'kV'
									if key == 'kvar':
										key = 'kVAR'
									if key == 'units':
										key = 'unitlength'
										unit_linecode = value
									
									if not isinstance(value, float) and re.compile('r[\d+]').search(key) and 'e' in value:
										value = float(value)
									elif key == 'switch':
										if value in ['y', 'Y', 'Yes', 'yes', 't', 'true', 'T', 'True']:
											value = True
										if value in ['f', 'F', 'No', 'no', 'f', 'false', 'F', 'False']:
											value = False
									elif key != 'length' and key != 'linecode' and re.compile('^\s*\d+\s*$').search(value) and key != 'bus1' and key != 'bus2':
										value = int(value)
									elif key != 'linecode' and re.compile('^(\d*\.\d+)|(\d+\.\d*)|(\d+)\s*$').search(
										value) and key != 'bus1' and key != 'bus2':
										value = float(value)
									if powerline['phases']==3 and(key == 'bus1' or key == 'bus2'):
										value = value.split('.')[0]
										
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
						if (
							to_check == "Rmatrix" or to_check == "Xmatrix" or to_check == "Cmatrix" or previous_set_square == True):
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
						
						if (word.lower() == "rmatrix" or word.lower() == "xmatrix" or word.lower() == "cmatrix"):
							linecode[word.lower()] = []
							word_set = word
						if (len(split_word) > 1 and "" not in split_word):
							key = split_word[0]
							linecode[key] = split_word[1]
						if "(" in word or "[" in word or previous_set:
							previous_set = True
							if word == "|":
								linecode[word_set.lower()].append(val)
								val = []
							if (word == ')' or word == ']'):
								linecode[word_set.lower()].append(val)
								val = []
								previous_set = False
							if (not word == '|' and not word == ')'):
								value = re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', word)
								if (len(value) != 0):
									val.append(float(value[0]))
							if (']' in word and len(val) != 0):
								linecode[word_set.lower()].append(val)
								val = []
				
				if (words[0] == '~' and previous_type == 'circuit'):
					for word in words[1:]:
						split_word = word.split('=')
						key = split_word[0].lower()
						if len(split_word) > 1:
							value = word.split('=')[1]
						if (key == 'pu'):
							result['common']['per_unit'] = float(value)
						elif (key == 'basekv'):
							result['common']['base_kV'] = float(value)
						elif (key == 'mvasc3'):
							result['common']['MVAsc3'] = int(value)
						elif (key == 'mvasc1'):
							result['common']['MVAsc1'] = int(value)
						elif key == 'bus1':
							result['common']['bus1'] = str(value)
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
					for index in range(len(words)):
						word = words[index]
						operation_word = ''
						value_set = False
						if word != ' ' and word != '~' and word != '':
							split_word = word.split('=')
							key = split_word[0].lower()
							if (len(split_word) > 1):
								operation_word = split_word[1]
							if key == 'wdg':
								count = count + 1
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
									elements.append(
										(re.findall(r'[-+]?(?:(?:\w*\d*\.\d+)|(?:\w*\d+\.?))', operation_word)[0]))
								elif key == "conns":
									elements.append(''.join(re.findall(r'[a-z A-Z]*', operation_word)))
								else:
									elements.append(
										float(re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', operation_word)[0]))
								second_word = ''
								while ']' not in operation_word:
									operation_word = words[index + 1]
									if operation_word != '':
										if key == "buses":
											elements.append((re.findall(r'[-+]?(?:(?:\w*\d*\.\d+)|(?:\w*\d+\.?))',
											                            operation_word)[0]))
										elif key == "conns":
											elements.append(''.join(re.findall(r'[a-z A-Z]*', operation_word)))
										else:
											elements.append(float(
												re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', operation_word)[0]))
									index = index + 1
								value_set = True
								value = elements
								count = len(elements)
							if (len(split_word) > 1):
								if not value_set:
									value = split_word[1]
									if re.compile('^\s*\d+\s*$').search(value) and key != 'bus' and key != 'buses':
										value = int(value)
									elif re.compile('^\s*(\d*\.\d+)|(\d+\.\d*)\s*$').search(
										value) and key != 'bus' and key != 'buses':
										value = float(value)
								if key in ['conn', 'kv', 'kva']:
									key = key + 's'
								if key == 'conns':
									if(isinstance(value, list)):
										for val in value:
											val = val.lower()
									else:
										value = value.lower()
								if key == 'bus':
									key = 'buses'
								if key == 'xhl':
									key = 'xsc_array'
								if key == '%r':
									key = 'percent_rs'
								if key == '%loadloss':
									key = 'percent_load_loss'
								dict = {}
								dict['windings'] = count
								if not key in radials['transformer'][
									previous_index - 1].keys() and key != "wdg" and key != "xht" and key != "xlt" and key != "percent_load_loss":
									radials['transformer'][previous_index - 1][key] = []
								# if not 'windings' in radials['transformer'][previous_index - 1].keys():
								# 	radials['transformer'][previous_index - 1]['windings'] = count
								radials['transformer'][previous_index - 1].update(dict)
								# result['radials']['transformer'][previous_index - 1]['windings'] = count
								if isinstance(value, list) and key != 'wdg' and key != "xht" and key != "xlt":
									for v in value:
										radials['transformer'][previous_index - 1][key].append(v)
								elif key == 'percent_load_loss':
									radials['transformer'][previous_index - 1][key] = value
								elif key != 'wdg' and key != "xht" and key != "xlt":
									radials['transformer'][previous_index - 1][key].append(value)
					previous_type = 'Transformer'
		result['common']["url_storage_controller"] = "http://192.168.99.100:8080"
		result['common']["city"] = "Fur"
		result['common']["country"] = "Denmark"
		result['common']["max_real_power_in_kW_to_grid"] = 6
		result['common']["max_reactive_power_in_kVar_to_grid"] = 6
		result['radials'].append(radials)
		with open("Result.json", 'w') as file:
			json.dump(result, file, ensure_ascii=False, indent=4)
		print(result)


obj = dssToJson()
obj.convert_dss_to_json()
