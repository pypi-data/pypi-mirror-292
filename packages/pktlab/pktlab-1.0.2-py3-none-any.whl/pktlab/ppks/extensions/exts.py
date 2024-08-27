#
# Python3 script for custom cryptography extension definitions and helper functions.
# By TB Yan
# Last updated: 2022/10/03
#

from asn1tools import compile_string
from cryptography.x509 import \
    UnrecognizedExtension, ObjectIdentifier

from ..PacketLabConstants import PacketLabConstants as pconst
from .._utils import is_valid_info, is_valid_limit, parse_info, parse_limit

class PacketLabCertificateInformation(UnrecognizedExtension):
    def __init__(self, info_str):
        spec = compile_string(
            pconst.PKTLAB_EXT_ASN1_SPEC, codec="der")

        if not is_valid_info(info_str):
            _, errstr = parse_info(info_str)
            raise ValueError(errstr)

        der_value = bytes(spec.encode("PacketLabCertificateInformation", info_str.encode("utf-8")))
        oid = ObjectIdentifier(pconst.PKTLAB_EXT_PKTLAB_CERT_INFO)
        super().__init__(oid=oid, value=der_value)

class PacketLabCertificateLimitation(UnrecognizedExtension):
    def __init__(self, limit_str):
        spec = compile_string(
            pconst.PKTLAB_EXT_ASN1_SPEC, codec="der")

        if not is_valid_limit(limit_str):
            _, errstr = parse_limit(limit_str)
            raise ValueError(errstr)

        der_value = bytes(spec.encode("PacketLabCertificateLimitation", limit_str.encode("utf-8")))
        oid = ObjectIdentifier(pconst.PKTLAB_EXT_PKTLAB_CERT_LIMIT)
        super().__init__(oid=oid, value=der_value)

# extensions below not used anymore, but regex pattern may be useful afterwards
# class PacketLabUniformResourceIdentifier(UniformResourceIdentifier):
#     def __init__(self, uri):
#         if re.match("^pktlab:\/\/([a-zA-z0-9.-]+)(:[0-9]{1,5})?\/(exp|broker)\/$", uri) is None:
#             raise ValueError("Bad URI")
#         super().__init__(value=uri)

#
# UTILITY METHOD DEFINITIONS
#

def pktlab_ext_get_bytes(ext, oidstr=None):
    if ext is None: return None
    if oidstr is None: oidstr = ext.oid.dotted_string

    if oidstr == pconst.PKTLAB_EXT_PKTLAB_CERT_INFO:
        name = "PacketLabCertificateInformation"
    elif oidstr == pconst.PKTLAB_EXT_PKTLAB_CERT_LIMIT:
        name = "PacketLabCertificateLimitation"
    else:
        raise ValueError("Unknown pktlab extension OID")

    spec = compile_string(
        pconst.PKTLAB_EXT_ASN1_SPEC, codec="der")
    return spec.decode(name, ext.value.value, check_constraints=True)