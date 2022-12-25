import textwrap
import frida
import os
import sys
import frida.core
import core.dumper as dumper
import argparse
import logging
import time
from utils import misc, Utils




# Main Menu
def MENU():
    parser = argparse.ArgumentParser(
        prog='fridawizz',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(""))

    parser.add_argument('process',
                        help='the process that you will be injecting to')
    parser.add_argument('-o', '--out', type=str, metavar="dir",
                        help='provide full output directory path. (def: \'dump\')')
    parser.add_argument('-U', '--usb', action='store_true',
                        help='device connected over usb')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='verbose')
    parser.add_argument('-r', '--read-only', action='store_true',
                        help="dump read-only parts of memory. More data, more errors")
    parser.add_argument('-s', '--strings', action='store_true',
                        help='run strings on all dump files. Saved in output dir.')
    parser.add_argument('--max-size', type=int, metavar="bytes",
                        help='maximum size of dump file in bytes (def: 20971520)')
    parser.add_argument('-D', '--device', type=str, metavar='id',
                        help='connect to device with the given id')
    parser.add_argument('-H', '--host', type=str, metavar="host", 
                        help='remote device connected over tcp') 
    args = parser.parse_args()
    return args


arguments = MENU()
print(misc.logo())

# Define Configurations
APP_NAME = arguments.process
DIRECTORY = ""
USB = arguments.usb
DEBUG_LEVEL = logging.INFO
STRINGS = arguments.strings
MAX_SIZE = 20971520 # max integer value python
PERMS = 'rw-'
DEVICE = arguments.device
HOST = arguments.host # TODO

if arguments.read_only:
    PERMS = 'r--'

if arguments.verbose:
    DEBUG_LEVEL = logging.DEBUG
logging.basicConfig(format='%(levelname)s:%(message)s', level=DEBUG_LEVEL)


# Start a new Session


session = None

try:
    if USB:
        # if len(HOST) > 0:
        #     device_manager = frida.get_device_manager()
        #     device = device_manager.add_remote_device(HOST)
        #     pid = device.spawn([APP_NAME])
        #     device.resume(pid)
        #     session = frida.get_usb_device().attach(pid)
        device =  frida.get_usb_device()
        pid = device.spawn([APP_NAME])
        device.resume(pid)
        time.sleep(3) # LOL some apps ;p
        session = frida.get_usb_device().attach(pid)
    elif DEVICE:
        session = frida.get_device(DEVICE).attach(APP_NAME)
    else:
        session = frida.attach(APP_NAME)
except Exception as e:
    print("Can't connect to App. Have you connected the device?")
    logging.debug(str(e))
    sys.exit()


# Selecting Output directory
if arguments.out is not None:
    DIRECTORY = arguments.out
    if os.path.isdir(DIRECTORY):
        print("Output directory is set to: " + DIRECTORY)
    else:
        print("The selected output directory does not exist!")
        sys.exit(1)

else:
    print("Current Directory: " + str(os.getcwd()))
    DIRECTORY = os.path.join(os.getcwd(), "dump")
    print("Output directory is set to: " + DIRECTORY)
    if not os.path.exists(DIRECTORY):
        print("Creating directory...")
        os.makedirs(DIRECTORY)

mem_access_viol = ""

print("Starting Memory dump...")

script = session.create_script(
    """'use strict';

    rpc.exports = {
      enumerateRanges: function (prot) {
        return Process.enumerateRangesSync(prot);
      },
      readMemory: function (address, size) {
        return Memory.readByteArray(ptr(address), size);
      }
    };

    """)
script.on("message", Utils.on_message)
script.load()

agent = script.exports
ranges = agent.enumerate_ranges(PERMS)

if arguments.max_size is not None:
    MAX_SIZE = arguments.max_size

i = 0
l = len(ranges)

# Performing the memory dump
for range in ranges:
    base = range["base"]
    size = range["size"]

    logging.debug("Base Address: " + str(base))
    logging.debug("")
    logging.debug("Size: " + str(size))

    if size > MAX_SIZE:
        logging.debug("Too big, splitting the dump into chunks")
        mem_access_viol = dumper.splitter(
            agent, base, size, MAX_SIZE, mem_access_viol, DIRECTORY)
        continue
    mem_access_viol = dumper.dump_to_file(
        agent, base, size, mem_access_viol, DIRECTORY)
    i += 1
    Utils.printProgress(i, l, prefix='Progress:', suffix='Complete', bar=50)
print("")

# Run Strings if selected

if STRINGS:
    files = os.listdir(DIRECTORY)
    i = 0
    l = len(files)
    print("Running strings on all files:")
    for f1 in files:
        Utils.strings(f1, DIRECTORY)
        i += 1
        Utils.printProgress(i, l, prefix='Progress:', suffix='Complete', bar=50)
    aws = input("[*] Would you like to find juicy information wih regex patterns: (Y/n)")
    if aws.lower()[0] == 'y':
        Utils.inspec(DIRECTORY)
    else:
        print("[*] Thanks for using this tool! <3")
        print("Finished!")
        sys.exit(0)