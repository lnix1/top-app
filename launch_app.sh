#!/bin/bash

# Create and activate virtual environment
python3 -m venv venv
source "./venv/bin/activate"

# Install dependencies to the virtual environment
pip3 install -r requirements.txt

# Set Flask variables for running app
export FLASK_APP=top_app
export FLASK_ENV=development

# Run the app locally
pip install -e .
flask run
