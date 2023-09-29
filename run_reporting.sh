#!/bin/bash

source ~/.bashrc

cd ~/scalp_lab_reporting

# Run bonus-report pipeline
~/.conda/envs/py36/bin/python bonus_reporting/bonus_pipeline.py
# Run subject-report pipeline
~/.conda/envs/py36/bin/python subject_reporting/reporting_pipeline.py
