#!/bin/bash

# Error handler
set -e

# Environment
# Pre-instructions
export PYTHONPATH=/tmp/cwl-test//code/263259/HH_project/:/tmp/cwl-test//code/263259/HH_project/single_cell_models/:/home/fbonnier/.local/lib/python3.8/site-packages:/home/fbonnier/opt/nest-simulator-2.20.0/lib/python3.8/site-packages; pip3 install matplotlib numpy==1.20.3

# PIP list
pip3 list

# Start Watchdog
watchmedo shell-command --command='echo "${watch_src_path} ${watch_dest_path}" >> watchdog_log.txt' --patterns="*" --ignore-patterns='watchdog_log.txt' --ignore-directories --recursive /tmp/cwl-test/ & WATCHDOG_PID=$!;

# RUN
python3 /tmp/cwl-test//code/263259/HH_project/network_simulations/ntwk_sim_demo.py --CONFIG 'HH_RS--HH_FS--CONFIG1' --tstop 5000 -f /tmp/cwl-test//code/263259/HH_project/network_simulations/data/example.npy

# Stop Watchdog
kill -s 9 "${WATCHDOG_PID}";

