#!/bin/bash

# Activate virtual environment containing dependencies
source "./venv/bin/activate"

# Set Flask variables for running app
export FLASK_APP=top_app
export FLASK_ENV=development

# Run the app
pip install -e .
flask run
