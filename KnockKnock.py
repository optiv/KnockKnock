#!/usr/bin/python3

import requests,argparse,urllib3,json,threading,sys,re
from pathlib import Path
from argparse import RawTextHelpFormatter
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

banner = """
  _  __                 _    _  __                 _    
 | |/ /_ __   ___   ___| | _| |/ /_ __   ___   ___| | __
 | ' /| '_ \ / _ \ / __| |/ / ' /| '_ \ / _ \ / __| |/ /
 | . \| | | | (_) | (__|   <| . \| | | | (_) | (__|   < 
 |_|\_\_| |_|\___/ \___|_|\_\_|\_\_| |_|\___/ \___|_|\_\\
   v0.9                             Author: #Waffl3ss \n\n"""
print(banner)

parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument('-teams', dest='runTeams', required=False, default=False, help="Run the Teams User Enumeration Module", action="store_true")
parser.add_argument('-onedrive', dest='runOneDrive', required=False, default=False, help="Run the One Drive Enumeration Module", action="store_true")
parser.add_argument('-l', dest='teamsLegacy', required=False, default=False, help="Write legacy skype users to a seperate file", action="store_true")
parser.add_argument('-i', dest='inputList', type=argparse.FileType('r'), required=True, default='', help="Input file with newline-seperated users to check")
parser.add_argument('-o', dest='outputfile', type=str, required=False, default='', help="Write output to file")
parser.add_argument('-d', dest='targetDomain', type=str, required=True, default='', help="Domain to target")
parser.add_argument('-t', dest='teamsToken', required=False, default='', help="Teams Token (file containing token or a string)")
parser.add_argument('-threads', dest='maxThreads', required=False, default=10, help="Number of threads to use in the Teams User Enumeration (default = 10)")
parser.add_argument('-v', dest='verboseMode', required=False, default=False, help="Show verbose errors", action="store_true")
args = parser.parse_args()

if not args.runTeams and not args.runOneDrive:
    print("[!] You must select one enumeration module, Teams or OneDrive... Exiting...")
    sys.exit()
    
if args.runTeams and args.teamsToken == '':
    print("[!] Teams Bearer Token required for Teams enumeration, Exiting...")
    sys.exit()
    
if args.teamsLegacy and args.outputfile == '':
    print("[!] Teams Legacy Output requires the output file option (-o). Exiting...")
    sys.exit()

inputNames = []
nameList = []
validNames = []
legacyNames = []

for name in args.inputList.readlines():
    inputNames.append(name)

def OneDriveEnumerator():
    tenantData = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:exm="http://schemas.microsoft.com/exchange/services/2006/messages" xmlns:ext="http://schemas.microsoft.com/exchange/services/2006/types" xmlns:a="http://www.w3.org/2005/08/addressing" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <soap:Header>
                <a:Action soap:mustUnderstand="1">http://schemas.microsoft.com/exchange/2010/Autodiscover/Autodiscover/GetFederationInformation</a:Action>
                <a:To soap:mustUnderstand="1">https://autodiscover-s.outlook.com/autodiscover/autodiscover.svc</a:To>
                <a:ReplyTo>
                    <a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address>
                </a:ReplyTo>
            </soap:Header>
            <soap:Body>
                <GetFederationInformationRequestMessage xmlns="http://schemas.microsoft.com/exchange/2010/Autodiscover">
                    <Request>
                        <Domain>{args.targetDomain}</Domain>
                    </Request>
                </GetFederationInformationRequestMessage>
            </soap:Body>
        </soap:Envelope>"""

    tenantHeaders = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": '"http://schemas.microsoft.com/exchange/2010/Autodiscover/Autodiscover/GetFederationInformation"',
        "User-Agent": "AutodiscoverClient",
        "Accept-Encoding": "identity",
        }

    try:
        tenantRequest = requests.post("https://autodiscover-s.outlook.com/autodiscover/autodiscover.svc",headers=tenantHeaders,data=tenantData)
        tenantRE = re.compile(r"<Domain>([^<>/]*)</Domain>", re.I)
        tenantDomainList = list(set(tenantRE.findall(tenantRequest.text)))
        for domain in tenantDomainList:
            if domain.lower().endswith(".onmicrosoft.com"):
                targetTenant = domain.split(".")[0]
    except Exception as e:
        print("[!] Error retrieving tenant for target, Exiting...")
        if args.verboseMode:
            print("[V] " + str(e))
        sys.exit()

    if args.verboseMode:
        print("[V] Using target tenant %s" % targetTenant)

    for potentialUser in nameList:
        try:
            testURL = "https://" + targetTenant + "-my.sharepoint.com/personal/" + str(potentialUser.replace(".","_")) + "_" + str(args.targetDomain.replace(".","_")) + "/_layouts/15/onedrive.aspx"
            if args.verboseMode:
                print("[V] Testing: " + str(testURL))
            userRequest = requests.get(testURL, verify=False)
            if userRequest.status_code in [200, 401, 403, 302]:
                print("[+] " + str(str(potentialUser) + "@" + str(args.targetDomain)))
                validNames.append(str(potentialUser))
            else:
                if args.verboseMode:
                    print("[-] " + str(str(potentialUser) + "@" + str(args.targetDomain)))
                pass

        except Exception as e:
            if args.verboseMode:
                print("[V] " + str(e))
            pass

def teamsEnum(potentialUserNameTeams):       
    if args.verboseMode:
        print("[V] Testing user %s" % potentialUserNameTeams)

    URL_TEAMS = "https://teams.microsoft.com/api/mt/emea/beta/users/"
    CLIENT_VERSION = "27/1.0.0.2021011237"

    if Path(args.teamsToken).is_file():
        tokenFile = open(args.teamsToken, 'r')
        theToken = str(tokenFile.read())
    else:
        theToken = str(args.teamsToken)

    if "Bearer" in theToken:
        theToken = theToken.replace("Bearer%3D","").replace("%26Origin%3Dhttps%3A%2F%2Fteams.microsoft.com","")

    initHeaders = {
        "Host": "teams.microsoft.com",
        "Authorization": "Bearer " + str(theToken),
        "X-Ms-Client-Version": str(CLIENT_VERSION),
    }

    initRequest = requests.get(URL_TEAMS + str(potentialUserNameTeams) + "/externalsearchv3?includeTFLUsers=true", headers=initHeaders)
    if initRequest.status_code == 403:
        print("[+] %s" % potentialUserNameTeams)
        validNames.append(str(potentialUserNameTeams.split("@")[0]))

    elif initRequest.status_code == 404:
        print("[!] Error with username")

    elif initRequest.status_code == 200:
        statusLevel = json.loads(initRequest.text)
        if statusLevel:
            print("[+] %s -- Legacy Skype Detected" % potentialUserNameTeams)
            validNames.append(str(potentialUserNameTeams.split("@")[0]))
            legacyNames.append(str(potentialUserNameTeams.split("@")[0]))
            if args.verboseMode:
                print(json.dumps(statusLevel, indent=2))
        elif not statusLevel:
            if args.verboseMode:
                print("[-] %s" % potentialUserNameTeams)

    elif initRequest.status_code == 401:
        print("[!] Error with Teams Auth Token... \n\tShutting down threads and Exiting")
        sys.exit()

def main():
    global nameList    
    for name in inputNames:
        if "@" in name:
            name = name.split("@")[0]
            nameList.append(name.strip())
        else:
            nameList.append(name.strip())            
    nameList = list(dict.fromkeys(nameList))

    if args.runOneDrive:
        if args.verboseMode:
            print("[V] Running OneDrive Enumeration")
        OneDriveEnumerator()

    if args.runOneDrive and args.runTeams:
        nameList = [i for i in nameList if i not in validNames]

    if args.runTeams:
        if args.verboseMode:
            print("[V] Running Teams User Enumeration using %i threads" % args.maxThreads)

        threads = []
        max_threads = args.maxThreads
        for potentialUserNameTeams in nameList:
            teamsEnumUser = str(potentialUserNameTeams.strip()) + str("@") + str(args.targetDomain)
            while threading.active_count() >= max_threads + 1:
                pass

            thread = threading.Thread(target=teamsEnum, args=(teamsEnumUser,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    if validNames:
        if args.outputfile != '':
            overwriteOutputFile = True
            if Path.exists(Path(args.outputfile)):
                overwriteOutFileChoice = input("[!] Output File exists, overwrite? [Y/n] ")
                if overwriteOutFileChoice == "y" or "Y" or "":
                    overwriteOutputFile = True
                    Path(args.outputfile).unlink(missing_ok=True)
                else:
                    overwriteOutputFile = False

            if overwriteOutputFile:
                if args.verboseMode:
                    print("[V] Running deduplication and writing names to file")
                validNamesUnique = list(dict.fromkeys(validNames))
                with open(args.outputfile, 'w') as outfile:
                    for item in validNamesUnique:
                        outfile.write(item + "@" + args.targetDomain + "\n")
                outfile.close()
            else:
                print("[-] Not overwriting output file")

    if args.teamsLegacy:
        if legacyNames:
            if args.outputfile != '':
                legacyOutFile = "Legacy_" + str(args.outputfile)
                legacyOverwriteFile = True

                if Path.exists(Path(legacyOutFile)):
                    legOverwriteChoice = input("[!] Legacy Output File exists, overwrite? [Y/n] ")
                    if legOverwriteChoice == "y" or "Y" or "":
                        legacyOverwriteFile = True
                        Path(legacyOutFile).unlink(missing_ok=True)
                    else:
                        legacyOverwriteFile = False

                if legacyOverwriteFile:
                    if args.verboseMode:
                        print("[V] Found %i Legacy Skype Users, creating file with names" % len(legacyNames))
                    legacyNamesUniq = list(dict.fromkeys(legacyNames))
                    with open(legacyOutFile, "w") as legOut:
                        for legName in legacyNamesUniq:
                            legOut.write(legName + "@" + args.targetDomain + "\n")
                    legOut.close()
                else:
                    print("[-] Not overwriting legacy skype users file")
        else:
            print("[-] No legacy skype users identified")

if __name__ == "__main__":
    main()
