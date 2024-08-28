"""Copyright © 2023 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import os
from oathlink.util.https.https import _post
from oathlink.util.crypto import Fernet

def decryptOathId(oathIdEncrypted: str, oathSecret: str) -> str:
    if os.path.isfile(oathSecret):
        with open(oathSecret, 'r') as file:
            oathSecret = file.read()
    return Fernet.decode(key=oathSecret, encryptedString=oathIdEncrypted)

def decryptOathIdRemote(certificateFilename: str, keyFilename: str, oathIdEncrypted: str, oathSecret: str) -> str:
    if os.path.isfile(oathSecret):
        with open(oathSecret, 'r') as file:
            oathSecret = file.read()
    extension = 'decrypt'
    payload = {"oathSecret": oathSecret, 'recordIdEncrypted': oathIdEncrypted}
    response = _post(certificateFilename=certificateFilename, keyFilename=keyFilename, extension=extension,
                     payload=payload)
    return response
