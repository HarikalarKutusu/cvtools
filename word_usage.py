#!/usr/bin/python

import sys, getopt, re
from collections import defaultdict

input_file = ''
dictionary_file = ''
limit = 0

try:
	opts, args = getopt.getopt(sys.argv[1:],"i:d:l",["input=","dictionary=","limit="])
except getopt.GetoptError:
	print('word_usage.py -i <input file> [-d <dictionary>] [--limit x]')
	sys.exit(2)

for opt, arg in opts:
	if opt == '-h':
		print('word_usage.py -i <input file> [-d <dictionary>] [--limit x]')
		sys.exit()
	elif opt in ("-i", "--input"):
		input_file = arg
	elif opt in ("-d", "--dictionary"):
		dictionary_file = arg
	elif opt in ("-l", "--limit"):
		limit = int(arg)

word_dict = defaultdict(int)

# Scan sentences
with open(input_file) as f:  
	for line in f:		
		words = line.lower().split()
		
		for w in words:
			# Filter out symbols
			w = re.sub('[^a-zA-Z\u00c0-\u024f\u1e00-\u1eff\']', '', w)
		
			# Ignore apostrophes at start or end
			if len(w) > 1 and w[:1] == "'":
				w = w[1:]
				
			if len(w) > 1 and w[-1] == "'":
				w = w[:-1]
		
			if len(w) > 0:
				val = word_dict[w]
				val += 1
				word_dict[w] = val

# Scan dictionary if the user specified it (assumes one word per line)
if dictionary_file:
	with open(dictionary_file) as f:  
		for line in f:	
			line = line.lower()
			
			# Filter out symbols
			line = re.sub('[^a-zA-Z\u00c0-\u024f\u1e00-\u1eff\']', '', line)
		
			if len(line) > 0:
				# Add word if it doesn't exist
				val = word_dict[line]
				word_dict[line] = val

# Now sort by alphabetical order of word
sorted_words = sorted(word_dict.items(), key=lambda x:x[0]);

# Sort words by most to least frequent
sorted_words = sorted(sorted_words, key=lambda x:x[1], reverse=True);

# Set limit if specified
if limit > 0 and len(sorted_words) > limit:
	sorted_words = sorted_words[:limit]

for word,num in sorted_words:
	print("{} {}".format(word,num))
