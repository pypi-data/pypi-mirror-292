# standard gdd definitions
from gbdtransformation.designs import kinds as std_kinds
from gbdtransformation.designs import status as std_status

# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = [
    "http://www.oami.europa.eu/schemas/design_Transaction",
    "http://www.oami.europa.eu/schemas/design_IndicationProduct",
    "http://www.oami.europa.eu/schemas/design",
]

def get_appdate(appdate, appnum):
    return appdate

def get_designs_count(design, header):
    return '1'

def get_designs_pos(design, header):
    return '1'

# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------
def translate_kind(desgin, header):
    code = header.TransactionCode.lower()
    if code == 'ds-search design list':
        return 'Industrial Design'
    raise Exception('Type "%s" is not mapped.' % (code))

def parseForSt13(appnum, des_ref):
    if des_ref.get('DesignIdentifier'):
        return appnum + '-' + des_ref['DesignIdentifier'].split('-')[1]
    else:
        return appnum + '-' +  des_ref['DesignURI'].split('-')[1]

def format_address(address):
    return '%s, %s %s' % (address.AddressStreet,
                          address.AddressPostcode,
                          address.AddressCity)

def format_name(name):
    fname = name.FirstName
    lname = name.LastName

    full_name = [name.FirstName, name.LastName]
    full_name = [f.strip() for f in full_name if f is not None]

    return ' '.join(full_name)


def is_international(header):
    return False

def get_ir_refnum(appnum):
    return appnum

def translate_status(desgin):
    if desgin._operationCode == 'Delete':
        return 'Delete'

    status = desgin.DesignCurrentStatusCode

    if status in ['Application filed',
                  'Application published',
                  'Application under examination',
                  'Registration pending',
                  'Appeal pending',
                  'Registration cancellation pending',
                  'Filed']:
        return 'Pending'

    if status in ['Application refused',
                  'Application withdrawn',
                  'Application opposed',
                  'Registration cancelled',
                  'Registration surrendered',
                  'Design surrendered',
                  'Design declared invalid',
                  'Lack of effects',
                  "Design lapsed",
                  'Ended']:
        return 'Ended'

    if status in ['Registered',
                  'Registered and subject to deferment',
                  'Registered and fully published']:
        return 'Registered'
    if status in ['Registration expired', 'Expired']: return 'Expired'

    raise Exception('Status "%s" not mapped.' % status)