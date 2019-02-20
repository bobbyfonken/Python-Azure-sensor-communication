import gnupg
import getpass

# Variable to use gnupg
gpg = gnupg.GPG()

gpgPass = getpass.getpass("Please provide the passphrase to encrypt the config file: ")
print("\n")

gpg = gnupg.GPG()
with open('config.json', 'rb') as f:
	status = gpg.encrypt_file(f, None, passphrase=gpgPass, symmetric=True, output='config.json.gpg')

print 'ok: ', status.ok
print 'status: ', status.status
print 'stderr: ', status.stderr