import os
import subprocess

key = os.environ["ENCRYPTION_KEY"]

subprocess.run(["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-in", "credentials.json.enc", "-out", "credentials.json", "-k", key])
