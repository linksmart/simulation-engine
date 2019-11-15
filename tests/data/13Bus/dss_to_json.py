import json
import re

class dssToJson:
	def convert(self):
		result = {}
		previous_type = ''
		result['common'] = {}
		result['radials'] = {}
		result['radials']['regcontrol'] = []
		result['radials']['transformers'] = []
		result['radials']['linecode'] = []
		result['radials']['loads'] = []
		result['radials']['capacitor'] = []
		result['radials']['powerLines'] = []

		with open('IEEE13Nodeckt.dss', 'r') as f:
			for cnt, line in enumerate(f):
				words = line.strip().split(" ")
				print("Count {}: {}".format(cnt, words))
				if (words[0] != '~'):
					previous_type = ''
				if str(words[0]).lower() == 'new':
					type = words[1].split('.')[0]
					if (type == 'circuit'):
						value = words[1].split('.')[1]
						
						result['common']['id'] = value
						previous_type = 'circuit'
						continue
					if (type == 'Transformer'):
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
									trans['xsc_array'] = (first / second)
								elif (word.split('=')[0] == '%r'):
									trans['percent_rs'] = (first / second)
								word = words[index]
							if '[' in operation_word:
								elements = []
								# operation_word = split_word[1]
								elements.append((re.findall(r'\d+', operation_word)[0]))
								second_word = ''
								while ']' not in operation_word:
									operation_word = words[index + 1]
									if operation_word != '':
										elements.append(re.findall(r'\d+', operation_word)[0])
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
						result['radials']['transformers'].append(trans)
						previous_type = 'Transformer'
						previous_index = len(result['radials']['transformers'])
					if (type == "linecode" or type == "Linecode"):
						# linecode = []
						linecode = {}
						linecode['id'] = words[1].split('.')[1]
						for word in words[1:]:
							if word != ' ' and word != '~' and word != '':
								split_word = word.split('=')
								if (len(split_word) > 1):
									linecode[split_word[0]] = split_word[1]
						previous_type = "linecode"
						result['radials']['linecode'].append(linecode)
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
									value = split_word[1]
									if re.compile('^\s*\d+\s*$').search(value) and key!= 'bus':
										value = int(value)
									elif re.compile('^\s*(\d*\.\d+)|(\d+\.\d*)\s*$').search(value)and key!= 'bus':
										value = float(value)
									load[key] = value
						previous_type = "load"
						result['radials']['loads'].append(load)
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
										key = 'kVAR'
									value = split_word[1]
									if re.compile('^\s*\d+\s*$').search(value) and key!= 'bus':
										value = int(value)
									elif re.compile('^\s*(\d*\.\d+)|(\d+\.\d*)\s*$').search(value) and key!= 'bus':
										value = float(value)
									capacitator[key] = value
						previous_type = "capacitor"
						result['radials']['capacitor'].append(capacitator)
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
						result['radials']['regcontrol'].append(regcontrol)
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
									value = split_word[1]
									if re.compile('^\s*\d+\s*$').search(value) and key != 'bus1' and key != 'bus2':
										value = int(value)
									elif re.compile('^(\d*\.\d+)|(\d+\.\d*)\s*$').search(value) and key != 'bus1' and key != 'bus2':
										value = float(value)
									powerline[key] = value
						previous_type = "powerLines"
						result['radials']['powerLines'].append(powerline)
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
						if (word.split('=')[0] == 'pu'):
							result['common']['per_unit'] = float(word.split('=')[1])
						elif word != ' ' and word != '~' and word != '':
							split_word = word.split('=')
							if (len(split_word) > 1):
								value = split_word[1]
								if re.compile('^\s*\d+\s*$').search(value):
									value = int(value)
								elif re.compile('^\s*(\d*\.\d+)|(\d+\.\d*)\s*$').search(value):
									value = float(value)
								result['common'][split_word[0]] = value
					previous_type = 'circuit'
				if (words[0] == '~' and previous_type == 'Transformer'):
					for index in range(len(words[1:])):
						word = words[index]
						operation_word = ''
						value_set = False
						if word != ' ' and word != '~' and word != '':
							split_word = word.split('=')
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
								elements.append(float(re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', operation_word)[0]))
								second_word = ''
								while ']' not in operation_word:
									operation_word = words[index + 1]
									if operation_word != '':
										elements.append(
											float(re.findall(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))', operation_word)[0]))
									index = index + 1
								value_set = True
								value = elements
							if (len(split_word) > 1):
								key = split_word[0]
								if not value_set:
									value = split_word[1]
									if re.compile('^\s*\d+\s*$').search(value)and key!= 'bus':
										value = int(value)
									elif re.compile('^\s*(\d*\.\d+)|(\d+\.\d*)\s*$').search(value)and key!= 'bus':
										value = float(value)
								if key in ['conn', 'kv', 'kva']:
									key = key +'s'
								if key == 'bus':
									key = 'buses'
								if key == '%r':
									key = 'percent_rs'
								if not split_word[0] in result['radials']['transformers'][previous_index - 1].keys():
									result['radials']['transformers'][previous_index - 1][key] = []
								if isinstance(value, list):
									for v in value:
										result['radials']['transformers'][previous_index - 1][key].append(v)
								else:
									result['radials']['transformers'][previous_index - 1][key].append(value)
					previous_type = 'Transformer'
				# previous_index = previous_index + 1
				cnt = len(words)
		print("***Result***")
		with open("Result.json", 'w') as file:
			json.dump(result, file, ensure_ascii=False, indent=4)
		# print(json.dumps(result))
		print(result)


ob = dssToJson()
ob.convert()
