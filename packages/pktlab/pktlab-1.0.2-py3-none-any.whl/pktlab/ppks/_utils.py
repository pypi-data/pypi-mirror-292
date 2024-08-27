#
# Python3 script for general utility functions and constants.
# By TB Yan
# Last updated: 2022/10/03
#

from multiprocessing.sharedctypes import Value
import os
import getpass
import ipaddress

from cryptography.hazmat.primitives.hashes import Hash, SHA256
from cryptography.hazmat.primitives.serialization import \
    Encoding, PublicFormat, \
    load_pem_public_key, load_pem_private_key
from cryptography.x509 import \
    ObjectIdentifier, load_pem_x509_csr, ExtensionNotFound
from cryptography.exceptions import InvalidSignature
from math import ceil
from sys import stderr

from .LocalFSPPKSKeyManager import LocalFSPPKSKeyManager
from .LocalFSPPKSStateManager import LocalFSPPKSStateManager
from .PacketLabConstants import PacketLabConstants as pconst

#
# EXPORTED CONSTANTS
#

KEYMAN_LS = [
    LocalFSPPKSKeyManager
]
STATEMAN_LS = [
    LocalFSPPKSStateManager
]

KEY_SUBCMD_SET  = {"key", "k"}
CSR_SUBCMD_SET  = {"certificatesigningrequest", "csr"}
CERT_SUBCMD_SET = {"certificate", "cert"}

#
# UTILITY METHOD DEFINITIONS
#

## Info field name value checker

def is_valid_info_name_str(name_str): # for unknown info fields
    valid_special_char = {
        '_', '-',
    }

    # at least one char needed
    if len(name_str) == 0:
        return False

    # only special char and alnum allowed
    for i in name_str:
        if i not in valid_special_char and \
           not is_alnum(i):
           return False

    return True

def is_valid_cert_type_str(cert_type_str):
    cert_type_str_set = {
        pconst.PKTLAB_CERT_TYPE_STR_SUBCMD,
        pconst.PKTLAB_CERT_TYPE_STR_PUBCMD,
        pconst.PKTLAB_CERT_TYPE_STR_EXPPRIV,
        pconst.PKTLAB_CERT_TYPE_STR_DELPRIV,
        pconst.PKTLAB_CERT_TYPE_STR_AGENT,
    }

    return cert_type_str in cert_type_str_set

def is_valid_del_type_str(del_type_str):
    del_type_str_set = {
        pconst.PKTLAB_DEL_TYPE_STR_EXPPRIV,
        pconst.PKTLAB_DEL_TYPE_STR_REPPRIV,
    }

    dup_check = set()
    del_type_ls = del_type_str.split(sep=",")
    for i in del_type_ls:
        if i not in del_type_str_set:
            return False # unknown del_type str

        if i in dup_check:
            return False # duplicate del_type str
        dup_check.add(i)

    return True

def is_valid_info_value_str(value_str): # for free-style fields
    valid_special_char = {
        '_', '-', '.', ':', '[', ']', ',', '/', '(', ')', ' ', '\t',
    }

    # only special char and alnum allowed
    for i in value_str:
        if i not in valid_special_char and \
           not is_alnum(i):
           return False

    return True

def is_valid_info(info_str):
    nv_store, _ = parse_info(info_str)
    return nv_store is not None and len(nv_store) != 0

## Limit field name value checker

def is_valid_limit_name_str(name_str): # for unknown limit fields
    valid_special_char = {
        '_', '-',
    }

    # at least one char needed
    if len(name_str) == 0:
        return False

    if len(name_str) == 1 and name_str == '*':
        return False

    if name_str[0] == '*':
        name_str = name_str[1:]

    # only special char and alnum allowed
    for i in name_str:
        if i not in valid_special_char and \
           not is_alnum(i):
           return False

    return True

def is_valid_digest(digest_str):
    # should be a concatenated list of SHA2 digest in hex
    if len(digest_str) == 0 or \
       len(digest_str) % (pconst.PKTLAB_SHA256_DIGEST_LEN*2) != 0:
        return False

    for i in digest_str:
        if not is_xdigit(i):
            return False

    return True

def is_valid_decimal_str(decimal_str):
    if len(decimal_str) == 0:
        return False

    for i in decimal_str:
        if not is_digit(i):
            return False

    return True

def is_valid_rate_str(rate_str):
    # should be in the form of DECIMAL/DECIMAL
    rate_ls = rate_str.split(sep="/", maxsplit=1)

    if len(rate_ls) != 2:
        return False

    cnt, period = rate_ls
    if len(cnt) == 0 or len(period) == 0:
        return False

    for i in cnt:
        if not is_digit(i):
            return False
    for i in period:
        if not is_digit(i):
            return False

    # period cannot be 0
    if int(period) == 0:
        return False

    return True

def is_valid_rate_ls_str(rate_ls_str):
    # should be in the form of RATE,RATE ...
    rate_ls_ls = rate_ls_str.split(sep=",")

    for i in rate_ls_ls:
        if not is_valid_rate_str(i):
            return False

    return True

def is_valid_dest_str(dest_str):
    # should be in the form of ADDR/SUBNET_MASK,ADDR/SUBNET_MASK ...
    # subnet mask can be ignored

    dest_ls = dest_str.split(sep=",")
    for i in dest_ls:
        try:
            ipaddress.ip_network(i)
        except Exception:
            return False

    return True

def is_valid_src_ip_sproof_str(src_ip_sproof_str):
    # should only be 0 (False) or 1 (True)
    return src_ip_sproof_str == "0" or src_ip_sproof_str == "1"


def is_valid_limit_value_str(value_str):
    valid_special_char = {
        '_', '-', '.', ':', '[', ']', ',', '/', '(', ')', ' ', '\t',
    }

    # only special char and alnum allowed
    for i in value_str:
        if i not in valid_special_char and \
           not is_alnum(i):
           return False

    return True

def is_valid_limit(limit_str):
    nv_store, _ = parse_limit(limit_str)
    return nv_store is not None and len(nv_store) != 0

## info/limit field parsers

def parse_info(info_str):
    info_name2val_checker = {
        pconst.PKTLAB_CERT_INFO_CERT_TYPE: is_valid_cert_type_str,
        pconst.PKTLAB_CERT_INFO_DEL_TYPE:  is_valid_del_type_str,
        pconst.PKTLAB_CERT_INFO_CERT_DESC: is_valid_info_value_str,
    }

    info_ls = info_str.split(sep=";")

    # line must end in ';'
    if len(info_ls[-1]) != 0:
        return None, "info field does not end with ';'"

    # check validity of present pair
    # also record nv for futher checks
    nv_store = {}
    for nv_str in info_ls[:-1]:
        nv_ls = nv_str.split(sep="=", maxsplit=1)
        if len(nv_ls) != 2:
            return None, "'{};' is not in NAME=VALUE; format".format(nv_str)

        name, val = nv_ls
        if name not in info_name2val_checker:
            if not is_valid_info_name_str(name) or \
               not is_valid_info_value_str(val):
                return None, \
                    "'{};' contains invalid char for name/value".format(nv_str)
        elif not info_name2val_checker[name](val):
            return None, \
                "'{}' does not conform to '{}' nv-pair requirements".format(val, name)

        if name in nv_store:
            return None, "Duplicate '{}' nv-pair".format(name)

        # we store unrecognized nv pair as well
        nv_store[name] = val

    # check validity for each field
    if pconst.PKTLAB_CERT_INFO_CERT_TYPE not in nv_store:
        return None, "'cert_type' nv-pair not present"
    if (nv_store[pconst.PKTLAB_CERT_INFO_CERT_TYPE] == \
        pconst.PKTLAB_CERT_TYPE_STR_DELPRIV) != \
       (pconst.PKTLAB_CERT_INFO_DEL_TYPE in nv_store):
        return None, "'del_type' nv-pair field invalid presence"

    return nv_store, None

def parse_aux_info(aux_info_str):
    aux_info_ls = aux_info_str.split(sep=";")

    # line must end in ';'
    if len(aux_info_ls[-1]) != 0:
        return None, "aux info str does not end with ';'"

    # record nv, and only check format and dup
    nv_store = {}
    for nv_str in aux_info_ls[:-1]:
        nv_ls = nv_str.split(sep="=", maxsplit=1)
        if len(nv_ls) != 2:
            return None, "'{};' is not in NAME=VALUE; format".format(nv_str)

        name, val = nv_ls
        if not is_valid_info_name_str(name) or \
           not is_valid_info_value_str(val):
            return None, \
                "'{};' contains invalid char for name/value".format(nv_str)

        if name in nv_store:
            return None, "Duplicate '{}' nv-pair".format(name)

        nv_store[name] = val

    return nv_store, None

def parse_limit(limit_str):
    limit_name2val_checker = {
        pconst.PKTLAB_CERT_LIMIT_FILT_DIGEST:         is_valid_digest,
        pconst.PKTLAB_CERT_LIMIT_MON_DIGEST:          is_valid_digest,
        pconst.PKTLAB_CERT_LIMIT_MAX_NUM_PRIORITY:    is_valid_decimal_str,
        pconst.PKTLAB_CERT_LIMIT_MAX_SOCKET_COUNT:    is_valid_decimal_str,
        pconst.PKTLAB_CERT_LIMIT_MAX_EXP_PERIOD:      is_valid_decimal_str,
        pconst.PKTLAB_CERT_LIMIT_MAX_SEND_BYTE:       is_valid_decimal_str,
        pconst.PKTLAB_CERT_LIMIT_MAX_SEND_PKT:        is_valid_decimal_str,
        pconst.PKTLAB_CERT_LIMIT_MAX_RECV_BYTE:       is_valid_decimal_str,
        pconst.PKTLAB_CERT_LIMIT_MAX_RECV_PKT:        is_valid_decimal_str,
        pconst.PKTLAB_CERT_LIMIT_MAX_BURST_RATE_BYTE: is_valid_rate_ls_str,
        pconst.PKTLAB_CERT_LIMIT_MAX_BURST_RATE_PKT:  is_valid_rate_ls_str,
        pconst.PKTLAB_CERT_LIMIT_VALID_DEST:          is_valid_dest_str,
        pconst.PKTLAB_CERT_LIMIT_SRC_IP_SPROOF:       is_valid_src_ip_sproof_str,
    }

    limit_ls = limit_str.split(sep=";")

    # line must end in ';'
    if len(limit_ls[-1]) != 0:
        return None, "limit field does not end with ';'"

    # check validity of present pair
    # also record nv for futher checks
    nv_store = {}
    for nv_str in limit_ls[:-1]:
        nv_ls = nv_str.split(sep="=", maxsplit=1)
        if len(nv_ls) != 2:
            return None, "'{};' is not in NAME=VALUE; format".format(nv_str)

        name, val = nv_ls
        if not is_valid_limit_name_str(name):
            return None, "'{}' not valid name".format(name)

        optional = False
        if name[0] == '*':
            optional = True
            name = name[1:]

        unknown = False # as in should be known but unknown
        if name not in limit_name2val_checker:
            if optional:
                unknown = True

            if not is_valid_limit_value_str(val):
                return None, "'{}' not valid value".format(val)
        elif not limit_name2val_checker[name](val):
            return None, \
                "'{}' does not conform to '{}' nv-pair requirements".format(val, name)

        if name in nv_store:
            return None, "Duplicate '{}' nv-pair".format(name)

        # we store unrecognized nv pair as well
        nv_store[name] = (optional, val, unknown)

    return nv_store, None

def parse_aux_limit(aux_limit_str):
    aux_limit_ls = aux_limit_str.split(sep=";")

    # line must end in ';'
    if len(aux_limit_ls[-1]) != 0:
        return None, "limit field does not end with ';'"

    # record nv, and only check format and dup
    nv_store = {}
    for nv_str in aux_limit_ls[:-1]:
        nv_ls = nv_str.split(sep="=", maxsplit=1)
        if len(nv_ls) != 2:
            return None, "'{};' is not in NAME=VALUE; format".format(nv_str)

        name, val = nv_ls
        if not is_valid_limit_name_str(name):
            return None, "'{}' not valid name".format(name)

        optional = False
        if name[0] == '*':
            optional = True
            name = name[1:]

        if not is_valid_limit_value_str(val):
            return None, "'{}' not valid value".format(val)

        if name in nv_store:
            return None, "Duplicate '{}' nv-pair".format(name)

        # we store unrecognized nv pair as well
        # unknown (3rd field) is the same as optional
        # unknown as in should be known but unknown
        nv_store[name] = (optional, val, optional)

    return nv_store, None

## check char utilities

def is_alpha(c):
    return \
        ('a' <= c and c <= 'z') or \
        ('A' <= c and c <= 'Z')

def is_digit(c):
    return ('0' <= c and c <= '9')

def is_alnum(c):
    return is_digit(c) or is_alpha(c)

def is_xdigit(c):
    return is_digit(c) or \
        ('a' <= c and c <= 'f') or \
        ('A' <= c and c <= 'F')

## other misc utility
def fix0x(string):
    return string[2:] if string[:2] == "0x" else string

def get_nvp_str(name, value):
    return "{}={};".format(name,value)

def get_nvp_str_opt(name, value, optional):
    if optional:
        name = "*"+name
    return get_nvp_str(name, value)

def sha256(data):
    digest = Hash(SHA256())
    digest.update(data)
    return digest.finalize()

def get_raw_pubkey(pubkey):
    return pubkey.public_bytes(Encoding("Raw"), PublicFormat("Raw"))

def is_end_cert(cert_type):
    return cert_type == pconst.PKTLAB_CERT_TYPE_STR_SUBCMD or \
           cert_type == pconst.PKTLAB_CERT_TYPE_STR_PUBCMD or \
           cert_type == pconst.PKTLAB_CERT_TYPE_STR_AGENT

def can_contain_limitation(cert_type, del_type):
    return (cert_type == pconst.PKTLAB_CERT_TYPE_STR_EXPPRIV) or \
           (cert_type == pconst.PKTLAB_CERT_TYPE_STR_DELPRIV and \
            del_type is not None and \
            pconst.PKTLAB_DEL_TYPE_STR_EXPPRIV in del_type)

def yes_no_prompt(start_text, fail_text, default=-1):
    """
    default parameter meaning:
        -1 -> enter means no
         0 -> enter is incorrect input
         1 -> enter means yes
    """

    assert default in range(-1, 2)

    while True:
        reply = input(start_text).lower()

        if len(reply) == 0:
            if default == -1:
                return False
            elif default == 1:
                return True
            # do nothing when default == 0
        elif reply == "y" or reply == "yes":
            return True
        elif reply == "n" or reply == "no":
            return False

        print(fail_text)

def multistr_fmt(str_ls):
    return "".join(["\n\t"+i for i in str_ls])

def multihex_fmt(hex_ls):
    hex_seg = []
    for indx, h in enumerate(hex_ls):
        tmp = [h[32*i:32*i+16] + " " + h[32*i+16:32*(i+1)] for i in range(ceil(len(h)/32))]
        if indx != len(hex_ls)-1:
            tmp[-1] = tmp[-1]+","
        if indx != 0:
            hex_seg.append("")
        hex_seg += tmp
    return "".join(["\n\t"+i for i in hex_seg])

def warn(string):
    print("Warning: {}".format(string), file=stderr)

def is_index(s):
    try:
        rst = int(s.strip())
    except Exception as e:
        return False

    if rst < 0:
        return False
    return True

def try_get_extension(oidstr, extensions):
    try:
        return extensions.get_extension_for_oid(ObjectIdentifier(oidstr))
    except ExtensionNotFound:
        return None

def safe_decode(b):
    return b if b is None else b.decode()

def safe_parse_digests(all_digests):
    if all_digests is None: return None
    digest_hex_len = pconst.PKTLAB_SHA256_DIGEST_LEN*2
    return [
        all_digests[i:i+digest_hex_len]
        for i in range(0, len(all_digests), digest_hex_len)]

def safe_combine_str(s1, s2):
    if s1 is None and s2 is None:
        return None

    if s1 is None:
        s1 = ""
    if s2 is None:
        s2 = ""
    return s1+s2

def safe_concat(ls, sep=""):
    if ls is None:
        return None
    return sep.join(ls)

def list_names(start_output, name_ls, start_indx=0):
    print(start_output)
    for i, name in enumerate(name_ls):
        print("\t{}. {}".format(i+start_indx, name))
    return

def is_cert_valid(cert, signer_pubkey):
    try:
        signer_pubkey.verify(cert.signature, cert.tbs_certificate_bytes)
        return True
    except InvalidSignature:
        return False

def is_good_del_type(dt):
    if not isinstance(dt, bytes) or \
       len(dt) != 1 or \
       (dt[0] & \
        ~pconst.PKTLAB_DEL_TYPE_EXPPRIV & \
        ~pconst.PKTLAB_DEL_TYPE_REPPRIV) != 0:
        return False
    return True

def comp_del_type(del_exppriv, del_reppriv):
    if not del_exppriv and not del_reppriv:
        return None

    ret_ls = []
    if del_exppriv:
        ret_ls.append(pconst.PKTLAB_DEL_TYPE_STR_EXPPRIV)
    if del_reppriv:
        ret_ls.append(pconst.PKTLAB_DEL_TYPE_STR_REPPRIV)
    return ",".join(ret_ls)

def decode_del_type(del_type):
    # does not check if del type is well-formed
    return \
        del_type[0] & pconst.PKTLAB_DEL_TYPE_EXPPRIV != 0, \
        del_type[0] & pconst.PKTLAB_DEL_TYPE_REPPRIV != 0

#
# LOAD FUNCTIONS
#

def prompt_passphrase(privkey_name):
    passphrase = getpass.getpass(
        "Please enter passphrase for Ed25519 private key ({}): ".format(
            privkey_name))
    return bytes(passphrase, encoding="utf8")

def load_privkey_ppksman(ppksman, indx):
    privkey = ppksman.get_privkey(indx) # try loading without passphrase
    if privkey is not None:
        return privkey

    # prompt passphrase and load with passphrase
    passphrase = prompt_passphrase("privkey list indx: {}".format(indx))
    return ppksman.get_privkey(indx, passphrase)

def load_key_ppksman(ppksman, indx):
    pubkey_ls = ppksman.get_pubkey_list()
    if indx in range(len(pubkey_ls)):
        return ppksman.get_pubkey(indx), None

    privkey = load_privkey_ppksman(ppksman, indx-len(pubkey_ls))
    return privkey.public_key(), privkey

def load_privkey_file(path):
    with open(path, "rb") as fp:
        data = fp.read()

    try:
        privkey = load_pem_private_key(data, None)
        return privkey.public_key(), privkey # try loading without passphrase
    except TypeError:
        pass # need passphrase

    # prompt passphrase and load with passphrase
    passphrase = prompt_passphrase(path)
    privkey = load_pem_private_key(data, passphrase)
    return privkey.public_key(), privkey

def load_key_file(path):
    name = os.path.basename(os.path.abspath(path))
    if name[-4:] == ".pub":
        with open(path, "rb") as fp:
            pubkey = load_pem_public_key(fp.read())
        privkey = None
    else:
        pubkey, privkey = load_privkey_file(path)

    return pubkey, privkey

def load_csr_file(path):
    with open(path, "rb") as fp:
        data = fp.read()
    return load_pem_x509_csr(data)

def load_config(path):
    if not os.path.exists(path) or not os.path.isfile(path):
        return None, None

    with open(path, "r") as fp:
        data = fp.readlines()

    keyman_configstr_name_set = {c.get_configstr_name() for c in KEYMAN_LS}
    stateman_configstr_name_set = {c.get_configstr_name() for c in STATEMAN_LS}
    assert len(keyman_configstr_name_set.intersection(stateman_configstr_name_set)) == 0

    keyman_configstr_tup = None
    stateman_configstr_tup = None

    for line in data:
        if len(line) > 0 and line[0] == "#":
            continue # comments

        parsedline = line.strip().split(maxsplit=1)
        if len(parsedline) == 0:
            continue
        elif parsedline[0] in keyman_configstr_name_set:
            if keyman_configstr_tup is not None:
                raise ValueError("Bad config format: multiple KeyManager configstr")
            keyman_configstr_tup = (parsedline[0], parsedline[1])
        elif parsedline[0] in stateman_configstr_name_set:
            if stateman_configstr_tup is not None:
                raise ValueError("Bad config format: multiple StateManager configstr")
            stateman_configstr_tup = (parsedline[0], parsedline[1])
        else: # Bad config format
            raise ValueError(
                "Bad config format: unknown configstr name ({})".format(parsedline[0]))

    return keyman_configstr_tup, stateman_configstr_tup