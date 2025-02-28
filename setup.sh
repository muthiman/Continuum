#!/bin/bash

# Install Python dependencies
python3 -m pip install -r requirements.txt

# Install Node.js dependencies
npm install -g circom snarkjs

# Create necessary directories
mkdir -p src/secure_enclave/circuits
