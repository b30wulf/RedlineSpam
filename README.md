![alt text](https://github.com/hariomenkel/RedlineSpam/blob/main/redline_logo.png?raw=true)
# RedlineSpam
Python tool to spam Redline Infostealer panels with legit looking data

This tool tries to imitate legitimate stolen credentials, cookies etc. to flood operators with fake date which aims to make finding legit data as "easy" as finding a needle in the haystack

https://mariohenkel.medium.com/dissecting-redline-infostealer-traffic-a-soapy-endeavour-eb70694e243b

# Prerequisites
Please install Tor before using this script and make sure it is running and listening on Port 9050

Afterwards install the following package:<BR>
<BR>
`pip install PySocks`<BR>
`pip install stem`<BR>
`pip install requests`<BR>
<BR>  
Please follow these steps to make sure this script is able to change the TOR IP programmatically<BR>
<BR>
`$ tor --hash-password MyStr0n9P#D`<BR>
`16:160103B8D7BA7CFA605C9E99E5BB515D9AE71D33B3D01CE0E7747AD0DC`<BR>
<BR>
Add this value to `/etc/torrc` for the value `HashedControlPassword` so it reads<BR>
`HashedControlPassword 16:160103B8D7BA7CFA605C9E99E5BB515D9AE71D33B3D01CE0E7747AD0DC`<BR>
<BR>
Afterwards uncomment the line<BR>
`ControlPort 9051`<BR>
<BR>
and finally restart tor service to make changes take effect<BR>
`$ sudo service tor restart`
  
# Weaponization
With the flag --weaponization_path <path> you can tell RedlineSpam to get a payload of your choice and send it to the attacker as a bait. Use cases for this might be leveraging CobaltStrike beacons etc.
