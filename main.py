import os
import sys
import argparse
import json as json
import warnings
import re

def get_runscript_from_workflow (workdir, workflow_run, workflow_data):
    runscript_file = None
    if (workflow_run):
        pass
    return runscript_file 

def get_runscript_from_code (workdir, environment, pre_instruction, instruction):
    runscript_file = None

    # Create runscript_file
    runscript_file = open (str(workdir) + "/run_me.sh", "w")
    runscript_file.write("#!/bin/bash\n\n")

    # Set error handler: if any command returns other value than exit(0) in the script, stops the script
    runscript_file.write("# Error handler\n")
    runscript_file.write("set -e\n\n")

    # Prepare environment
    # TODO
    runscript_file.write("# Environment\n")

    # Pre-instructions
    # Raw instructions, no classification with untar, compile, move, install, post-install ...
    runscript_file.write("# Pre-instructions\n")
    # for ipreinstr in pre_instruction:
    runscript_file.write(str(pre_instruction) + "\n\n")

    runscript_file.write("# PIP list\n")
    runscript_file.write("pip3 list\n\n")
    
    # Download inputs
    # runscript_file.write("# Inputs\n")
    # for iinput in inputs:
        # runscript_file.write("wget -N " + str(iinput['url']) + " " + str(iinput['path']) + "\n\n")

    # Start watchdog
    runscript_file.write("# Start Watchdog\n")
    runscript_file.write("watchmedo shell-command --command='echo \"${watch_src_path} ${watch_dest_path}\" >> watchdog_log.txt' --patterns=\"*\" --ignore-patterns='watchdog_log.txt' --ignore-directories --recursive " + str(workdir) + " & WATCHDOG_PID=$!;\n\n")

    # Run
    runscript_file.write("# RUN\n")
    runscript_file.write(str(instruction) + "\n\n")

    # Stop Watchdog
    runscript_file.write("# Stop Watchdog\n")
    runscript_file.write("kill -s 9 \"${WATCHDOG_PID}\";\n\n")

    # Extract watchdog files and add output files to JSON report
    # runscript_file.write("# Extract watchdog files and add output files to JSON report\n")
    # runscript_file.write("hbp_extract_watchdog --json " + str (json_file) + " --watchdog watchdog_log.txt;\n\n")

    # Close file
    runscript_file.close()

    return runscript_file

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate HBP model instance runscript from metadata JSON file")

    parser.add_argument("--json", type=argparse.FileType('r'), metavar="JSON Metadata file", nargs=1, dest="json", default="",\
    help="JSON File that contains Metadata of the HBP model to run")

    args = parser.parse_args()


    # Load JSON data
    json_file = args.json[0]
    if not json_file:
        print ("Fatal Error:  Invalid JSON File, please give a valid JSON file using \"--json <path-to-file>\"")
        exit(1)
    json_data = json.load(json_file)

    # Load workdir
    workdir = json_data["Metadata"]["workdir"]

    # Load workflow
    workflow_run_file = json_data["Metadata"]["workflow"]["run"]
    workflow_data_file = json_data["Metadata"]["workflow"]["data"]

    # Load inputs
    # inputs = json_data["Metadata"]["run"]["inputs"]

    # Load outputs
    # outputs = json_data["Metadata"]["run"]["outputs"]

    # Load environment
    environment = json_data["Metadata"]["run"]["environment"]

    # Load pre-instruction
    pre_instruction = json_data["Metadata"]["run"]["pre-instruction"]

    # Load code
    # code = { "url": json_data["Metadata"]["run"]["code"]["url"], "path": json_data["Metadata"]["run"]["code"]["path"]}

    # Load instruction
    instruction = json_data["Metadata"]["run"]["instruction"]

    runscript_file = None

    # Write runscript file from workflow
    runscript_file = get_runscript_from_workflow (workdir, workflow_run_file, workflow_data_file)

    # Write runscript file from runscript
    if (not runscript_file):
        runscript_file = get_runscript_from_code (workdir, environment, pre_instruction, instruction)

    sys.exit()
