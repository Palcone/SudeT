# A tool for extracting and parsing steam user data
# Created by Parker Alcone

import vdf
import os
import requests
import shutil
import sys

def parse_files():
    userpath = os.path.join(os.getenv("programfiles(x86)"), r"Steam\config\loginusers.vdf")
    remotepath = os.path.join(os.getenv("programfiles(x86)"), r"Steam\config\remoteclients.vdf")

    steamid = ""
    accountid = ""

    print("=================================================")
    print("Parsing Steam Artifacts")
    print("=================================================")

    print("\nAccount Details")
    print("=================================================")

    try:
        with open(userpath, "r", encoding="utf-8") as file:
            d = vdf.parse(file)
            steamid = "".join(d["users"].keys())
            print("Steam ID:\t\t" + steamid)
            response = requests.get("https://steamcommunity.com/actions/ajaxresolveusers?steamids=" + steamid)
            accountid = str(response.json()[0]["accountid"])
            print("Account ID:\t\t" + accountid)
            print("Account Name:\t\t" + d["users"][steamid]["AccountName"])
            print("User Name:\t\t" + d["users"][steamid]["PersonaName"])

    except FileNotFoundError:
        print("Error: File Not Found")
        sys.exit(1)

    friendpath = os.path.join(os.getenv("programfiles(x86)"), r"Steam\userdata", accountid, r"config\localconfig.vdf")

    print("\nFriends")
    print("=================================================")

    try:
        with open(friendpath, "r", encoding="utf-8") as file:
            print("Username : Account ID")
            print("---------------------")
            d = vdf.parse(file)
            for key in d["UserLocalConfigStore"]["friends"]:
                if isinstance(d["UserLocalConfigStore"]["friends"][key], dict):
                    print(d["UserLocalConfigStore"]["friends"][key]["name"] + " : " + key)

            print("\nOwned Games")
            print("=================================================")
            print("Game Title : Application ID")
            print("---------------------------")
            for key in d["UserLocalConfigStore"]["Software"]["Valve"]["Steam"]["apps"]:
                response = requests.get("https://store.steampowered.com/api/libraryappdetails/?appid=" + str(key) + "&l=english")
                if response.json()["status"] != 2:
                    print(response.json()["name"] + " : " + key)
    except FileNotFoundError:
        print("Error: File Not Found")


    print("\nRemote Connections")
    print("=================================================")

    try:
        with open(remotepath, "r", encoding="utf-8") as file:
           for line in file:
               print(line)
    except FileNotFoundError:
        print("Error: No Remote Connections Found")


def extract_files():

    htmlpath = os.path.join(os.getenv("userprofile"), r"AppData\Local\Steam\htmlcache")
    logpath = os.path.join(os.getenv("programfiles(x86)"), r"Steam\logs")
    filepath1 = os.path.join(os.getenv("programfiles(x86)"), r"Steam\config\loginusers.vdf")

    try:
        with open(filepath1, "r") as file:
            d = vdf.parse(file)
            steamid = "".join(d["users"].keys())
    except:
        print("Error: loginusers.vdf Not Found")
        sys.exit(1)

    response = requests.get("https://steamcommunity.com/actions/ajaxresolveusers?steamids=" + steamid)
    accountid = str(response.json()[0]["accountid"])

    filepath2 = os.path.join(os.getenv("programfiles(x86)"), r"Steam\userdata", accountid, r"config\localconfig.vdf")
    filepath3 = os.path.join(os.getenv("programfiles(x86)"), r"Steam\config\remoteclients.vdf")

    print("=================================================")
    print("Extracting Steam Artifacts to \'steam_artifacts\'")
    print("=================================================")

    print(r"Creating output directory...")
    try:
        os.mkdir(r"steam_artifacts")
    except OSError as error:
        print(error)
    try:
        os.mkdir(r"steam_artifacts/files")
    except OSError as error:
        print(error)

    print(r"Extracting web cache...")

    try:
        shutil.make_archive(r"steam_artifacts/htmlcache", 'zip', htmlpath)
    except:
        print("Error: failed to extract htmlcache files")

    print("Extracting steam logs...")

    try:
        shutil.make_archive(r"steam_artifacts/logs", "zip", logpath)
    except:
        print("Error: failed to extract log files")

    print("Extracting vdf files...")

    try:
        shutil.copy2(filepath1, r"steam_artifacts/files/loginusers.vdf")
    except:
        print("Error: loginusers.vdf not located")

    try:
        shutil.copy2(filepath2, r"steam_artifacts/files/localconfig.vdf")
    except:
        print("Error: localconfig.vdf not located")

    try:
        shutil.copy2(filepath3, r"steam_artifacts/file/remoteclients.vdf")
    except:
        print("Error: remoteclients.vdf not located")

    print("\nExtraction Complete")
    

def main():

    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    i = 0

    if "-h" in opts:
        print("=================================================")
        print("Steam User Data Extration Tool")
        print("=================================================")
        print("Parses or collects locally-stored Steam user information.")
        print("\nUsage: \n\tpython sudet.py [option]")
        print("\nFunctions: \n\t-p\tDisplays parsed data from local Steam files, includes account details,\n\t\tfriends, owned games, and remote connections.")
        print("\t-e\tExtracts important files from local Steam files, includes raw vdf \n\t\tfiles, web browser files, and log files.")
        print("\t-h\tPrints help information.")
        print("\t-y\tBypass warning message.")
        sys.exit(0)

    if "-p" in opts:
        if "-y" not in opts:
            print("=================================================")
            print("WARNING: This tool will perform several request to online Steam services in order to identify file locations and artifact details")
            print("=================================================\n")
            put = input("Continue? (y/n)\n")
            if put != "y":
                sys.exit(0)
        parse_files()
        i += 1
    if "-e" in opts:
        if "-y" not in opts:
            print("=================================================")
            print("WARNING: This tool will perform several request to online Steam services in order to identify file locations and artifact details")
            print("=================================================\n")
            put = input("Continue? (y/n)\n")
            if put != "y":
                sys.exit(0)
        extract_files()
        i += 1
    if i == 0:
        print("\nTry: \n\tpython sudet.py -h")
        sys.exit(0)
    

if __name__ == "__main__":
    main()