import unittest
import os
import subprocess
from src.gps_module.gps_receiver import GPSReceiver, SatelliteData
from src.secure_enclave.zk_prover import ZKTimeProver
from src.validation.time_validator import TimeValidator

class TestTimeConsensus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the Circom circuit and trusted setup."""
        # Get absolute paths
        root_dir = os.path.dirname(os.path.dirname(__file__))
        os.chdir(root_dir)
        
        circom_path = os.path.expanduser("~/.cargo/bin/circom")
        circuit_path = os.path.join(root_dir, "src/secure_enclave/circuits/SatelliteTimeCheck.circom")
        
        # Compile the circuit
        print("Compiling Circom circuit...")
        subprocess.run([
            circom_path,
            "--r1cs",
            "--wasm",
            "--sym",
            "--c",
            circuit_path
        ], check=True)
        
        # Generate trusted setup (for testing only)
        print("Generating trusted setup...")
        subprocess.run([
            "snarkjs",
            "powersoftau",
            "new",
            "bn128",
            "12",
            "pot12_0000.ptau",
            "-v"
        ], check=True)
        
        subprocess.run([
            "snarkjs",
            "powersoftau",
            "contribute",
            "pot12_0000.ptau",
            "pot12_0001.ptau",
            "--name='First contribution'",
            "-v",
            "-e='some random text'"
        ], check=True)
        
        # Generate proving/verification keys
        subprocess.run([
            "snarkjs",
            "groth16",
            "setup",
            "SatelliteTimeCheck.r1cs",
            "pot12_0001.ptau",
            "SatelliteTimeCheck.zkey"
        ], check=True)
        
        subprocess.run([
            "snarkjs",
            "zkey",
            "export",
            "verificationkey",
            "SatelliteTimeCheck.zkey",
            "verification_key.json"
        ], check=True)

    def setUp(self):
        """Set up test components."""
        self.gps = GPSReceiver()
        self.prover = ZKTimeProver()
        self.validator = TimeValidator()

    def test_mock_satellite_data(self):
        """Test with mock satellite data."""
        # Create mock satellite data
        mock_satellites = [
            SatelliteData(
                prn_code=f"PRN{i}",
                position=(1000.0 * i, 2000.0 * i, 3000.0 * i),
                atomic_timestamp=1677649200.0 + i,  # Some base time + offset
                transmission_time=1677649200.0 + i - 0.067,  # Base time - transmission delay
                ephemeris_data={
                    "semi_major_axis": 26559.0,
                    "eccentricity": 0.01,
                    "inclination": 55.0,
                    "right_ascension": 100.0 + i,
                    "argument_of_perigee": 200.0 + i,
                    "mean_anomaly": 300.0 + i
                },
                almanac_data={
                    "clock_correction": 0.000001 * i,
                    "ionospheric_data": 0.5 + i * 0.1,
                    "atmospheric_corrections": 0.2 + i * 0.05,
                    "satellite_health": 0,
                    "doppler_shift": 1000.0 + i * 10
                }
            )
            for i in range(4)  # Create 4 satellites
        ]

        try:
            # Generate proof
            proof = self.prover.generate_time_proof(mock_satellites)
            self.assertIsNotNone(proof, "Proof should not be None")

            # Verify proof
            is_valid = self.validator.verify_time_proof(proof)
            self.assertTrue(is_valid, "Proof should be valid")

        except Exception as e:
            self.fail(f"Test failed with error: {e}")

    def test_real_gps_data(self):
        """Test with real GPS data if available."""
        try:
            # Try to connect to real GPS
            if self.gps.connect():
                # Get satellite data
                satellites = self.gps.get_satellite_data()
                self.assertGreaterEqual(len(satellites), 4, "Need at least 4 satellites")

                # Generate proof
                proof = self.prover.generate_time_proof(satellites)
                self.assertIsNotNone(proof, "Proof should not be None")

                # Verify proof
                is_valid = self.validator.verify_time_proof(proof)
                self.assertTrue(is_valid, "Proof should be valid")
            else:
                print("Warning: No real GPS connection available, skipping real GPS test")

        except Exception as e:
            self.fail(f"Test failed with error: {e}")

    def test_fingerprint_replay_protection(self):
        """Test that replay attacks are prevented."""
        # Create initial mock data
        mock_satellites = [
            SatelliteData(
                prn_code="PRN1",
                position=(1000.0, 2000.0, 3000.0),
                atomic_timestamp=1677649200.0,
                transmission_time=1677649199.933,
                ephemeris_data={
                    "semi_major_axis": 26559.0,
                    "eccentricity": 0.01,
                    "inclination": 55.0,
                    "right_ascension": 100.0,
                    "argument_of_perigee": 200.0,
                    "mean_anomaly": 300.0
                },
                almanac_data={
                    "clock_correction": 0.000001,
                    "ionospheric_data": 0.5,
                    "atmospheric_corrections": 0.2,
                    "satellite_health": 0,
                    "doppler_shift": 1000.0
                }
            )
        ] * 4  # Create 4 identical satellites for simplicity

        # Generate initial proof
        proof1 = self.prover.generate_time_proof(mock_satellites)
        
        # Wait a moment to ensure time difference
        import time
        time.sleep(2)
        
        # Try to verify the old proof
        is_valid = self.validator.verify_time_proof(proof1)
        self.assertFalse(is_valid, "Old proof should be invalid due to time expiration")

if __name__ == '__main__':
    unittest.main() 