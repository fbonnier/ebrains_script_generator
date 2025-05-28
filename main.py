import os
import sys
import argparse
import json as json
import warnings
import re

known_machine_confs = { "default":{
                                "job scheduler": ["slurm"],
                                "container manager": ["singularity"],
                                "partition" : ["mem", "cpu_long"],
                                "n_nodes": 2},
                        "jusuf":{
                                "job scheduler": ["slurm"],
                                "container manager": ["singularity"],
                                "partition" : ["mem", "cpu_long"],
                                "n_nodes": 2},
                        "ruche":{
                                "job scheduler": ["slurm"],
                                "container manager": ["singularity"],
                                "partition" : ["mem", "cpu_long"],
                                "n_nodes": 2},
                        "spinnaker":{
                                "job scheduler": ["job manager"],
                                "container manager": [""],
                                "partition" : [""],
                                "n_nodes": 1}
                    }

def generate_cwl_script (model_id):
    cwl_me = None

    # Create cwl_file
    cwl_me = open (str(workdir) + "/run_me.cwl", "w")

    # Write the body of the CWL file
    body = """cwlVersion: v1.0
class: CommandLineTool
baseCommand: sbatch
requirements:
  - class: DockerRequirement
    dockerPull: docker-registry.ebrains.eu/ebrains-model-verification/docker-"""+model_id+""":latest
inputs:
  runme_file:
    type: File
    inputBinding:
      position: 1
      prefix: " "
  code_folder:
    type: Directory
    inputBinding:
      position: 2
      prefix: " "
outputs:
  watchdog_log:
    type: File
    outputBinding:
      glob: "./watchdog_log.txt"
  output_folder:
    type: Directory
    outputBinding:
      glob: "./outputs"
"""
    cwl_me.write(body)


def generate_input_yml (machine_config):
    input_me = None
    
    # Write the body of the YML file
    body = "runme_file: run_me.sh\n"
    body += "code_folder: code\n"
    
    ##### WRITE BODY #####
    try:
        # Create input_file
        input_me = open (str(workdir) + "/input_me.yml", "w")
        # Write the body of the YML file
        input_me.write(body)
        input_me.close()
    except Exception as e:
        print (e)
        print ("Error in creating input_me.yml file")
        sys.exit(1)



def generate_sbatch (machine_config):
    srun_me = None

    # Create srunscript_file
    srun_me = open (str(workdir) + "/srun_me.sh", "w")

    # Write the head of the file according to machine config
    srun_me.write("#!/bin/bash\n\n")
    if machine_config["account"]: srun_me.write("#SBATCH --account=" + machine_config["account"] + "\n")
    if machine_config["user mail"]:
        srun_me.write("#SBATCH --mail-user=" + machine_config["user mail"] + "\n")
        srun_me.write("#SBATCH --mail-type=all\n")
    if machine_config["partition"]: srun_me.write("#SBATCH --partition="+machine_config["partition"] + "\n")
    srun_me.write("#SBATCH --wait\n")
    if machine_config["n_nodes"]: srun_me.write("#SBATCH --nodes=" + machine_config["n_nodes"] + "\n")
    # if machine_config["container manager"]: runscript_file.write("--"+machine_config["container manager"])
    srun_me.write("\n\n")

    # Prepare environment
    srun_me.write("# Environment\n")
    
    # Write modules to load after a purge
    srun_me.write("# Modules\n")
    srun_me.write("module purge\n")
    
    if machine_config["modules"]:
        for imodule in machine_config["modules"]:
            srun_me.write("module load " + imodule)
    
    # # Pre-instructions
    # # Raw instructions, no classification with untar, compile, move, install, post-install ...
    # runscript_file.write("# Model Pre-instructions\n")
    # # for ipreinstr in pre_instruction:
    # if pre_instruction:
    #     runscript_file.write(str(pre_instruction) + "\n\n")

    # runscript_file.write("# PIP modules to install\n\n")
    # # runscript_file.write("pip3 list\n\n")

    # SRun and wait till the script ends
    model_id = int(0)
    outputdir = str(workdir) + "/output-" + model_id
    cwl_runscript = "run_model-" + model_id + ".cwl"
    inputs_file = str(workdir) + "/input_me.yml"
    srun_me.write("# SRUN\n")
    srun_me.write(str("srun --wait cwltool --outputdir" + outputdir + " " + cwl_runscript + " " + inputs_file) + "\n\n")

    # Close file
    srun_me.close()

    return srun_me

# Check if the machine configuration is supported
def check_machine_conf (machine_conf):
    
    pass

def get_machine_conf (machine_config_file=None):
    machine_config = {}
    if machine_config_file:
        # Load configuration JSON file
        try:
            json_data = json.load(json_file)
        except Exception as e:
            print (e)
            print ("Error in reading machine configuration file")
        try:    
            machine_config["machine"] = json_data["machine"]
            if machine_config["machine"] in known_machine_confs.keys():
                machine_config["container manager"] = json_data["container manager"]
            else:
                print("Machine configuration unknown -- Loding default configuration file")
                
            machine_config["partition"] = json_data["partition"]
            machine_config["modules"] = json_data["modules"]
            machine_config["n_nodes"] = json_data["n_nodes"]
            machine_config["account"] = json_data["account"]
            machine_config["user mail"] = json_data["user mail"]
            machine_config["pre-instructions"] = json_data["pre-instructions"]
        except Exception as e:
            print(e)
            print("Machine configuration file not recognized\nGet default machine configuration\n")
            machine_config = get_machine_conf("default")
    else: pass
    return machine_config
         

def get_runscript_from_workflow (workdir, workflow_run, workflow_data):
    runscript_file = None
    if (workflow_run):
        pass
    return runscript_file 

def generate_runscript_from_code (workdir=".", environment=None, pre_instruction=None, instruction="run", outputs_folder_path="."):
    runscript_file = None

    # Create runscript_file
    runscript_file = open (str(workdir) + "/run_me.sh", "w")

    # Write the head of the file according to machine config
    runscript_file.write("#!/bin/bash\n\n")
    
    # Set error handler: if any command returns other value than exit(0) in the script, stops the script
    runscript_file.write("# Error handler\n")
    runscript_file.write("set -e\n\n")

    # # Export workdir to enable env variable in the script or model inputs
    # runscript_file.write("# Enable Workdir variable\n")
    # runscript_file.write("export WORKDIR=" + str(workdir) + "\n\n")

    # Prepare environment
    # TODO
    runscript_file.write("# Environment\n")
    
    # Pre-instructions
    # Raw instructions, no classification with untar, compile, move, install, post-install ...
    runscript_file.write("# Model Pre-instructions\n")
    # for ipreinstr in pre_instruction:
    if pre_instruction:
        runscript_file.write(str(pre_instruction) + "\n\n")

    runscript_file.write("# PIP modules to install\n\n")
    # runscript_file.write("pip3 list\n\n")

    # Start watchdog
    runscript_file.write("# Start Watchdog\n")
    runscript_file.write("watchmedo shell-command --command='echo \"${watch_src_path} ${watch_dest_path}\" >> " + str(workdir) + "watchdog_log.txt' --patterns=\"*\" --ignore-patterns=watchdog_log.txt;run_stderr.txt;run_stdout.txt --ignore-directories --recursive " + str(outputs_folder_path) + " & WATCHDOG_PID=$!;\n\n")

    # Run
    runscript_file.write("# RUN\n")
    if instruction:
        runscript_file.write(str(instruction) + "\n\n")


    # Stop Watchdog
    runscript_file.write("# Stop Watchdog\n")
    runscript_file.write("kill -s 9 \"${WATCHDOG_PID}\";\n\n")

    # Close file
    runscript_file.close()

    return runscript_file

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate HBP model instance runscript from metadata JSON file")

    parser.add_argument("--json", type=argparse.FileType('r'), metavar="JSON Metadata file", nargs=1, dest="json", default="",\
    help="JSON File that contains Metadata of the HBP model to run")

    parser.add_argument("--outputdir", type=str, metavar="Outputs Directory", nargs=1, dest="outputdir", default="",\
    help="Directory where outputs will be stored and where the watchdog will look at")

    # parser.add_argument("--machine", type=argparse.FileType('r'), metavar="JSON machine configuration file", nargs='?', dest="machine", default="", required=False\
    # help="JSON File that contains targeted configuration parameters")

    args = parser.parse_args()


    # Load JSON data
    json_file = args.json[0]
    if not json_file:
        print ("Fatal Error:  Invalid JSON File, please give a valid JSON file using \"--json <path-to-file>\"")
        exit(1)
    json_data = json.load(json_file)

    # Load output directory
    outputdir = args.outputdir[0] if args.outputdir else "."

    # Load Machine configuration file
    

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

    # Get machine configuration
    # TODO
    # machine_config_file = None
    # try:
    #     machine_config_file = args["machine"]
    # except Exception as e:
    #     print(e)

    # # Check if the machine configuration is supported
    # check_machine_conf (machine_config_file=machine_config_file)
    # machine_config = get_machine_conf(machine_config_file=machine_config_file)
    
    # # Write sbatch file
    # sbatch_file = generate_sbatch (machine_config)

    # Write runscript file from workflow
    runscript_file = get_runscript_from_workflow (workdir, workflow_run_file, workflow_data_file)

    # Write runscript file from runscript
    if (not runscript_file):
        runscript_file = generate_runscript_from_code (workdir, environment, pre_instruction, instruction, outputs_folder_path=".")
    
    sys.exit()
