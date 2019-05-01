#!/usr/bin/python

import sys, getopt, re

input_file = ''
profanity_file = ''
profanity_list = []
output_success_file = ''
output_fail_file = ''
approved_sentences = set()

# Define custom exception
class ValidationFailure(Exception):
   pass
   
   
def runScript():
	global input_file,output_success_file,output_fail_file,profanity_file

	try:
		opts, args = getopt.getopt(sys.argv[1:],"i:p:o:of:",["input=","profanity-list=","output-success=","output-fail="])
	except getopt.GetoptError:
		print('sentence_validator.py -i <input file> [--profanity-list <file>] [--output-success <output file>] [-output-fail <output file>]')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print('sentence_validator.py -i <input file> [--profanity-list <file>] [--output-success <output file>] [-output-fail <output file>]')
			sys.exit()
		elif opt in ("-i", "--input"):
			input_file = arg
		elif opt in ("-p", "--profanity-list"):
			profanity_file = arg
		elif opt in ("-o", "--output-success"):
			output_success_file = arg
		elif opt in ("-of", "--output-fail"):
			output_fail_file = arg

	# Cache profanity
	if profanity_file:
		with open(profanity_file) as pf:  
			for line in pf:
				profanity_list.append(line.strip())

	# Open files for writing
	if output_success_file:
		f_success = open(output_success_file, "w")

	if output_fail_file:
		f_fail = open(output_fail_file, "w")

	# Scan sentences
	with open(input_file) as f:  
		for line in f:		
			try:
				# Tidy up sentence endings
				if line.endswith("!.") or line.endswith("?."):
					line = line[:-1]
				
				# Clean up quotes
				if line.count("\"") == 1:
					line = line.replace("\"","")

				# Replace abbreviated words
				line = expandAbbreviations(line)
			
				# Replace stylized symbols
				line = line.replace(u"\u2018","'")
				line = line.replace(u"\u2019","'")
				line = line.replace(u"\u0060","'")
				line = line.replace(u"\u00B4","'")
				line = line.replace(u"\u201C","\"")
				line = line.replace(u"\u201D","\"")
				line = line.replace(u"\u05BE","-")
				line = line.replace(u"\u2010","-")
				line = line.replace(u"\u2011","-")
				line = line.replace(u"\u2012","-")
				line = line.replace(u"\u2013","-")
				line = line.replace(u"\u2014","-")
				line = line.replace(u"\u2015","-")
								
				words = line.split()
				word_count = len(words)
				char_count = len(line)
			
				# Check for obviously truncated sentences
				last_word = words[-1].lower()
				sub_words = re.split(r'-|\.{3}',last_word) # Split on - or ...
				last_word = re.sub(r'[^[a-zA-Z.]','', sub_words[-1])
				
				if last_word == "e.g." or last_word == "i.e." or last_word == "a.k.a" or last_word == "no."\
				or last_word == "al." or last_word == "op.":
					raise ValidationFailure("partial sentence")
				
				# Check if too short or too long
				if char_count < 5 or char_count > 125 or word_count < 3 or word_count > 14:
					raise ValidationFailure("length")
					
				# Check if words are reasonable length
				for w in words:
					sub_words = re.split(r'-|\.{3}',w) # Split on - or ...
					
					for sw in sub_words:
						sw = re.sub(r'[^[a-zA-Z]','', sw)

						if len(sw) > 15:
							raise ValidationFailure("word length")
		
				# Check for non-English chars
				if re.search(r"[^a-zA-Z'\-,.!?:;() \"]", line) is not None:
					raise ValidationFailure("invalid chars")

				# Check if it starts with a capital letter
				first_char = line[0];
				if first_char != first_char.upper():
					raise ValidationFailure("partial sentence")

				if first_char == "'" or first_char == "\"":
					second_char = line[1];
					if second_char != second_char.upper():
						raise ValidationFailure("partial sentence")
						
				# Check if it starts with an obviously wrong character
				if first_char == "," or first_char == "." or first_char == ";" or first_char == ":" or first_char == "-":
					raise ValidationFailure("partial sentence")

				if len(line) > 2 and (line[:2] == ("' ") or line[:2] == ("\" ") or line[:2] == ("',")):
					raise ValidationFailure("partial sentence")
					
				# Check if it ends with valid punctuation
				last_char = line[-1];
				if not (last_char == "." or last_char == "!" or last_char == "?" or last_char == "'" or last_char == '"'):
					raise ValidationFailure("punctuation")
					
				# Look for missing words
				for w in words:
					if w == "\"\"" or w == "\"\"." or w == "\"\"," or w == "\"\";" or w == "\"\":" or w == "\"\"!"\
					or w == "\"\"?" or w == "'s" or w.startswith("??") or w.startswith("\"??"):
						raise ValidationFailure("missing word")
						
				if line.count(" over of ") > 0 or line.count(" on of ") > 0 or line.count(" with of ") > 0 \
				or line.count(" by of ") > 0 or line.count(" between of ") > 0 or line.count(" between and ") > 0 \
				or line.count(" and and ") > 0 or line.count(" of and ") > 0 or line.count(" of of ") > 0 \
				or line.count(" than and ") > 0 or line.count(" than of ") > 0 or line.count(" of but ") > 0 \
				or line.count(" about long ") > 0 or line.count(" about wide ") > 0 or line.count(" about tall ") > 0 \
				or line.count(" about short ") > 0 or line.count(" about thick ") > 0 or line.count(" about deep ") > 0 \
				or line.count(" approximately long ") > 0 or line.count(" approximately wide ") > 0 \
				or line.count(" approximately tall ") > 0 or line.count(" approximately short ") > 0 \
				or line.count(" approximately thick ") > 0 or line.count(" approximately deep ") > 0 \
				or line.count(" from in ") > 0 or line.count(" to in ") > 0 or line.count(" from inches ") \
				or line.count(" is in size ") > 0 or line.count(" than in size ") > 0 or line.count(" measures high ") > 0 \
				or line.count(" measures wide ") > 0 or line.count(" measures long ") > 0 or line.count(" measures in size ") > 0 \
				or line.count(" measuring in ") > 0 or line.count(" measuring between ") > 0 or line.count(" of per ") > 0:
						raise ValidationFailure("missing word")
					
				# Check for possible foreign terms (e.g. Persona y Sociedad)
				if containsForeignTerm(words):
						raise ValidationFailure("foreign term")
					
				# Check for profanity
				if containsProfanity(words):
					raise ValidationFailure("profanity")
					
				# Prevent long lists
				if line.count(",") > 4:
					raise ValidationFailure("long list")
					
				# Check for dupes
				if line in approved_sentences:
					raise ValidationFailure("duplicate sentence")

				# Validation successful
				approved_sentences.add(line)
				
				if output_success_file:
					f_success.write(line + "\n")
					
			except ValidationFailure as vf:
					print("Validation failed ({}): {}".format(vf,line))

					if output_fail_file:
						f_fail.write(line + "\n")

	# Close files
	if output_success_file:
		f_success.close()

	if output_fail_file:
		f_fail.close()


def expandAbbreviations(line):
	# Find and replace common terms
	line = line.replace("World War II","World War Two")
	line = line.replace("World War I","World War One")
	line = line.replace("Grade II","Grade Two")
	line = line.replace("Grade I","Grade One")
	line = line.replace("grade II","grade two")
	line = line.replace("grade I","grade one")
	line = line.replace("Type I","Type One")
	line = line.replace("Type II","Type Two")
	line = line.replace("type I","type one")
	line = line.replace("type II","type two")
	line = line.replace("Category I","Category One")
	line = line.replace("Category II","Category Two")
	line = line.replace("category I","category one")
	line = line.replace("category II","category two")
	line = line.replace(".com"," dot com")
	line = line.replace(".net"," dot net")
	line = line.replace(".org"," dot org")
	line = line.replace(".ie"," dot ie")
	line = line.replace(".co"," dot co")
	line = line.replace(".ac"," dot ac")
	line = line.replace(".uk"," dot uk")
	line = line.replace(".ca"," dot ca")
	line = line.replace(".fm"," dot fm")
	line = line.replace(".gov"," dot gov")
	line = line.replace("www.","www dot ")
	
	source_words = line.split()	
	out_words = [];
	
	for w in source_words:
		out_word = w
		
		if w == "&":
			out_word = "and"
		elif w.count("&") > 0:
			out_word = w.replace("&"," and ")
		elif w == "Jr" or w == "Jr." or w == "Jr.,":
			out_word = "Junior"
		elif w == "Sr" or w == "Sr." or w == "Sr.,":
			out_word = "Senior"
		elif w == "No." or w == "Nr.":
			out_word = "Number"
		elif w == "Nos.":
			out_word = "Numbers"
		elif w == "no.":
			out_word = "number"
		elif w == "Mt" or w == "Mt.":
			out_word = "Mount"
		elif w == "Mts.":
			out_word = "Mounts"
		elif w == "Bros" or w == "Bros.":
			out_word = "Brothers"
		elif w == "Bros," or w == "Bros.,":
			out_word = "Brothers,"
		elif w == "Bros\"" or w == "Bros.\"":
			out_word = "Brothers\""
		elif w == "Capt" or w == "Capt.":
			out_word = "Captain"
		elif w == "Col" or w == "Col.":
			out_word = "Colonel"
		elif w == "Lt" or w == "Lt.":
			out_word = "Lieutenant"
		elif w == "Sgt" or w == "Sgt.":
			out_word = "Sergeant"
		elif w == "Sgts" or w == "Sgts.":
			out_word = "Sergeants"
		elif w == "Gen.":
			out_word = "General"
		elif w == "Pt" or w == "Pt.":
			out_word = "Part"
		elif w == "pt" or w == "pt.":
			out_word = "part"
		elif w == "Fr" or w == "Fr.":
			out_word = "Father"
		elif w == "Rev" or w == "Rev.":
			out_word = "Reverend"
		elif w == "Vol" or w == "Vol.":
			out_word = "Volume"
		elif w == "\"Vol.":
			out_word = "\"Volume"
		elif w == "vol" or w == "vol.":
			out_word = "volume"
		elif w == "Ch.":
			out_word = "Chapter"
		elif w == "ch.":
			out_word = "chapter"
		elif w == "pp" or w == "pp.":
			out_word = "pages"
		elif w == "p.":
			out_word = "page"
		elif w == "Ex:":
			out_word = "Example:"
		elif w == "Rep" or w == "Rep.":
			out_word = "Representative"
		elif w == "Govt" or w == "Govt.":
			out_word = "Government"
		elif w == "Dr" or w == "Dr.":
			out_word = "Doctor"
		elif w == "Drs" or w == "Drs.":
			out_word = "Doctors"
		elif w == "ca.":
			out_word = "circa"
		elif w == "Ca.":
			out_word = "California"
		elif w == "Co.":
			out_word = "Company"
		elif w == "Hon.":
			out_word = "Honorable"
		elif w == "Inc." or w == "Inc.,":
			out_word = "Incorporated"
		elif w == "v." or w == "vs" or w == "vs.":
			out_word = "versus"
		elif w == "Vs.":
			out_word = "Versus"
		elif w == "Msgr" or w == "Msgr.":
			out_word = "Monsignor"
		elif w == "St" or w == "St.":
			out_word = "Saint"
		elif w == "Sts" or w == "Sts.":
			out_word = "Saints"
		elif w == "Ltd" or w == "Ltd.":
			out_word = "Limited"
		elif w == "Ave.":
			out_word = "Avenue"
		elif w == "Brgy." or w == "Bgy.":
			out_word = "Barangay"
		elif w == "Hr.":
			out_word = "Higher"
		elif w == "Corp" or w == "Corp.":
			out_word = "Corporation"
		elif w == "Pfc.":
			out_word = "Private first class"
		elif w == "approx.":
			out_word = "approximately"
		elif w == "Mtn.":
			out_word = "Mountain"
		elif w == "Mgmt.":
			out_word = "Management"
		elif w == "Vt.":
			out_word = "Vermont"
		elif w == "kg":
			out_word = "kilograms"
		elif w == "kg.":
			out_word = "kilograms."
		elif w == "km":
			out_word = "kilometers"
		elif w == "km.":
			out_word = "kilometers."
		elif w == "Wg.":
			out_word = "Wing"
		elif w == "Det.":
			out_word = "Detective"
		elif w == "Cllr" or w == "Cllr.":
			out_word = "Councillor"

		out_words.append(out_word)
		
	return " ".join(out_words)
	
def containsForeignTerm(words):
	for w in words:
		sub_words = re.split(r'-|\.{3}',w) # Split on - or ...
		for sw in sub_words:
			sw_unstripped = sw
			sw = re.sub(r'[^[a-zA-Z]','', sw)
			sw_lower = sw.lower()
			
			if sw_unstripped == "i" or sw_unstripped == "y" or sw_unstripped == "e" or sw_lower == "el" \
			or sw_lower == "le" or sw_lower == "ng" or sw == "les" or w == "de" or w == "un" or sw == "del" \
			or sw == "og" or sw_lower == "la" or sw == "ap" or sw == "ibn" or sw == "al" or sw == "das" \
			or sw == "et" or sw == "fu" or sw == "ga" or sw == "sur" or sw == "du" or sw == "aj" or sw == "ud" \
			or sw_lower == "ix" or sw_lower == "ich" or sw_lower == "zur" or sw == "und" or sw == "una" \
			or sw == "jou" or sw_lower == "que" or sw == "qui" or sw == "est" or sw_lower == "te" \
			or sw_lower == "tu" or sw_lower == "il" or sw_lower == "avec" or sw_lower == "vous" or sw_lower == "yr" \
			or sw == "ar" or sw == "al" or sw == "il" or sw_lower == "sa" or sw == "af" or sw == "auf" \
			or sw_lower == "na" or sw == "vi" or sw_lower == "ein" or sw_lower == "ist" or sw == "alte" \
			or sw_lower == "mon" or sw_lower == "lei" or sw == "ma" or sw_lower == "lui" or sw == "dos" \
			or sw == "mo" or sw_lower == "mi" or sw_lower == "moi" or sw_lower == "mon" or sw == "zu" \
			or sw == "mit" or sw_lower == "von" or sw_lower == "au" or sw == "des" or sw_lower == "je" or sw_lower == "ne" \
			or sw_lower.count("sz") > 0 or sw_lower.count("fj") > 0 or sw_lower.count("rrr") > 0:
				return True
			
			if len(sw_unstripped) > 2:
				prefix = sw[:2] if len(sw) > 2 else ""
				prefix_lower = prefix.lower()
				prefix_unstripped = sw_unstripped[:2]
				prefix_unstripped_lower = prefix_unstripped.lower()
				
				suffix = sw[-2] if len(sw) > 2 else ""
				suffix_lower = suffix.lower()
				suffix_unstripped = sw_unstripped[-2]
				suffix_unstripped_lower = suffix_unstripped.lower()

				if prefix_unstripped_lower == "l'" or prefix_unstripped_lower == "d'" or prefix_unstripped_lower == "q'" \
				or prefix_unstripped_lower == "j'" or prefix_unstripped_lower == "k'" or prefix_unstripped_lower == "b'" \
				or prefix_unstripped_lower == "z'" or prefix_unstripped_lower == "s'" \
				or prefix == "Hr" or prefix_lower == "tl" or prefix == "Rj" or prefix == "Ng" or prefix == "Nj" or prefix == "Hl" \
				or prefix == "Tx" or prefix_lower == "cv" or prefix == "Tk" or prefix == "Zh" or prefix == "Kt" \
				or prefix_lower == "lj" or prefix == "Kj" or prefix == "Bj" or prefix == "Hj" or prefix == "Dn" \
				or prefix == "Qe" or prefix_lower == "sv" or prefix_lower == "sz" or prefix_lower == "tz" \
				or prefix_lower == "dz" or prefix == "Rz" or prefix_lower == "bz" or prefix_lower == "Nz" \
				or prefix == "Mz" or prefix == "Ys" or prefix == "Mx" or prefix == "tx" or prefix == "Yx" \
				or prefix_lower == "ix" or prefix_lower == "gx" or prefix_lower == "lx" or prefix_lower == "xx" \
				or prefix == "Nx" or prefix == "Vs" or prefix == "Vr" or prefix == "Vh" or prefix == "Vv" or prefix_lower == "vn" \
				or prefix == "Kw" or prefix == "Kp" or prefix == "Ks" or prefix == "Kg" or prefix == "Kz" or prefix == "Kv" \
				or prefix == "Qw" or prefix == "Qo" or prefix == "Qh" or prefix_lower == "ql" or prefix == "Qv" \
				or prefix_lower == "qn" or prefix_lower == "wd" or prefix == "Wl" or prefix_lower == "wm" or prefix == "Zw" \
				or prefix == "Zr" or prefix == "Zs" or prefix_lower == "zd" or prefix == "Zv" or prefix == "Zb" \
				or prefix_lower == "zn" or prefix == "Zm" or prefix == "Pf" or prefix == "Hv" or prefix == "Gj" \
				or prefix == "Ts" or prefix_lower == "bw" or suffix == "kw" or suffix_unstripped == "'u" \
				or suffix_unstripped == "'e" or suffix_unstripped == "'a" or suffix_unstripped == "'i" \
				or suffix_unstripped == "'o" or suffix_unstripped == "'h" or suffix_unstripped == "'r":
					return True
			
	return False
	
def containsProfanity(words):
	for w in words:
		sub_words = re.split(r'-|\.{3}',w) # Split on - or ...
		
		for sw in sub_words:
			sw = re.sub(r'[^[a-zA-Z]','', sw)
			if profanity_list.count(sw.lower()) > 0:
				return True
			
	return False
	
runScript()

