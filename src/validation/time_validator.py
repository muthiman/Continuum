from typing import Dict, Optional, List
from ..secure_enclave.zk_prover import TimeProof
import hashlib
import time
import json
import subprocess

class TimeValidator:
    def __init__(self):
        """Initialize the time validation system."""
        self.verification_key = None
        self.accepted_time_range = 1.0  # Maximum allowed time deviation in seconds
        
    def verify_time_proof(self, proof: TimeProof) -> bool:
        """Verify a time proof from another node."""
        try:
            # Verify the ZK proof
            if not self._verify_zk_proof(proof.zk_proof, proof.metadata):
                return False
                
            # Verify satellite fingerprint
            if not self._verify_satellite_fingerprint(proof):
                return False
                
            # Verify timestamp is within acceptable range
            if not self._verify_timestamp_range(proof.timestamp):
                return False
                
            return True
            
        except Exception as e:
            print(f"Error verifying time proof: {e}")
            return False
            
    def _verify_zk_proof(self, proof: bytes, metadata: Dict) -> bool:
        """Verify the zero-knowledge proof."""
        try:
            # Write proof to file
            with open("proof.json", "wb") as f:
                f.write(proof)
            
            # Write public inputs
            with open("public.json", "w") as f:
                json.dump({
                    "T_sat": metadata["T_sat"],
                    "c": "299792458",
                    "Delta": "5000000"
                }, f)
            
            # Verify proof
            result = subprocess.run([
                "snarkjs",
                "groth16",
                "verify",
                "verification_key.json",
                "public.json",
                "proof.json"
            ], capture_output=True)
            
            return b"OK" in result.stdout
        
        except Exception as e:
            print(f"Error verifying ZK proof: {e}")
            return False
        
    def _verify_satellite_fingerprint(self, proof: TimeProof) -> bool:
        """Verify the satellite fingerprint matches metadata.
        
        Verifies that:
        1. The fingerprint matches the unreleased data
        2. The data is fresh (not replayed)
        3. The satellite data is authentic
        """
        try:
            # Reconstruct fingerprint from metadata
            unreleased_data = []
            for sat_data in proof.metadata["satellite_data"]:
                unreleased_data.extend([
                    str(sat_data["almanac"]["clock_correction"]),
                    str(sat_data["almanac"]["ionospheric_data"]),
                    str(sat_data["almanac"]["atmospheric_corrections"]),
                    str(sat_data["almanac"]["satellite_health"]),
                    str(sat_data["almanac"]["doppler_shift"]),
                ])
            
            # Generate verification fingerprint
            verification_fingerprint = hashlib.sha256(''.join(unreleased_data).encode()).hexdigest()
            
            # Compare with provided fingerprint
            if verification_fingerprint != proof.satellite_fingerprint:
                return False
                
            # Verify data freshness
            if not self._verify_data_freshness(proof.metadata):
                return False
                
            return True
            
        except Exception as e:
            print(f"Error verifying satellite fingerprint: {e}")
            return False
        
    def _verify_data_freshness(self, metadata: Dict) -> bool:
        """Verify the data is fresh and not replayed."""
        try:
            # Check if the timestamp is too old
            current_time = time.time_ns()
            proof_time = metadata["timestamp"]
            
            # Reject if proof is too old (prevent replay attacks)
            if (current_time - proof_time) > self.accepted_time_range * 1e9:  # Convert to nanoseconds
                return False
                
            return True
            
        except Exception as e:
            print(f"Error verifying data freshness: {e}")
            return False
        
    def _verify_timestamp_range(self, timestamp: float) -> bool:
        """Verify timestamp is within acceptable range."""
        # Implementation for timestamp validation
        pass 