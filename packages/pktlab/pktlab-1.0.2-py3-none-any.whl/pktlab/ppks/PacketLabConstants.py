#
# Python3 script for pktlab constants.
# By TB Yan
# Last updated: 2022/10/03
#

# CLASS DEFINITIONS
#

#
# pktlab (cert) constants
# todo: import them from pktlab.h header with cython
#

class PacketLabConstants:
    PKTLAB_SHA256_DIGEST_LEN  = 32
    PKTLAB_KEYID_LEN          = PKTLAB_SHA256_DIGEST_LEN
    PKTLAB_FILTER_DIGEST_LEN  = PKTLAB_SHA256_DIGEST_LEN
    PKTLAB_MONITOR_DIGEST_LEN = PKTLAB_SHA256_DIGEST_LEN

    # X.509 Private Extension OIDs
    PKTLAB_EXT_PKTLAB_CERT_INFO  = "1.2.3.1"
    PKTLAB_EXT_PKTLAB_CERT_LIMIT = "1.2.3.3"

    # Cert Info Field Defined Names
    PKTLAB_CERT_INFO_CERT_TYPE = "cert_type"
    PKTLAB_CERT_INFO_DEL_TYPE  = "del_type"
    PKTLAB_CERT_INFO_CERT_DESC = "cert_desc"

    # (Cert Info) Certificate Type Value
    PKTLAB_CERT_TYPE_STR_SUBCMD  = "subcmd"
    PKTLAB_CERT_TYPE_STR_PUBCMD  = "pubcmd"
    PKTLAB_CERT_TYPE_STR_EXPPRIV = "exppriv"
    PKTLAB_CERT_TYPE_STR_DELPRIV = "delpriv"
    PKTLAB_CERT_TYPE_STR_AGENT   = "agent"

    # (Cert Info) Delegation Type Value
    PKTLAB_DEL_EXPPRIV = 0x1
    PKTLAB_DEL_REPPRIV = 0x2

    PKTLAB_DEL_TYPE_STR_EXPPRIV = "exppriv"
    PKTLAB_DEL_TYPE_STR_REPPRIV = "reppriv"

    # Cert Limit Field Defined Names
    PKTLAB_CERT_LIMIT_FILT_DIGEST         = "filter"
    PKTLAB_CERT_LIMIT_MON_DIGEST          = "monitor"
    PKTLAB_CERT_LIMIT_MAX_NUM_PRIORITY    = "max_num_priority"
    PKTLAB_CERT_LIMIT_MAX_SOCKET_COUNT    = "max_socket_count"
    PKTLAB_CERT_LIMIT_MAX_EXP_PERIOD      = "max_exp_period"
    PKTLAB_CERT_LIMIT_MAX_SEND_BYTE       = "max_send_byte"
    PKTLAB_CERT_LIMIT_MAX_SEND_PKT        = "max_send_pkt"
    PKTLAB_CERT_LIMIT_MAX_RECV_BYTE       = "max_recv_byte"
    PKTLAB_CERT_LIMIT_MAX_RECV_PKT        = "max_recv_pkt"
    PKTLAB_CERT_LIMIT_MAX_BURST_RATE_BYTE = "max_burst_rate_byte"
    PKTLAB_CERT_LIMIT_MAX_BURST_RATE_PKT  = "max_burst_rate_pkt"
    PKTLAB_CERT_LIMIT_VALID_DEST          = "valid_dest"
    PKTLAB_CERT_LIMIT_SRC_IP_SPROOF       = "src_ip_sproof"

    PKTLAB_EXT_ASN1_SPEC  = \
"""
PacketLabExtensions DEFINITIONS ::=
BEGIN

    -- PacketLab Certificate Information --
    PacketLabCertificateInformation ::= OCTET STRING (SIZE(1..MAX))

    -- PacketLab Certificate Limitation --
    PacketLabCertificateLimitation ::= OCTET STRING (SIZE(1..MAX))

END
"""