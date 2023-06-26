# KnockKnock - v0.9 - [@waffl3ss](https://github.com/waffl3ss)

#### Please make sure to actually utilize the README. 

Designed to validate potential usernames by querying OneDrive and/or Microsoft Teams, which are passive methods.  
Additionally, it can output/create a list of legacy Skype users identified through Microsoft Teams enumeration.  
Finally, it also creates a nice clean list for future usage, all conducted from a single tool.  

------------------------------------------------------------------------------------

# Usage

```
$ python3 .\KnockKnock.py -h

  _  __                 _    _  __                 _
 | |/ /_ __   ___   ___| | _| |/ /_ __   ___   ___| | __
 | ' /| '_ \ / _ \ / __| |/ / ' /| '_ \ / _ \ / __| |/ /
 | . \| | | | (_) | (__|   <| . \| | | | (_) | (__|   <
 |_|\_\_| |_|\___/ \___|_|\_\_|\_\_| |_|\___/ \___|_|\_\
   v0.9                             Author: #Waffl3ss


usage: KnockKnock.py [-h] [-teams] [-onedrive] [-l] -i INPUTLIST [-o OUTPUTFILE] -d TARGETDOMAIN [-t TEAMSTOKEN] [-threads MAXTHREADS] [-v]

options:
  -h, --help           show this help message and exit
  -teams               Run the Teams User Enumeration Module
  -onedrive            Run the One Drive Enumeration Module
  -l                   Write legacy skype users to a seperate file
  -i INPUTLIST         Input file with newline-seperated users to check
  -o OUTPUTFILE        Write output to file
  -d TARGETDOMAIN      Domain to target
  -t TEAMSTOKEN        Teams Token (file containing token or a string)
  -threads MAXTHREADS  Number of threads to use in the Teams User Enumeration (default = 10)
  -v                   Show verbose errors

```
### Examples

```
./KnockKnock.py -teams -i UsersList.txt -d Example.com -o OutFile.txt -t BearerToken.txt
./KnockKnock.py -onedrive -i UsersList.txt -d Example.com -o OutFile.txt
./KnockKnock.py -onedrive -teams -i UsersList.txt -d Example.com -t BearerToken.txt -l
```

------------------------------------------------------------------------------------
# Options

 - You can select one or both modes, as long as the appropriate options are provided for the modules selected.  
 - Both modules will require the domain flag (-d) and the user input list (-i).  
 - The tool does not require an output file as an option, and if not supplied, it will print to screen only.  
 - The verbose mode will show A LOT of extra information, including users that are not valid.  
 - The Teams option requires a bearer token. The script automatically removes the beginning and end portions to use only whats required.  

------------------------------------------------------------------------------------
# How to get your Bearer token

To get your bearer token, you will need a Cookie Manager plugin on your browser and login to your own Microsoft Teams through the browser.  
Next, view the cookies related to the current webpage (teams.microsoft.com).  
The cookie you are looking for is for the domain .teams.microsoft.com and is titled "authtoken".  
You can copy the whole token as the script will split out the required part for you.  

------------------------------------------------------------------------------------
# References

[@nyxgeek](https://github.com/nyxgeek) - [onedrive_user_enum](https://github.com/nyxgeek/onedrive_user_enum)  
[@immunIT](https://github.com/immunIT) - [TeamsUserEnum](https://github.com/immunIT/TeamsUserEnum)  
