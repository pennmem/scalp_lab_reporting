#!/bin/bash

source ~/.bashrc

cd ~/scalp_lab_reporting

# Update records of recently modified sessions
~/.conda/envs/py36/bin/python identify_modified_participants.py

