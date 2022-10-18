#!python3
import os, sys
import configparser

from winsys import _advapi32, encryption

DOMAIN = "VOUK"
CREDENTIALS_DIRPATH = os.path.expandvars("%USERPROFILE%")

CMD_FILEPATH = os.path.expandvars(r"%WINDIR%\system32\cmd.exe")
STARTUP_FILEPATH = os.path.expandvars(r"%USERPROFILE%\tools\startup.cmd")
CMD = CMD_FILEPATH + " /k " + STARTUP_FILEPATH

def get_params(default_username):
    domain = input("Domain: [%s] " % DOMAIN) or DOMAIN
    username = input("Username: [%s] " % default_username) or default_username
    password = input("Password for %s\\%s: " % (domain, username))
    return domain, username, password

def write_credentials(filepath, domain, username, password):
    with open(filepath, "wb") as f:
        f.write(encryption.dumps((domain, username, password)))

def get_default_username():
    ini_filepath = os.path.join(CREDENTIALS_DIRPATH, "vouk.ini")
    ini = configparser.ConfigParser()
    ini.read(ini_filepath)
    if "accounts" in ini:
        accounts = ini['accounts']
        if "default" in accounts:
            return accounts['default']

    return ""

def main(command_or_folder=".", username="", working_directory="."):
    default_username = username or get_default_username()
    if not default_username:
        raise RuntimeError("No default account in vouk.ini and no username on command-line")

    credentials_filepath = os.path.join(CREDENTIALS_DIRPATH, default_username)
    while not os.path.exists(credentials_filepath):
        print("No credentials file at %s" % credentials_filepath)
        domain, username, password = get_params(default_username)
        write_credentials(credentials_filepath, domain, username, password)

    with open(credentials_filepath, "rb") as f:
        domain, username, password = encryption.loads(f.read())

    #
    # If command_or_folder is a folder, it's the target for a new
    # cmd window; otherwise it's a command
    #
    if command_or_folder == ".":
        command_or_folder = os.getcwd()
    if os.path.isdir(command_or_folder):
        command_line = CMD_FILEPATH + ' /k '
        command_line += 'title Running as %s\\%s && ' % (domain, username)
        if os.path.exists(STARTUP_FILEPATH):
            command_line += STARTUP_FILEPATH + ' "' + command_or_folder + '"'
        command_line += ''
    else:
        command_line = command_or_folder

    _advapi32.CreateProcessWithLogonW(
        username, domain, password,
        _advapi32.LOGON_FLAGS.NETCREDENTIALS_ONLY,
        None, command_line, 0, None,
        working_directory
    )

def command_line():
    #
    # If no extra params are supplied, dump out a useful help string
    #
    if len(sys.argv) == 1:
        print("%s [[command_or_folder] [username] [working_directory]]" % sys.argv[0])
    else:
        main(*sys.argv[1:])

if __name__ == '__main__':
    main(*sys.argv[1:])
