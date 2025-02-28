pragma circom 2.0.0;

include "../../../node_modules/circomlib/circuits/comparators.circom";

template SatelliteTimeCheck() {
    // Public inputs
    signal input T_sat;    // Satellite broadcast time
    signal input c;        // Speed of light constant
    signal input Delta;    // Allowed error margin
    
    // Private inputs
    signal input T_local;  // Device's local time
    signal input D;        // Distance/time-of-flight factor
    
    // Compute offset
    signal difference;
    difference <== T_local - T_sat;
    
    signal offset;
    offset <== difference * c - D;
    
    // Check if offset is within acceptable range
    component lt = LessThan(252);
    lt.in[0] <== offset + Delta;  // offset + Delta > 0
    lt.in[1] <== 0;
    
    component gt = GreaterThan(252);
    gt.in[0] <== offset - Delta;  // offset - Delta < 0
    gt.in[1] <== 0;
    
    // Both conditions must be true
    signal valid;
    valid <== lt.out * gt.out;
    valid === 1;  // Must be valid
}

component main = SatelliteTimeCheck();
