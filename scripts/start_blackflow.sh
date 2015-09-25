#!/usr/bin/env bash
cd ../
export PYTHONPATH=./
python blackflow/bin/blackflow_service.py -c examples/config/blackflow_config.json -a apps