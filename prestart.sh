#!/bin/bash

# Create commands, this should only be ran via docker since it requires environment variables to be set
python -c 'import scripts; scripts.create_commands()' global