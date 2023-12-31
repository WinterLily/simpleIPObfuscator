# simpleIPObfuscator
Simple IP obfuscation script written to generate obfuscated "browser-recognizable" IP addresses for security research purposes, inspired by Andrew Brandt's talk at DEFCON 31 (https://www.youtube.com/watch?v=RRjre0dnOGQ)

## Requirements
- Python 3.x
- curl (used for validating the obfuscated addresses)

## Usage
1. Initialize the script with ```python3 simpleIPObfuscator.py```, or access help with ```python3 simpleIPObfuscator.py -h```
2. To obfuscate at random, use ```python3 simpleIPObfuscator.py -u {ip} -r true -i {number of iterations} -t {concurrent threads}```
3. All generated obfuscations are tested against CURL, which generates a LOT of false failures. 

## Methods
The script supports various obfuscation methods, including:
- Hex
- Dword
- Octal
You can select a method using the ```-m {method}``` flag

A "mixed" method is also supported, which allows for two obfuscation methods to be used against the same IP. This can be activated using the flags: ```-m mixed -f {first method} -l {last method} -s {"switch" octet}```.

You can also specify a dotless flag ```-d true``` which will url-encode any remaining dots in the obfuscated IP. 

If using the random method, all of these flags will be randomized for each iteration. 

## Disclaimer
This script is written for research purposes only.
