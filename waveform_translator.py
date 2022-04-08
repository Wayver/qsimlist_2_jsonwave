import os
import sys

###########################
# howto
# this script currently takes 3 arguments
# 1) name of input .lst file (signals should be added to list with -nodelta argument when creating it in questa)
# 2) name of desired output file
# 3) clock period of simulation in PICOSECONDS 

# for example:
# python waveform_translator.py sample_list.lst best_ever_output.json 2000

# the generated output waveform does not currently add a clock
# in the future a clock may be used to obviate the need for 
# users to pass in the clock period, but not now
# minor instructions for dealing with the clock appear at the end of this file
############################

###########
# how will this work?

# plan to reformat list into workable data:

# 1) split the names from the time entries

# 2) break each data line up so that the transition times and value can be
# matched with the apporpriate signal name

# 3) translate the data into a format that wavedrom can understand

# unless this info can be included in the questa list output somehow . . .
# user will need to pass it in in PICOSECONDS
clock_period = sys.argv[3]

def Sort(sub_li):
  return(sorted(sub_li, key = lambda x: x[1]))

# function to parse input file, get the unique signal names, and match the data from each column
# it reads in a .lst file, and modifies an input dictionary and list to store:
# 	a) a dictionary with timestamps from the .lst as keys
#       b) a list of unique signal names paired with column # info so they can be sorted  
def reformat_input(target_file,time_dict,signal_names):
  with open(target_file) as file:
    orig = file.readlines()
    for line in orig:
    # this script was written from a catapult/scverify perspective
      if "/" in line:
        potential_signals = line.split()
        for block in potential_signals:    
          if "/" in block:
            var_name = block.split("/")[-1]
             # need to order the signal names columnwise, since questa .lst does not order them "normally"
             # lets "find" the substring and add the length of the substring to the found start index,
            if var_name not in signal_names:
              signal_names.append([var_name,line.find(var_name)+len(var_name)])

      else:
        data = line.split()
        if int(data[0]) > int(myend_time):
          print(data[0],myend_time)
          break
        if int(data[0]) % int(clock_period) > 0:
          continue
        if data[0] not in time_dict:
          #print("adding ",data[0])
          time_dict[int(data[0])] = {}
           # order by descending
          for idx,signal in enumerate(Sort(signal_names)):
            time_dict[int(data[0])][signal[0].strip()] = data[idx+1].strip() 
  file.close()

# convert the actual values of the signals for output to wavedrom
# currently this is hardcoded for hexadecimal radix
def txt_2_num(orig):
  if True:
  #try:
    if "'" in orig: 
      parts = orig.split("'")
      if parts[1][0] == 'h' and 'x' not in parts[1] and 'X' not in parts[1]:
        mini = parts[1].strip()
        if len(mini) == 2:
          return(int(mini[1],16))
        elif len(mini) > 2:
          return(int(mini[1:len(mini)],16))
    # handle x values, data labels of 'x' are currently shown instead of crosshatching
    # this could be improved
      if 'x' or 'X' in parts[1]:
        return('x')
    if "'" not in orig:
      if orig == "U":
        return 'x'
      else:
        return orig
#  except:
#    print(orig)

# function that takes in dictionary of times, and a signal name, and returns the
# waveform and data label strings in a two element list
def wvdrm_write_signals(g_record, my_signal):
  output = []
  output.append("")
  complete_signal = ""
  data_names = []
  prev_signal = 'zzzz'
  keyList = sorted(g_record.keys())
  # signal name fragments used to identify signals that contain data, as opposed to just high/low
  data_signals = ['dat','count','sig']
  # default value of times to add a signal value to the string 
  repeater = 1
	
  last = False
  
  for i,v in enumerate(keyList):
    # we need to repeat the signal in "wave" string of the json file
    # depending on the interval between this timestamp and the next, but
    # we need to handle trying to reach for the timestamp beyond the end of our range
    
    #print(i,v)
    try:
        
      a = keyList[i+1]-keyList[i]
      repeater = a/int(clock_period)*2
     
    except:
      last = True
		
    new_value = str(txt_2_num(g_record[v][my_signal[0]]))
	
    # loop to pad the "wave" string with the calculated "repeater"	
    for x in range(int(repeater)):
      #if my_signal[0].split("_")[-1] != 'dat': 
      if my_signal[0].split("_")[-1] not in data_signals: 
        if prev_signal == new_value:
          complete_signal += "."
        else:
          complete_signal +=  new_value
        prev_signal = new_value

      # we want to store labels for the data signals, but we only want one label
      # per unique data element ("unique" only in the sense that i-1 and i+1 are different)
      #if my_signal[0].split("_")[-1] == 'dat': 
      if my_signal[0].split("_")[-1] in data_signals:
        #print(my_signal[0].split("_")[-1])  
        if prev_signal == new_value:
          complete_signal += "."
        else:
          complete_signal += "="
          if x == 0:
            data_names.append(new_value)
        prev_signal = new_value
		
  output[0] = complete_signal
  output.append(data_names)
  return output

######################################################
# main body of script begins
######################################################	
record = {}
signals = []

myinput = sys.argv[1]
myoutput = sys.argv[2] 
if len(sys.argv) > 3:
  myend_time = sys.argv[4] 
else:
  myend_time = 1000000000
#reformat_input("./noduplicate_list.lst",record,signals)
reformat_input(myinput,record,signals)

signals = Sort(signals)

# assemble the parts of the signal
output_signals = []
sig_count = 0

for signal in signals:
  output_signals.append(["",""])
  signal_text = ""
  data_arr = wvdrm_write_signals(record,signal)
  if data_arr[1] == []:
    signal_text += "name: '" + signal[0] + "', wave: '" + data_arr[0] + "'"
    output_signals[sig_count][0] = signal_text 
	
  # check if this is a data signal that needs to be paired with values
  if data_arr[1] != []:
    #print(signal)
    dat_string = "["
    for dvalue in data_arr[1]:
      dat_string += "'" + dvalue + "', "
    dat_string = dat_string[:-2]
    dat_string += "]"
    output_signals[sig_count][1] = dat_string

    signal_text += "name: '" + signal[0] + "', wave: '" + data_arr[0] + "'"
    output_signals[sig_count][0] = signal_text 

  sig_count += 1
 
# combine the signal and data strings when applicable
light_at_the_end = "{ signal: [ \n" 

for final_lines in output_signals:
  # not a data signal, no need to add data labels  
  if final_lines[1] == "":
    light_at_the_end += "  {"+final_lines[0]+"},\n"
  # add labels for data
  else:
    light_at_the_end += "  {"+final_lines[0] + ", data: " + final_lines[1]+"},\n"

light_at_the_end = light_at_the_end[:-2]
light_at_the_end += "\n]}"	

# in the current form, this output json requires the manual
# additon of clk signals, and periods, specify the clock with a period 2x as long as the 
# other signals (as far as wavedrom knows) in order to ensure that signals can be
# depicted accurately as changing at times not on clock edges
new_file = open(myoutput,"w")
new_file.write(light_at_the_end)
