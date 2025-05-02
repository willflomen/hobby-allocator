#!/bin/bash

# Install required system packages
apt-get update
apt-get install -y coinor-cbc glpk-utils build-essential

# Force install PuLP to the global environment
pip install pulp==2.7.0 --upgrade --no-cache-dir

# Print diagnostic information
echo "PuLP installation complete"
echo "Python version: $(python --version)"
echo "PuLP location: $(pip show pulp | grep Location)"
echo "CBC solver location: $(which cbc || echo 'Not found')"
