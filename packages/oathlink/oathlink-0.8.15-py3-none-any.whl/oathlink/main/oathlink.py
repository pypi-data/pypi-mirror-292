"""Copyright © 2023 Burrus Financial Intelligence, Ltda. (hereafter, BFI) Permission to include in application
software or to make digital or hard copies of part or all of this work is subject to the following licensing
agreement.
BFI Software License Agreement: Any User wishing to make a commercial use of the Software must contact BFI
at jacques.burrus@bfi.lat to arrange an appropriate license. Commercial use includes (1) integrating or incorporating
all or part of the source code into a product for sale or license by, or on behalf of, User to third parties,
or (2) distribution of the binary or source code to third parties for use with a commercial product sold or licensed
by, or on behalf of, User. """

from oathlink.services.hello import helloOathlink
from oathlink.services.record.upload import getOathlinkUpload
from oathlink.services.record.download import getOathlinkDownload
from oathlink.services.record.decrypt import decryptOathId
from oathlink.services.record.decrypt import decryptOathIdRemote
from oathlink.services.record.archive import archiveOathlink
from oathlink.services.record.cancel import cancelOathlink
from oathlink.services.agent.account.create import createAgent
from oathlink.services.agent.ip.add import addIP
from oathlink.services.agent.ip.remove import removeIP
from oathlink.services.agent.account.link import linkAgents
from oathlink.services.agent.account.unlink import unlinkAgents
from oathlink.services.report.outstanding import reportOutstanding
from oathlink.services.report.record import reportRecord
from oathlink.services.report.history import reportHistory
from oathlink.util.https.https import get as getData, put as putData

def hello(certificate_filename_pem: str, certificate_filename_key: str) -> str:
    return helloOathlink(certificateFilename=certificate_filename_pem, keyFilename=certificate_filename_key)

def data_upload(oath_link: str, data: str) -> bool:
    return putData(url=oath_link, data=data)

def data_download(oath_link: str) -> list:
    try:
        return getData(url=oath_link)
    except Exception as e:
        print(f'Downloading from {oath_link} failed (Most likely due to unregistered IP - Error: {str(e)}).')

def upload(certificate_filename_pem: str, certificate_filename_key: str, user_id: str, owner_id: str,
           owner_authorization: str = '', description: str = '', intent: str = '') -> str:
    return getOathlinkUpload(certificateFilename=certificate_filename_pem, keyFilename=certificate_filename_key,
                             userId=user_id, ownerId=owner_id, ownerAuthorization=owner_authorization,
                             description=description, intent=intent)

def download(certificate_filename_pem: str, certificate_filename_key: str, record_id: str) -> str:
    return getOathlinkDownload(certificateFilename=certificate_filename_pem, keyFilename=certificate_filename_key,
                               oathId=record_id)

def decrypt(record_id_encrypted: str, secret: str, certificate_filename_pem: str, certificate_filename_key: str) -> str:
    # if certificate_filename_pem is None or certificate_filename_key is None:
    #     return decryptOathId(oathIdEncrypted=record_id_encrypted, oathSecret=secret)
    return decryptOathIdRemote(certificateFilename=certificate_filename_pem, keyFilename=certificate_filename_key,
                               oathIdEncrypted=record_id_encrypted, oathSecret=secret)

def delete(certificate_filename_pem: str, certificate_filename_key: str, record_id: str = None) -> list:
    return archiveOathlink(certificateFilename=certificate_filename_pem, keyFilename=certificate_filename_key,
                           recordId=record_id)

def cancel(certificate_filename_pem: str, certificate_filename_key: str, record_id: str = None) -> list:
    return cancelOathlink(certificateFilename=certificate_filename_pem, keyFilename=certificate_filename_key,
                          recordId=record_id)

def agent_create(certificate_filename_pem: str, certificate_filename_key: str, serial: str, description: str) -> str:
    return createAgent(certificateFilename=certificate_filename_pem, keyFilename=certificate_filename_key,
                       serial=serial, description=description)

def agent_ip_add(certificate_filename_pem: str, certificate_filename_key: str, ip: str) -> str:
    return addIP(certificateFilename=certificate_filename_pem, keyFilename=certificate_filename_key, ip=ip)

def agent_ip_remove(certificate_filename_pem: str, certificate_filename_key: str, ip: str) -> str:
    return removeIP(certificateFilename=certificate_filename_pem, keyFilename=certificate_filename_key, ip=ip)

def agent_link(certificate_filename_pem: str, certificate_filename_key: str, user_id: str) -> str:
    return linkAgents(certificateFilename=certificate_filename_pem, keyFilename=certificate_filename_key, userId=user_id)

def agent_unlink(certificate_filename_pem: str, certificate_filename_key: str, user_id: str) -> str:
    return unlinkAgents(certificateFilename=certificate_filename_pem, keyFilename=certificate_filename_key, userId=user_id)

def report_record(certificate_filename_pem: str, certificate_filename_key: str, record_id: str = None) -> list:
    return reportRecord(certificateFilename=certificate_filename_pem, keyFilename=certificate_filename_key,
                        recordId=record_id)

def report_history(certificate_filename_pem: str, certificate_filename_key: str, record_id: str = None) -> str:
    return reportHistory(certificateFilename=certificate_filename_pem, keyFilename=certificate_filename_key,
                         recordId=record_id)

def report_outstanding(certificate_filename_pem: str, certificate_filename_key: str) -> str:
    return reportOutstanding(certificateFilename=certificate_filename_pem, keyFilename=certificate_filename_key)
