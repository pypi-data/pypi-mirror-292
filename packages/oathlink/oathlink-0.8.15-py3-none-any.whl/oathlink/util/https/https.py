"""Copyright © 2023 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

import os
import json
import requests
from zipfile import ZipFile


def _getBaseUrl() -> str:
    return 'https://api.oathlink.com'

def _getUrl(extension: str) -> str:
    if len(extension) > 0:
        if extension[0] == '/':
            extension = extension[1:]
    return f'{_getBaseUrl()}/{extension}'

def get(url: str) -> str:
    response = requests.get(url)
    zipFilename = f'download.zip'
    with open(zipFilename, 'wb') as file:
        file.write(response.content)
    with ZipFile(zipFilename, 'r') as zip:
        zip.extractall()
        info = zip.infolist()[0]
        filename = info.filename
    os.remove(zipFilename)
    return filename

def put(url: str, data: str) -> bool:
    # Resolving url
    temporalFilename = 'tmp.txt'
    if not os.path.isfile(data):
        filename = temporalFilename
        content = data
        # Writing file if contents are handed
        with open(filename, 'w') as file:
            file.write(content)
    else:
        filename = data
    # Zipping the file
    zipFilename = f'{filename}.zip'
    with ZipFile(zipFilename, 'w') as zip:
        zip.write(filename)
    # Regular putting of a file
    response = requests.put(url, data=open(zipFilename, 'rb')).text
    try:
        os.remove(zipFilename)
    except:
        pass
    if filename == temporalFilename:
        try:
            os.remove(filename)
        except:
            pass
    if '<Error><Code>' in response:
        return False
    return True


def _post(certificateFilename: str, keyFilename: str, extension: str = None, payload: dict = None):
    if extension is None:
        extension = ''
    if payload is None:
        payload = {}
    cert = (certificateFilename, keyFilename)
    data = json.dumps(payload)
    response = requests.post(_getUrl(extension), data=data, cert=cert)
    return response.text


def _get(certificateFilename: str, keyFilename: str, extension: str = None):
    if extension is None:
        extension = ''
    cert = (certificateFilename, keyFilename)
    response = requests.get(_getUrl(extension), cert=cert)
    return response.text
