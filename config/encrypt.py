# This script encrypts the config.json file that contains sensitive contents

import gnupg
import getpass

# Variable to use gnupg
gpg = gnupg.GPG()

# Get the passphrase to encrypt the file with. This also needs to be given when running the meting.py file
gpgPass = getpass.getpass("Please provide the passphrase to encrypt the config file: ")
print("\n")

# Opens the unencrypted file and encrypts the contents --> DELETE THE UNENCRYPTED FILE AFTERWARDS!!!!!
with open('config.json', 'rb') as f:
	status = gpg.encrypt_file(f, None, passphrase=gpgPass, symmetric=True, output='config.json.gpg')

# Prints debug information
print 'ok: ', status.ok
print 'status: ', status.status
print 'stderr: ', status.stderr