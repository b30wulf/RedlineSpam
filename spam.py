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

url = 'http://192.168.117.134:6677/IRemotePanel'

fileFirstnames = "first-names.txt"
fileLastnames = "last-names.txt"
fileEmails = "mail-domains.txt"
fileDomains = "domains.txt"
fileCountrycodes = "iso_country_codes.txt"
fileSoftware = "applications.txt"
fakeDomains = []

class RedlineSettings:
    """MyClass class instance"""
    def __init__(self, grabbrowsers, grabftp, grabfiles, grabimclients, grabpaths):
        self.grabbrowsers = grabbrowsers
        self.grabftp = grabftp
        self.grabfiles = grabfiles
        self.grabimclients = grabimclients
        self.grabpaths = grabpaths


def get_settings():
    headers = { 'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://tempuri.org/IRemotePanel/GetSettings'}

    x = requests.post(url, headers = headers, data='<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><GetSettings xmlns="http://tempuri.org/"/></s:Body></s:Envelope>')

    json_result = xmltodict.parse(x.text)
    r = RedlineSettings(json_result['s:Envelope']['s:Body']['GetSettingsResponse']['GetSettingsResult']['a:GrabBrowsers'],
                        json_result['s:Envelope']['s:Body']['GetSettingsResponse']['GetSettingsResult']['a:GrabFTP'],
                        json_result['s:Envelope']['s:Body']['GetSettingsResponse']['GetSettingsResult']['a:GrabFiles'],
                        json_result['s:Envelope']['s:Body']['GetSettingsResponse']['GetSettingsResult']['a:GrabImClients'],
                        json_result['s:Envelope']['s:Body']['GetSettingsResponse']['GetSettingsResult']['a:GrabPaths'])
    return r


def build_payload():
    fake = Faker()
    countrycode = create_countrycode()
    country = pycountry.countries.get(alpha_2=countrycode)
    number_browsers = random.randint(1, 4)
    payload = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><SendClientInfo xmlns="http://tempuri.org/"><user xmlns:a="v1/Models" xmlns:i="http://www.w3.org/2001/XMLSchema-instance"><a:AdminPromptType>DimmedPromptForNonWindowsBinaries</a:AdminPromptType>'
    payload += '<a:BuildID>' + ''.join(random.choices(string.ascii_uppercase + string.digits, k = random.randint(4,12))) + '</a:BuildID>'
    payload += '<a:Country>' + countrycode + '</a:Country>'
    payload += '<a:Credentials>'
    payload += '<a:Browsers>'

    for i in range(number_browsers):
        payload += '<a:Browser>'
        
        payload += '<a:Autofills>'
        for r in range(random.randint(1,10)):
            payload += '<a:Autofill>'
            payload += '<a:Name>' + create_username() + '</a:Name>'
            payload += '<a:Value>' + create_username() + '</a:Value>'
            payload += '</a:Autofill>'
        payload += '</a:Autofills>'

        payload += '<a:Cookies>'
        for c in range(random.randint(50,123)):
            payload += '<a:Cookie>'
            payload += '<a:Expires>0</a:Expires>'
            payload += '<a:Host>' + fakeDomains[random.randint(0, len(fakeDomains) - 1)] + '</a:Host>'
            payload += '<a:Http>false</a:Http>'
            payload += '<a:Name>' + ''.join(random.choices(string.ascii_uppercase + string.digits, k = random.randint(4,27))) + '</a:Name>'
            payload += '<a:Path>/</a:Path>'
            payload += '<a:Secure>false</a:Secure>'
            payload += '<a:Value>' + ''.join(random.choices(string.ascii_uppercase + string.digits, k = random.randint(10,34))) + '</a:Value>'
            payload += '</a:Cookie>'
        payload += '</a:Cookies>'

        payload += '<a:Credentials>'
        for p in range(random.randint(7,23)):
            payload += '<a:LoginPair>'
            payload += '<a:Host>' + fakeDomains[random.randint(0, len(fakeDomains) - 1)] + '</a:Host>'
            payload += '<a:Login>' + create_username() + "@" + fakeDomains[random.randint(0, len(fakeDomains) - 1)] + '</a:Login>'
            payload += '<a:Password>' + create_fakepassword() +'</a:Password>'
            payload += '</a:LoginPair>'
        payload += '</a:Credentials>'

        payload += '<a:CreditCards/>'
        payload += '<a:Name>' + create_fake_browser() + '</a:Name>'
        payload += '<a:Profile>Default</a:Profile>'
        payload += '</a:Browser>'

    payload += '</a:Browsers>'
    payload += '<a:Defenders xmlns:b="http://schemas.microsoft.com/2003/10/Serialization/Arrays"><b:string>Windows Defender</b:string></a:Defenders>'
    payload += '<a:Files/><a:FtpConnections/>' # No files and FtpConnections for now
    payload += '<a:Hardwares><a:Hardware><a:Caption>Intel(R) Core(TM) i7-8700 CPU @ 3.20GHz</a:Caption><a:HardType>Processor</a:HardType><a:Parameter>2</a:Parameter></a:Hardware><a:Hardware><a:Caption>Intel(R) Core(TM) i7-8700 CPU @ 3.20GHz</a:Caption><a:HardType>Processor</a:HardType><a:Parameter>2</a:Parameter></a:Hardware></a:Hardwares>'

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
    payload += '<a:Screenshot>' + create_fake_screenshot() +'</a:Screenshot>'
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
        fake_processes += '<b:string>ID: ' + str(random.randint(300,4000)) + ', Name: ' + fake_filename + ', CommandLine: </b:string>'
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

    rand_username_format = random.randint(0,2)

    if rand_username_format == 0:
        glob_username = firstnames[rand_firstname] + "." + lastnames[rand_lastname]
    elif rand_username_format == 1:
        glob_username = firstnames[rand_firstname][0] + lastnames[rand_lastname]
    elif rand_username_format == 2:
        glob_username = lastnames[rand_lastname] + firstnames[rand_firstname][0]
    return glob_username


def send_record(settings):
    headers = {'Content-Type': 'text/xml; charset=utf-8',
               'SOAPAction': 'http://tempuri.org/IRemotePanel/SendClientInfo'}

    contents = build_payload()

    x = requests.post(url, headers=headers,
                      data=contents)
    return


def create_fakeversion():
    p1 = random.randint(1,16)
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
    bool = random.randint(0,1)
    if bool == 0:
        return "x64"
    else:
        return "x32"

# We only do this once at the beginning since it's a 15 MB file
load_fake_domains()
r = get_settings()


for i in range(1000):
    print("Now sending item #" + str(i))
    send_record(r)