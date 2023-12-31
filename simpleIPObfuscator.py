import argparse
import random
import re
import subprocess
import os
import multiprocessing
import concurrent.futures
import time

def testObfuscatedIP(obfuscatedIP, operatingSystem):

    """
    Test the obfuscated IP address by sending a curl request, to verify whether external services will interpret it properly. 
    """
    # Check whether to use the Windows or Linux curl command
    if operatingSystem == "Windows":
        process = subprocess.Popen(['curl.exe', '--connect-timeout', '1', 'https://'+obfuscatedIP], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        process = subprocess.Popen(['curl', '--connect-timeout', '1', 'https://'+obfuscatedIP], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    stdout, stderr = process.communicate()

    """
    String filtering for output to ensure that the returned data is clean. 
    """
    try:
        interpretedAddress = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', stdout.decode()).group(0)
    except: 
        interpretedAddress = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', stdout.decode())

    return interpretedAddress
    
def octetObfuscation(octets, method, order ):

    """
    Obfuscate the IP address octets based on the selected method
    """
    
    match method: 

        case "hex":
            hexOctets = [hex(int(octet)) for octet in octets]
            obfuscatedOctets = [".".join(hexOctets)]

        case "dword": 
            if order == "first": 
                octetStart = 3
                octetSum = 0
                for octet in octets: 
                    octetSum += int(octet) * (256 ** octetStart)
                    octetStart -= 1
            elif order == "last":
                octetStart = len(octets) -1
                octetSum = 0
                for octet in octets: 
                    octetSum += int(octet) * (256 ** octetStart)
                    octetStart -= 1
            obfuscatedOctets = [str(octetSum)]

        case "octal": 
            octalOctets = [oct(int(octet)).replace('o','') for octet in octets]
            obfuscatedOctets = [".".join(octalOctets)]

    return obfuscatedOctets

def getArgs(cpuCores):

    parser = argparse.ArgumentParser(description="Obfuscate an IP address")
    parser.add_argument("-u", "--ip", metavar="IP", type=str, help="IP address to obfuscate")
    parser.add_argument("-m", "--method", type=str, help="Obfuscation method", choices=["hex", "dword", "octal", "mixed"], default="hex")
    parser.add_argument("-f", "--first", type=str, help="(Used only when method is 'mixed') Select the method for the first obfuscation task", choices=["hex", "dword", "octal"], default="hex")
    parser.add_argument("-l", "--last", type=str, help="(Used only when method is 'mixed') Select the method for the second (last) obfuscation task", choices=["hex", "dword", "octal"], default="dword")
    parser.add_argument("-s", "--switch", type=int, help="(Used only when method is 'mixed') Select the octet at which to switch methods", choices=[4, 3, 2, 1], default=3)
    parser.add_argument("-r", "--random", type=str, help="Randomize all obfuscation attributes", choices=["true", "false"], default="false")
    parser.add_argument("-i", "--iterations", type=int, help="(Used only when randomizing) Number of randomization iterations for a given IP", choices=range(1,101), default=100)
    parser.add_argument("-d", "--dotless", type=str, help="Return the output IP dotlessly", choices=["true", "false"], default="false")
    parser.add_argument("-t", "--threads", type=int, help="Number of threads to use for obfuscation", choices=range(1,101), default=cpuCores)
    args = parser.parse_args()

    return args

def randomObfuscationJob(operatingSystem, inputOctets, args):
            
            """
            Institute a random delay on thread execution, to prevent threads from running the same job at the same time.
            """
            time.sleep(random.random())
            """
            Generate random obfuscation spec 
            """
            randomMethod = random.choice(["hex", "dword", "octal", "mixed"])
            randomDotless = random.choice(["true", "false"]) 

            if randomMethod == "mixed":
                firstMethod = random.choice(["hex", "dword", "octal"])
                secondMethod = random.choice(["hex", "dword", "octal"])
                randomSwitch = random.choice([4, 3, 2, 1])

                # Create the spec dictionary

                spec = {
                    "method": randomMethod,
                    "first": firstMethod,
                    "last": secondMethod,
                    "switch": randomSwitch,
                    "dotless": randomDotless
                }

                # Check if we've run this spec before, if so, skip it.

                if checkSpecs(jobSpecs, spec) == True:
                    print("[DUPLICATE] - Spec already used. Skipping...")
                    return False
                else:
                    jobSpecs.append(spec)
                    obfuscatedFirstOctets = octetObfuscation(inputOctets[:int(randomSwitch)], firstMethod, order="first")
                    obfuscatedLastOctets = octetObfuscation(inputOctets[int(randomSwitch):], secondMethod, order="last")
                    obfuscatedIP = ".".join(obfuscatedFirstOctets + obfuscatedLastOctets)
                    if randomDotless == "true":
                        obfuscatedIP = obfuscatedIP.replace(".", "%2E")
                    interpretedAddress = testObfuscatedIP(obfuscatedIP, operatingSystem)
                    if interpretedAddress == args.ip:
                        result = "[SUCCESS]"
                    else:
                        result = "[FAIL]"                    
                    print(F"{result} - Input Address: {args.ip}\n\tSpec:: Method: {randomMethod}, First: {firstMethod}, Last: {secondMethod}, Switch: {randomSwitch}, Dotless: {randomDotless}\n\t\t Obfuscated IP address: {obfuscatedIP} -> Interpreted As: {interpretedAddress}")


            else:

                # Create the spec dictionary
                
                spec = {
                    "method": randomMethod,
                    "dotless": randomDotless
                }

                # Check if we've run this spec before, if so, skip it.

                if checkSpecs(jobSpecs, spec) == True:
                     print("[DUPLICATE] - Spec already used. Skipping...")
                     pass
                else:
                    jobSpecs.push(spec)                    
                    obfuscatedOctets = octetObfuscation(inputOctets, randomMethod, order="first")
                    obfuscatedIP = ".".join(obfuscatedOctets)
                    if randomDotless == "true":
                        obfuscatedIP = obfuscatedIP.replace(".", "%2E")
                    interpretedAddress = testObfuscatedIP(obfuscatedIP, operatingSystem)
                    if interpretedAddress == args.ip:
                        result = "[SUCCESS]"
                    else:
                        result = "[FAIL]"
                    print(F"{result} - Input Address: {args.ip}\n\tSpec:: Method: {randomMethod}, Dotless: {randomDotless}\n\t\t Obfuscated IP address: {obfuscatedIP} -> Interpreted As: {interpretedAddress}")                

def singletonObfuscationJob(operatingSystem, inputOctets, args):
        
        """
        Check if the user has selected the mixed method, if so, split the octets into two lists and obfuscate separately, rejoin later. 
        """
        if args.method == "mixed":

            obfuscatedFirstOctets = octetObfuscation(inputOctets[:int(args.switch)], args.first, order="first")
            obfuscatedLastOctets = octetObfuscation(inputOctets[int(args.switch):], args.last, order="last")
            obfuscatedIP = ".".join(obfuscatedFirstOctets + obfuscatedLastOctets)
        else:
            obfuscatedOctets = octetObfuscation(inputOctets, args.method, order="first")
            obfuscatedIP = ".".join(obfuscatedOctets)

        interpretedAddress = testObfuscatedIP(obfuscatedIP, operatingSystem)

        """
        Output results. 
        """
        if args.method == "mixed":
            print(F"Input Address: {args.ip}\n\tSpec:: Method: {args.method}, First: {args.first}, Last: {args.last}, Switch: {args.switch}, Dotless: {args.dotless}\n\t\t Obfuscated IP address: {obfuscatedIP} -> Interpreted As: {interpretedAddress}")
        else:
            print(F"Input Address: {args.ip}\n\tSpec:: Method: {args.method}, Dotless: {args.dotless}\n\t\t Obfuscated IP address: {obfuscatedIP} -> Interpreted As: {interpretedAddress}")      

def checkSpecs(jobSpecs, spec):

    if spec in jobSpecs:
        return True
    else:
        return False

def main():

    """
    Get the current OS; 
    This is so that we can later use the correct command to test the obfuscated IP address
    """

    if os.name == "nt":
        operatingSystem = "Windows"
    else:
        operatingSystem = "Linux/Other"

    """
    Get the current CPU core count;
    This will be used later to determine the amount of threads to use for batch obfuscation jobs
    """
    cpuCores = multiprocessing.cpu_count()

    """
    Get launch argument and instantiate initial variables 
    """
    args = getArgs(cpuCores)
    if args.ip == None:
        args.ip = input("Enter an IP address to obfuscate: ")
    inputOctets = args.ip.split(".")

    """
    Run obfuscation jobs
    """
    if args.random == "true":
        # Instantiate the Job Specs dictionary list, so that we can later compare and ensure that we don't run the same jobs multiple times.  
        global jobSpecs
        jobSpecs = [{}]
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
            for i in range(args.iterations):
                executor.submit(randomObfuscationJob, operatingSystem, inputOctets, args)
    else:
            singletonObfuscationJob(operatingSystem, inputOctets, args)

main()
