import os
import logging
import sys
import hashlib

# Reading bytes from session and saving it to a file

def dump_to_file(agent,base,size,error,directory):
        try:
                filename = str(base)+'_dump.data'
                dump =  agent.read_memory(base, size)
                f = open(os.path.join(directory,filename), 'wb')
                f.write(dump)
                f.close()
                return error
        except Exception as e:
            logging.debug("[!]"+str(e))
            print("[*] memory access violation!")
            return error

def regex_dump_file(directory, finding):
    try:
        with open(os.path.join(directory,'regex_findings.txt'), 'a') as f:
            write_line = finding + '\n'
            f.writelines(write_line)
    except Exception as e:
        logging.debug(f"[!] {e}")
        print(f"[!] error while saving regex findings {e}")
        sys.exit(1)
    

    ## remove duplicates
    input_file_path = os.path.join(directory,'regex_findings.txt')
    out_file_path = os.path.join(directory,'regex_findings_uniq.txt')

    complete_line_hash = set()
    out_file = open(out_file_path, "w")
    for line in open(input_file_path, "r"):
        hash_value = hashlib.md5(line.rstrip().encode('utf-8')).hexdigest()
        if hash_value not in complete_line_hash:
            out_file.write(line+'\n')
            complete_line_hash.add(hash_value)
    out_file.close()



#Read bytes that are bigger than the max_size value, split them into chunks and save them to a file

def splitter(agent,base,size,max_size,error,directory):
        #times = size//max_size
        times = int(size/max_size) #fix where times is not a number
        diff = size % max_size
        if diff is 0:
            logging.debug("Number of chunks:"+str(times+1))
        else:
            logging.debug("Number of chunks:"+str(times))
        global cur_base
        cur_base = int(base,0)

        for time in range(int(times)):
                logging.debug("Save bytes: "+str(cur_base)+" till "+str(cur_base+max_size))
                dump_to_file(agent, cur_base, max_size, error, directory)
                cur_base = cur_base + max_size

        if diff is not 0:
            logging.debug("Save bytes: "+str(hex(cur_base))+" till "+str(hex(cur_base+diff)))
            dump_to_file(agent, cur_base, diff, error, directory)

