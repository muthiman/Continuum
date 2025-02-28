# Distributed Consensus of Synchronised Time

A decentralized system for achieving consensus on time using GPS satellites and zero-knowledge proofs, without relying on a central authority.

## Overview

This system provides a trust-minimized approach to maintaining accurate time across a distributed network by:

1. Using GPS satellite data for initial time synchronization
2. Implementing zero-knowledge proofs for time validation
3. Leveraging BFT consensus for network-wide time agreement
4. Preventing replay attacks through cryptographic fingerprinting
5. Enabling real-time price discovery through ordered transactions

## Architecture

### Key Components

1. **GPS Module**
   - Receives signals from multiple satellites
   - Processes PRN codes and ephemeris data
   - Calculates precise timing information

2. **Secure Enclave**
   - Validates GPS module output
   - Runs ZK circuits for time verification
   - Generates cryptographic proofs

3. **Validation Engine**
   - Verifies time proofs from other nodes
   - Implements BFT consensus rules
   - Maintains accepted time ranges

4. **Network Layer**
   - Handles peer-to-peer communication
   - Propagates time proofs
   - Manages validator connections

5. **Data Availability Layer**
   - Stores validated time proofs
   - Maintains consensus history
   - Enables proof verification

### Security Model

- Minimum 4 satellites required for triangulation
- Network requires 400+ validators for security
- BFT consensus with 2/3 + 1 agreement
- Protection against replay attacks via fingerprinting
- Slashing conditions for malicious validators

## Requirements

- Python 3.8+
- GPS receiver module
- Rust and Cargo
- Node.js and npm
- Circom 2.0.0+

## Installation

1. **Clone the Repository**
```bash
git clone https://github.com/muthiman/Continuum.git
cd Continuum
```

2. **Install Prerequisites**
```bash
# Install Rust (for Circom)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"

# Install Circom
cargo install circom

# Install Node.js and npm (if not already installed)
# On macOS:
brew install node
# On Ubuntu:
# sudo apt install nodejs npm
```

3. **Run Setup Script**
```bash
chmod +x setup.sh
./setup.sh
```

4. **Verify Installation**
```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Run tests
python3 -m unittest tests/test_time_consensus.py -v
```

## Usage

### 1. Start the GPS Module
```python
from src.gps_module.gps_receiver import GPSReceiver

# Initialize GPS receiver
gps = GPSReceiver(port="/dev/ttyUSB0")  # Adjust port as needed
gps.start()

# Get satellite data
satellite_data = gps.get_satellite_data()
```

### 2. Generate Time Proofs
```python
from src.secure_enclave.zk_prover import ZKTimeProver

# Initialize prover
prover = ZKTimeProver()

# Generate proof
proof = prover.generate_proof(
    satellite_data=satellite_data,
    local_time=time.time()
)
```

### 3. Validate Time Proofs
```python
from src.validation.time_validator import TimeValidator

# Initialize validator
validator = TimeValidator()

# Verify proof
is_valid = validator.verify_proof(proof)
if is_valid:
    print("Time proof verified successfully!")
```

### 4. Run as Network Node
```bash
# Start validator node
python3 -m src.node.validator --port 8000 --peers peer1:8001,peer2:8002

# Start client node
python3 -m src.node.client --validator localhost:8000
```

## Security Considerations

1. **Trust Assumptions**
   - Minimum 4 non-colluding satellites
   - Sufficient network size for validator coverage
   - Honest majority of validators

2. **Attack Vectors**
   - Clock slowing attacks
   - Replay attacks
   - Validator collusion
   - GPS signal spoofing

3. **Mitigations**
   - Multi-satellite validation
   - Cryptographic proof verification
   - BFT consensus requirements
   - Slashing conditions for malicious behavior

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

- GitHub: [@muthiman](https://github.com/muthiman)
- Project Link: [https://github.com/muthiman/Continuum](https://github.com/muthiman/Continuum) 
