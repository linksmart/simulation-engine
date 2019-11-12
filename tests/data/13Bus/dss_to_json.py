import json
import re

class dssToJson:
	def convert(self):
		result = {}
		previous_type = ''
		result['radials'] = {}
		result['radials']['transformers'] = []
		result['radials']['linecode'] = []
		with open('IEEE13Nodeckt.dss', 'r') as f:
			for cnt, line in enumerate(f):
				words = line.strip().split(" ")
				print("Count {}: {}".format(cnt, words))
				if (words[0] != '~'):
					previous_type = ''
				if str(words[0]).lower() == 'new':
					type = words[1].split('.')[0]
					if(type == 'circuit'):
						result['common'] = {}
						result['common']['id'] = words[1].split('.')[1]
						previous_type = 'circuit'
						continue
					if(type == 'Transformer'):
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
							if(word.split('=')[0] == 'XHL' or word.split('=')[0] =='%r'):
								if "(" in operation_word:
									first = int(re.findall(r'\d+', operation_word)[0])
									# while ")" not in operation_word:
									second_word = words[index + 1]
									second = int(re.findall(r'\d+', second_word)[0])
									index = index + 1
								
								if (word.split('=')[0] == 'XHL'):
									trans['xsc_array']=(first/second)
								elif (word.split('=')[0] == '%r'):
									trans['percent_rs']=(first/second)
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
								
							if word != ' ' and word != '~' and word != '' and word!= '/':
								split_word = word.split('=')
								if (len(split_word) > 1):
									if not value_set:
										value = split_word[1]
									trans[split_word[0]] = value
						result['radials']['transformers'].append(trans)
						previous_type = 'Transformer'
						previous_index = len(result['radials']['transformers'])
					if(type == "linecode"):
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
				if (words[0] == '~' and previous_type == 'linecode'):
					word_set = ""
					previous_set = False
					val = []
					for index in range(len(words)):
						word = words[index]
						# operation_word = ''
						# value_set = False
						split_word = word.split('=')
						key = ""
						# line_dict = {}
						if(word == "rmatrix" or word == "xmatrix"):
							linecode[word] = []
							word_set = word
						if (len(split_word) > 1 and "" not in split_word):
							key = split_word[0]
							linecode[key] = split_word[1]
						if "(" in word or previous_set:
							previous_set = True
							if word == "|":
								linecode[word_set].append(val)
								val = []
							if(word == ')'):
								linecode[word_set].append(val)
								previous_set = False
							if(not word == '|' and not word == ')'):
								val.append(float(re.findall(r'(?:(?:\d*\.\d+)|(?:\d+\.?))', word)[0]))
						
				if(words[0]=='~' and previous_type == 'circuit'):
					for word in words[1:]:
						if(word.split('=')[0] == 'pu'):
							result['common']['per_unit'] = word.split('=')[1]
						elif word!=' ' and word!='~' and word!='':
							split_word = word.split('=')
							if(len(split_word) > 1):
								result['common'][split_word[0]] = split_word[1]
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
								first = float(re.findall(r'(?:(?:\d*\.\d+)|(?:\d+\.?))', operation_word)[0])
								# while ")" not in operation_word:
								second_word = words[index + 1]
								second = float(re.findall(r'(?:(?:\d*\.\d+)|(?:\d+\.?))', second_word)[0])
								index = index + 1
								value = first/second
								value_set = True
							if '[' in operation_word:
								elements = []
								operation_word = split_word[1]
								elements.append(float(re.findall(r'(?:(?:\d*\.\d+)|(?:\d+\.?))', operation_word)[0]))
								second_word = ''
								while ']' not in operation_word:
									operation_word = words[index + 1]
									if operation_word != '':
										elements.append(float(re.findall(r'(?:(?:\d*\.\d+)|(?:\d+\.?))', operation_word)[0]))
									index = index + 1
								value_set = True
								value = elements
							if (len(split_word) > 1):
								if not value_set:
									value = split_word[1]
								if not split_word[0] in result['radials']['transformers'][previous_index-1].keys():
									result['radials']['transformers'][previous_index - 1][split_word[0]] = []
								if isinstance(value, list):
									for v in value:
										result['radials']['transformers'][previous_index - 1][split_word[0]].append(v)
								else:
									result['radials']['transformers'][previous_index-1][split_word[0]].append(value)
					previous_type = 'Transformer'
					# previous_index = previous_index + 1
				cnt = len(words)
		print("***Result***")
		# print(json.dumps(result))
		print(result)
ob = dssToJson()
ob.convert()