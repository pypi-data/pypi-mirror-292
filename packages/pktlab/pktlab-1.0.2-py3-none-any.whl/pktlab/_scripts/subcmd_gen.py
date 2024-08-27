#
# Python3 script for the ppksman commandline tool gen subcmd.
# The gen subcmd allows generation of PPKS CSRs, certificates and keys.
# *PPKS: PPKS Public Key System, or PacketLab Public Key System
# By TB Yan
# Last updated: 2022/10/09
#

import os
from getpass import getpass

from cryptography.x509.oid import ExtensionOID
from cryptography.hazmat.primitives.serialization import \
    Encoding, PublicFormat

from ..ppks._utils import \
    parse_info, parse_limit, \
    parse_aux_info, parse_aux_limit, \
    get_nvp_str, get_nvp_str_opt, \
    safe_concat, safe_combine_str, \
    is_index, warn, yes_no_prompt, \
    load_key_ppksman, load_key_file, \
    load_csr_file, try_get_extension, \
    safe_decode, safe_parse_digests, multihex_fmt, \
    comp_del_type, can_contain_limitation, \
    KEY_SUBCMD_SET, CSR_SUBCMD_SET, CERT_SUBCMD_SET
from ..ppks.extensions import pktlab_ext_get_bytes
from ..ppks.PacketLabConstants import PacketLabConstants as pconst

#
# INTERNAL FUNCTIONS
#

def _prompt_new_passphrase():
    passphrase = getpass(
        "Please enter passphrase for Ed25519 private key " +
        "(press enter for no passphrase): ")

    if len(passphrase) != 0:
        passphrase_confirm = getpass("Please re-enter passphrase: ")
        if passphrase != passphrase_confirm:
            print("Passphrase does not match, aborting")
            return None

    return passphrase.encode()

def _genkey(ppksman, keyname, keypath):
    """
    keyname for storing with ppksman
    keypath for storing at additional location
    """

    passphrase = _prompt_new_passphrase()
    pubkey_bytes, privkey_bytes = ppksman.gen_key(keyname, passphrase)

    if keypath is not None:
        oldmask = os.umask(0o77) # only user has permission
        with open(keypath+".pub", "wb") as fp:
            fp.write(pubkey_bytes)
        with open(keypath, "wb") as fp:
            fp.write(privkey_bytes)
        os.umask(oldmask) # restore

    print("Key generation completed")
    return

def _fill_in_prompt_str(base_fmt, use_csr, print_content):
    return base_fmt.format(
        " (from CSR)" if use_csr == 1 else "",
        print_content)

def _fill_in_prompt_str_optional(
        base_fmt, use_csr, optional, print_content):
    if use_csr == 1 and optional:
        comment = " (from CSR; optional)"
    elif use_csr == 1:
        comment = " (from CSR)"
    elif optional:
        comment = " (optional)"
    else:
        comment = ""
    return base_fmt.format(comment, print_content)

def _get_privkey_short_desc(name, privkey):
    return "\n\tKey: {}\n\tLeading 4 bytes of corresponding public key: {}".format(
        name, privkey.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)[:4].hex())

def _get_pubkey_short_desc(name, pubkey):
    return "\n\tKey: {}\n\tLeading 4 bytes: {}".format(
        name, pubkey.public_bytes(Encoding.Raw, PublicFormat.Raw)[:4].hex())

def _prompt_input_info(
        cert_type_tup,
        signer_privkey_tup,
        signee_pubkey_tup,
        signee_privkey_tup,
        start_time_tup, end_time_tup,
        del_type_tup, cert_desp_tup,
        pathlen_tup, filter_digests_tup,
        monitor_digests_tup,
        max_num_priority_tup,
        max_socket_count_tup,
        max_exp_period_tup,
        max_send_byte_tup,
        max_send_pkt_tup,
        max_recv_byte_tup,
        max_recv_pkt_tup,
        max_burst_rate_byte_tup,
        max_burst_rate_pkt_tup,
        valid_dest_tup,
        src_ip_sproof_tup,
        csr_aux_info_str_tup,
        cmdline_aux_info_str_tup,
        csr_aux_limit_str_tup,
        cmdline_aux_limit_str_tup,
        signrst, ask):
    """
    Return True for can continue, return False if should terminate.
    Note that the meaning of the second value (indx 1) of the input tuples:
        0: value not supplied by user, i.e. should not prompt
        1: value supplied by user via CSR
        2: value supplied by user via commandline
    """

    print("--------------------------------------------------------------")
    print("> Proceeding to sign {} with the following information:".format(signrst))
    print_strs = []

    if cert_type_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "- Certificate type{}: {}",
                cert_type_tup[1],
                cert_type_tup[0]))

    if signer_privkey_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "- Signer private key{}:{}",
                signer_privkey_tup[1],
                _get_privkey_short_desc(
                    signer_privkey_tup[2],
                    signer_privkey_tup[0])))

    if signee_pubkey_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "- Signee public key{}:{}",
                signee_pubkey_tup[1],
                _get_pubkey_short_desc(
                    signee_pubkey_tup[2],
                    signee_pubkey_tup[0])))

    if signee_privkey_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "- Signee private key{}:{}",
                signee_privkey_tup[1],
                _get_privkey_short_desc(
                    signee_privkey_tup[2],
                    signee_privkey_tup[0])))

    if start_time_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "- Valid not before (Epoch time){}: {}",
                start_time_tup[1], start_time_tup[0]))

    if end_time_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "- Valid not after (Epoch time){}:  {}",
                end_time_tup[1], end_time_tup[0]))

    # info fields
    if del_type_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "- Delegation type{}: '{}'",
                del_type_tup[1], del_type_tup[0]))

    if cert_desp_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "- Certificate description{}: '{}'",
                cert_desp_tup[1], cert_desp_tup[0]))

    if csr_aux_info_str_tup[1] != 0:
        assert csr_aux_info_str_tup[1] == 1
        print_strs.append(
            _fill_in_prompt_str(
                "- Additional certificate information string{}: '{}'",
                1, csr_aux_info_str_tup[0]))
    if cmdline_aux_info_str_tup[1] != 0:
        assert cmdline_aux_info_str_tup[1] == 2
        print_strs.append(
            _fill_in_prompt_str(
                "- Additional certificate information string{}: '{}'",
                2, cmdline_aux_info_str_tup[0]))

    # separate privilege limitations printing for clarity
    if can_contain_limitation(cert_type_tup[0], del_type_tup[0]):
        print_strs.append(
            "--------------------------------------------------------------")
        print_strs.append(
            "> With the following limitations included:")

    # basic constrainsts fields
    if pathlen_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str(
                "- Path length{}: {}",
                pathlen_tup[1], pathlen_tup[0]))

    # limit fields
    if filter_digests_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str_optional(
                "- Filter digests{}:{}",
                filter_digests_tup[1],
                filter_digests_tup[2],
                multihex_fmt(filter_digests_tup[0])))
    if monitor_digests_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str_optional(
                "- Monitor digests{}:{}",
                monitor_digests_tup[1],
                monitor_digests_tup[2],
                multihex_fmt(monitor_digests_tup[0])))

    if max_num_priority_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str_optional(
                "- Max priority number{}: {}",
                max_num_priority_tup[1],
                max_num_priority_tup[2],
                max_num_priority_tup[0]))

    if max_socket_count_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str_optional(
                "- Max socket count number{}: {}",
                max_socket_count_tup[1],
                max_socket_count_tup[2],
                max_socket_count_tup[0]))

    if max_exp_period_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str_optional(
                "- Max experiment period (in pktlab ticks){}: {}",
                max_exp_period_tup[1],
                max_exp_period_tup[2],
                max_exp_period_tup[0]))

    if max_send_byte_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str_optional(
                "- Max send byte cnt{}: {}",
                max_send_byte_tup[1],
                max_send_byte_tup[2],
                max_send_byte_tup[0]))
    if max_send_pkt_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str_optional(
                "- Max send pkt cnt{}: {}",
                max_send_pkt_tup[1],
                max_send_pkt_tup[2],
                max_send_pkt_tup[0]))

    if max_recv_byte_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str_optional(
                "- Max recv byte cnt{}: {}",
                max_recv_byte_tup[1],
                max_recv_byte_tup[2],
                max_recv_byte_tup[0]))
    if max_recv_pkt_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str_optional(
                "- Max recv pkt cnt{}: {}",
                max_recv_pkt_tup[1],
                max_recv_pkt_tup[2],
                max_recv_pkt_tup[0]))

    if max_burst_rate_byte_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str_optional(
                "- Max byte burst rate (in X-bytes/Y-pktlab ticks){}: '{}'",
                max_burst_rate_byte_tup[1],
                max_burst_rate_byte_tup[2],
                ",".join(max_burst_rate_byte_tup[0])))
    if max_burst_rate_pkt_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str_optional(
                "- Max pkt burst rate (in X-pkts/Y-pktlab ticks){}: '{}'",
                max_burst_rate_pkt_tup[1],
                max_burst_rate_pkt_tup[2],
                ",".join(max_burst_rate_pkt_tup[0])))

    if valid_dest_tup[1] != 0:
        print_strs.append(
            _fill_in_prompt_str_optional(
                "- Allowed destination subnets{}: '{}'",
                valid_dest_tup[1],
                valid_dest_tup[2],
                ",".join(valid_dest_tup[0])))

    if src_ip_sproof_tup[1] != 0:
        src_ip_sproof: bool
        if src_ip_sproof_tup[0] == 1:
            src_ip_sproof = True
        elif src_ip_sproof_tup[0] == 0:
            src_ip_sproof = False
        else:
            raise ValueError("Unrecognized source IP sproof value, should be 0 or 1")
        print_strs.append(
            _fill_in_prompt_str_optional(
                "- Source IP sproof{}: {}",
                src_ip_sproof_tup[1],
                src_ip_sproof_tup[2],
                src_ip_sproof))

    if csr_aux_limit_str_tup[1] != 0:
        assert csr_aux_limit_str_tup[1] == 1
        print_strs.append(
            _fill_in_prompt_str(
                "- Additional certificate limitation string{}: '{}'",
                1, csr_aux_limit_str_tup[0]))
    if cmdline_aux_limit_str_tup[1] != 0:
        assert cmdline_aux_limit_str_tup[1] == 2
        print_strs.append(
            _fill_in_prompt_str(
                "- Additional certificate limitation string{}: '{}'",
                2, cmdline_aux_limit_str_tup[0]))

    for print_str in print_strs:
        print(print_str)
    print("--------------------------------------------------------------")

    if ask:
        return yes_no_prompt(
            start_text="Is the above information correct? (y/N) ",
            fail_text="Unrecognized input, please try again")

    return True

def _prep_data_tup(csr_data, passed_data):
    if csr_data is None and passed_data is None:
        prompt_type = 0
        data = None
    elif passed_data is not None:
        prompt_type = 2
        data = passed_data
    else:
        prompt_type = 1
        data = csr_data

    return (data, prompt_type)

def _prep_data_tup_key(csr_data, passed_data, passed_data_name):
    tup = _prep_data_tup(csr_data, passed_data)
    if csr_data is None and passed_data is None:
        return (*tup, "not supplied")
    elif passed_data is not None:
        return (*tup, passed_data_name)
    else:
        return (*tup, "from CSR")

def _prep_data_tup_limit(
        csr_data, passed_data, csr_data_opt, passed_data_opt):
    # last field value is to record required or not
    tup = _prep_data_tup(csr_data, passed_data)
    if csr_data is None and passed_data is None:
        return (*tup, False)
    elif passed_data is not None:
        return (passed_data, tup[1], passed_data_opt)
    else:
        return (csr_data, tup[1], csr_data_opt)

def _warn_unknown_aux_limit_str(aux_limit_str):
    if aux_limit_str is None:
        return

    aux_limit_dict, errstr = parse_aux_limit(aux_limit_str)
    if aux_limit_dict is None:
        raise ValueError("Auxiliary limit field string invalid: {}".format(errstr))

    for i in aux_limit_dict:
        if aux_limit_dict[i][2]:
            warn("Unrecognized optional name-value pair in Auxiliary limit field string"
                " (name:{},value:{})".format(i,aux_limit_dict[i][1]))
    return

def _sign_csr(
        ppksman, cert_type,
        signee_privkey,
        signee_privkey_name,
        del_type, cert_desp,
        pathlen, filter_digests,
        monitor_digests,
        max_num_priority, max_socket_count,
        max_exp_period,
        max_send_byte, max_send_pkt,
        max_recv_byte, max_recv_pkt,
        max_burst_rate_byte, max_burst_rate_pkt,
        valid_dest, src_ip_sproof, aux_info_str, aux_limit_str,
        opt_filter_digests,
        opt_monitor_digests,
        opt_max_num_priority, opt_max_socket_count,
        opt_max_exp_period,
        opt_max_send_byte, opt_max_send_pkt,
        opt_max_recv_byte, opt_max_recv_pkt,
        opt_max_burst_rate_byte, opt_max_burst_rate_pkt,
        opt_valid_dest, opt_src_ip_sproof, path, ask):

    # warn about optional unrecognzied nv pairs in aux_limit_str
    _warn_unknown_aux_limit_str(aux_limit_str)

    # prompt for confirmation
    if not _prompt_input_info(
            cert_type_tup=(cert_type, 2),
            signer_privkey_tup=(None, 0, ""),
            signee_pubkey_tup=(None, 0, ""),
            signee_privkey_tup=(signee_privkey, 2, signee_privkey_name),
            start_time_tup=(None, 0),
            end_time_tup=(None, 0),
            del_type_tup=_prep_data_tup(None, del_type),
            cert_desp_tup=_prep_data_tup(None, cert_desp),
            pathlen_tup=_prep_data_tup(None, pathlen),
            filter_digests_tup=
                _prep_data_tup_limit(
                    None, filter_digests,
                    False, opt_filter_digests),
            monitor_digests_tup=
                _prep_data_tup_limit(
                    None, monitor_digests,
                    False, opt_monitor_digests),
            max_num_priority_tup=
                _prep_data_tup_limit(
                    None, max_num_priority,
                    False, opt_max_num_priority),
            max_socket_count_tup=
                _prep_data_tup_limit(
                    None, max_socket_count,
                    False, opt_max_socket_count),
            max_exp_period_tup=
                _prep_data_tup_limit(
                    None, max_exp_period,
                    False, opt_max_exp_period),
            max_send_byte_tup=
                _prep_data_tup_limit(
                    None, max_send_byte,
                    False, opt_max_send_byte),
            max_send_pkt_tup=
                _prep_data_tup_limit(
                    None, max_send_pkt,
                    False, opt_max_send_pkt),
            max_recv_byte_tup=
                _prep_data_tup_limit(
                    None, max_recv_byte,
                    False, opt_max_recv_byte),
            max_recv_pkt_tup=
                _prep_data_tup_limit(
                    None, max_recv_pkt,
                    False, opt_max_recv_pkt),
            max_burst_rate_byte_tup=
                _prep_data_tup_limit(
                    None, max_burst_rate_byte,
                    False, opt_max_burst_rate_byte),
            max_burst_rate_pkt_tup=
                _prep_data_tup_limit(
                    None, max_burst_rate_pkt,
                    False, opt_max_burst_rate_pkt),
            valid_dest_tup=
                _prep_data_tup_limit(
                    None, valid_dest,
                    False, opt_valid_dest),
            src_ip_sproof_tup=
                _prep_data_tup_limit(
                    None, src_ip_sproof,
                    False, opt_src_ip_sproof),
            csr_aux_info_str_tup=(None, 0),
            cmdline_aux_info_str_tup=_prep_data_tup(None, aux_info_str),
            csr_aux_limit_str_tup=(None, 0),
            cmdline_aux_limit_str_tup=_prep_data_tup(None, aux_limit_str),
            signrst="CSR",
            ask=ask):
        print("Command aborted")
        return

    csr = ppksman.gen_csr(
        name=os.path.basename(path),
        cert_type=cert_type,
        signee_privkey=signee_privkey,
        del_type=del_type,
        cert_desp=cert_desp,
        pathlen=pathlen,
        filter_digests=safe_concat(filter_digests),
        monitor_digests=safe_concat(monitor_digests),
        max_num_priority=max_num_priority,
        max_socket_count=max_socket_count,
        max_exp_period=max_exp_period,
        max_send_byte=max_send_byte,
        max_send_pkt=max_send_pkt,
        max_recv_byte=max_recv_byte,
        max_recv_pkt=max_recv_pkt,
        max_burst_rate_byte=safe_concat(max_burst_rate_byte, ","),
        max_burst_rate_pkt=safe_concat(max_burst_rate_pkt, ","),
        valid_dest=safe_concat(valid_dest, ","),
        src_ip_sproof=src_ip_sproof,
        aux_info_str=aux_info_str,
        aux_limit_str=aux_limit_str,
        opt_filter_digests=opt_filter_digests,
        opt_monitor_digests=opt_monitor_digests,
        opt_max_num_priority=opt_max_num_priority,
        opt_max_socket_count=opt_max_socket_count,
        opt_max_exp_period=opt_max_exp_period,
        opt_max_send_byte=opt_max_send_byte,
        opt_max_send_pkt=opt_max_send_pkt,
        opt_max_recv_byte=opt_max_recv_byte,
        opt_max_recv_pkt=opt_max_recv_pkt,
        opt_max_burst_rate_byte=opt_max_burst_rate_byte,
        opt_max_burst_rate_pkt=opt_max_burst_rate_pkt,
        opt_valid_dest=opt_valid_dest,
        opt_src_ip_sproof=opt_src_ip_sproof)

    if csr is None:
        print("CSR signing failed; state is not updated")
        return

    with open(path, "w") as fp:
        fp.write(csr.public_bytes(Encoding.PEM).decode())

    print("\nSigned certificate signing request PEM:")
    print(csr.public_bytes(Encoding.PEM).decode(), end="")
    print("CSR signing succeeded")
    return csr

def _prep_data_tup_csr_limit_dict(
        name, csr_limit_dict,
        cmdline_data, cmdline_data_req, csr_data_parse=lambda x:x):
    # modifies csr_limit_dict content
    entry = csr_limit_dict.pop(name, None)
    if entry is None:
        return _prep_data_tup_limit(
            None, cmdline_data, False, cmdline_data_req)
    return _prep_data_tup_limit(
        csr_data_parse(entry[1]), cmdline_data, entry[0], cmdline_data_req)

def _safe_parse_str_2_dict(s, parser, except_str):
    s_dict = {}
    if s is not None:
        s_dict, errstr = parser(s)
        if s_dict is None:
            raise ValueError(except_str.format(errstr))
    return s_dict

def _sign_cert(
        ppksman, csr, cert_type,
        signer_privkey,
        signer_privkey_name,
        signee_pubkey,
        signee_pubkey_name,
        start_time, end_time,
        del_type, cert_desp,
        pathlen, filter_digests,
        monitor_digests,
        max_num_priority,
        max_socket_count,
        max_exp_period,
        max_send_byte, max_send_pkt,
        max_recv_byte, max_recv_pkt,
        max_burst_rate_byte,
        max_burst_rate_pkt,
        valid_dest,
        src_ip_sproof,
        aux_info_str, aux_limit_str,
        opt_filter_digests,
        opt_monitor_digests,
        opt_max_num_priority, opt_max_socket_count,
        opt_max_exp_period,
        opt_max_send_byte, opt_max_send_pkt,
        opt_max_recv_byte, opt_max_recv_pkt,
        opt_max_burst_rate_byte, opt_max_burst_rate_pkt,
        opt_valid_dest, opt_src_ip_sproof, path, ask):

    if csr is not None:
        # Extract information from CSR
        # Note that if also provided via commandline, the commandline info is always preferred
        csr_exts = csr.extensions

        csr_info_str = safe_decode(
            pktlab_ext_get_bytes(
                try_get_extension(
                    pconst.PKTLAB_EXT_PKTLAB_CERT_INFO,
                    csr_exts)))
        csr_limit_str = safe_decode(
            pktlab_ext_get_bytes(
                try_get_extension(
                    pconst.PKTLAB_EXT_PKTLAB_CERT_LIMIT,
                    csr_exts)))

        csr_info_dict = _safe_parse_str_2_dict(
            csr_info_str, parse_info,
            "Bad CSR certificate information field: {}")

        csr_limit_dict = _safe_parse_str_2_dict(
            csr_limit_str, parse_limit,
            "Bad CSR certificate limitation field: {}")

        csr_cert_type = csr_info_dict.pop(
            pconst.PKTLAB_CERT_INFO_CERT_TYPE, None)
        if csr_cert_type is not None and \
           cert_type is not None and \
           csr_cert_type != cert_type:
            warn(
                "CSR certificate type ({}) does not match supplied certificate type ({})".format(
                csr_cert_type, cert_type))

        cert_type_tup       = _prep_data_tup(csr_cert_type, cert_type)
        signer_privkey_tup  = (signer_privkey, 2, signer_privkey_name)
        signee_pubkey_tup   = _prep_data_tup_key(
            csr.public_key(), signee_pubkey, signee_pubkey_name)
        start_time_tup      = (start_time, 2)
        end_time_tup        = (end_time, 2)
        bc                  = try_get_extension(
            ExtensionOID.BASIC_CONSTRAINTS.dotted_string, csr_exts)
        pathlen_tup         = _prep_data_tup(
            bc.value.path_length if bc is not None else None, pathlen)

        #
        # info fields
        #

        del_type_tup        = _prep_data_tup(
            csr_info_dict.pop(
                pconst.PKTLAB_CERT_INFO_DEL_TYPE, None), del_type)
        cert_desp_tup       = _prep_data_tup(
            csr_info_dict.pop(
                pconst.PKTLAB_CERT_INFO_CERT_DESC, None), cert_desp)

        # remaining unrecognized nv pairs
        aux_info_dict = _safe_parse_str_2_dict(
            aux_info_str, parse_aux_info,
            "Bad auxiliary information: {}")

        # for nv pair that appeared in aux info
        cmdline_aux_info_ls = []
        for i in aux_info_dict:
            # ignore same nv pair in csr info
            csr_info_dict.pop(i, None)
            cmdline_aux_info_ls.append(
                get_nvp_str(i, aux_info_dict[i]))
        cmdline_aux_info_str_tup = _prep_data_tup(
            None, None if len(cmdline_aux_info_ls) == 0 \
                       else "".join(cmdline_aux_info_ls))

        # for nv pair that only appeared in CSR info
        csr_aux_info_ls = []
        for i in csr_info_dict:
            csr_aux_info_ls.append(
                get_nvp_str(i, csr_info_dict[i]))
        csr_aux_info_str_tup = _prep_data_tup(
            None if len(csr_aux_info_ls) == 0 \
                 else "".join(csr_aux_info_ls), None)

        #
        # limit fields
        #

        filter_digests_tup       = \
            _prep_data_tup_csr_limit_dict(
                pconst.PKTLAB_CERT_LIMIT_FILT_DIGEST, csr_limit_dict,
                filter_digests, opt_filter_digests, safe_parse_digests)
        monitor_digests_tup = \
            _prep_data_tup_csr_limit_dict(
                pconst.PKTLAB_CERT_LIMIT_MON_DIGEST, csr_limit_dict,
                monitor_digests, opt_monitor_digests, safe_parse_digests)
        max_num_priority_tup     = _prep_data_tup_csr_limit_dict(
            pconst.PKTLAB_CERT_LIMIT_MAX_NUM_PRIORITY, csr_limit_dict,
            max_num_priority, opt_max_num_priority)
        max_socket_count_tup     = _prep_data_tup_csr_limit_dict(
            pconst.PKTLAB_CERT_LIMIT_MAX_SOCKET_COUNT, csr_limit_dict,
            max_socket_count, opt_max_socket_count)
        max_exp_period_tup       = _prep_data_tup_csr_limit_dict(
            pconst.PKTLAB_CERT_LIMIT_MAX_EXP_PERIOD, csr_limit_dict,
            max_exp_period, opt_max_exp_period)
        max_send_byte_tup        = _prep_data_tup_csr_limit_dict(
            pconst.PKTLAB_CERT_LIMIT_MAX_SEND_BYTE, csr_limit_dict,
            max_send_byte, opt_max_send_byte)
        max_send_pkt_tup         = _prep_data_tup_csr_limit_dict(
            pconst.PKTLAB_CERT_LIMIT_MAX_SEND_PKT, csr_limit_dict,
            max_send_pkt, opt_max_send_pkt)
        max_recv_byte_tup        = _prep_data_tup_csr_limit_dict(
            pconst.PKTLAB_CERT_LIMIT_MAX_RECV_BYTE, csr_limit_dict,
            max_recv_byte, opt_max_recv_byte)
        max_recv_pkt_tup         = _prep_data_tup_csr_limit_dict(
            pconst.PKTLAB_CERT_LIMIT_MAX_RECV_PKT, csr_limit_dict,
            max_recv_pkt, opt_max_recv_pkt)
        max_burst_rate_byte_tup  = _prep_data_tup_csr_limit_dict(
            pconst.PKTLAB_CERT_LIMIT_MAX_BURST_RATE_BYTE, csr_limit_dict,
            max_burst_rate_byte, opt_max_burst_rate_byte, lambda x:x.split(sep=","))
        max_burst_rate_pkt_tup   = _prep_data_tup_csr_limit_dict(
            pconst.PKTLAB_CERT_LIMIT_MAX_BURST_RATE_PKT, csr_limit_dict,
            max_burst_rate_pkt, opt_max_burst_rate_pkt, lambda x:x.split(sep=","))
        valid_dest_tup           = _prep_data_tup_csr_limit_dict(
            pconst.PKTLAB_CERT_LIMIT_VALID_DEST, csr_limit_dict,
            valid_dest, opt_valid_dest, lambda x:x.split(sep=","))
        src_ip_sproof_tup        = _prep_data_tup_csr_limit_dict(
            pconst.PKTLAB_CERT_LIMIT_SRC_IP_SPROOF, csr_limit_dict,
            src_ip_sproof, opt_src_ip_sproof)

        # remaining unrecognized nv pairs
        aux_limit_dict = _safe_parse_str_2_dict(
            aux_limit_str, parse_aux_limit,
            "Bad auxiliary limitation: {}")

        # for nv pair that appeared in aux limit
        cmdline_aux_limit_ls = []
        for i in aux_limit_dict:
            # ignore same nv pair in csr limit
            csr_limit_dict.pop(i, None)
            cmdline_aux_limit_ls.append(
                get_nvp_str_opt(
                    i, aux_limit_dict[i][1], aux_limit_dict[i][0]))

            # warn about unknown nv pair
            if aux_limit_dict[i][2]:
                warn("Unrecognized optional name-value pair in auxiliary limit field string"
                    " (name:{},value:{})".format(i,aux_limit_dict[i][1]))

        cmdline_aux_limit_str_tup = _prep_data_tup(
            None, None if len(cmdline_aux_limit_ls) == 0 \
                       else "".join(cmdline_aux_limit_ls))

        # for nv pair that only appeared in CSR limit
        csr_aux_limit_ls = []
        for i in csr_limit_dict:
            csr_aux_limit_ls.append(
                get_nvp_str_opt(i, csr_limit_dict[i][1], csr_limit_dict[i][0]))

            # warn about unknown nv pair
            if csr_limit_dict[i][2]:
                warn("Unrecognized optional name-value pair in CSR limit field string"
                    " (name:{},value:{})".format(i,csr_limit_dict[i][1]))

        csr_aux_limit_str_tup = _prep_data_tup(
            None if len(csr_aux_limit_ls) == 0 \
                 else "".join(csr_aux_limit_ls), None)

    else:
        cert_type_tup             = (cert_type, 2)
        signer_privkey_tup        = (signer_privkey, 2, signer_privkey_name)
        signee_pubkey_tup         = (signee_pubkey, 2, signee_pubkey_name)
        start_time_tup            = (start_time, 2)
        end_time_tup              = (end_time, 2)
        pathlen_tup               = _prep_data_tup(None, pathlen)
        del_type_tup              = _prep_data_tup(None, del_type)
        cert_desp_tup             = _prep_data_tup(None, cert_desp)

        filter_digests_tup        = _prep_data_tup_limit(
            None, filter_digests, False, opt_filter_digests)
        monitor_digests_tup  = _prep_data_tup_limit(
            None, monitor_digests, False, opt_monitor_digests)
        max_num_priority_tup      = _prep_data_tup_limit(
            None, max_num_priority, False, opt_max_num_priority)
        max_socket_count_tup      = _prep_data_tup_limit(
            None, max_socket_count, False, opt_max_socket_count)
        max_exp_period_tup        = _prep_data_tup_limit(
            None, max_exp_period, False, opt_max_exp_period)
        max_send_byte_tup         = _prep_data_tup_limit(
            None, max_send_byte, False, opt_max_send_byte)
        max_send_pkt_tup          = _prep_data_tup_limit(
            None, max_send_pkt, False, opt_max_send_pkt)
        max_recv_byte_tup         = _prep_data_tup_limit(
            None, max_recv_byte, False, opt_max_recv_byte)
        max_recv_pkt_tup          = _prep_data_tup_limit(
            None, max_recv_pkt, False, opt_max_recv_pkt)
        max_burst_rate_byte_tup   = _prep_data_tup_limit(
            None, max_burst_rate_byte, False, opt_max_burst_rate_byte)
        max_burst_rate_pkt_tup    = _prep_data_tup_limit(
            None, max_burst_rate_pkt, False, opt_max_burst_rate_pkt)
        valid_dest_tup            = _prep_data_tup_limit(
            None, valid_dest, False, opt_valid_dest)
        src_ip_sproof_tup         = _prep_data_tup_limit(
            None, src_ip_sproof, False, opt_src_ip_sproof)
        csr_aux_info_str_tup      = (None, 0)
        cmdline_aux_info_str_tup  = _prep_data_tup(None, aux_info_str)
        csr_aux_limit_str_tup     = (None, 0)
        cmdline_aux_limit_str_tup = _prep_data_tup(None, aux_limit_str)

        _warn_unknown_aux_limit_str(aux_limit_str)

    if not _prompt_input_info(
            cert_type_tup=cert_type_tup,
            signer_privkey_tup=signer_privkey_tup,
            signee_pubkey_tup=signee_pubkey_tup,
            signee_privkey_tup=(None, 0, ""),
            start_time_tup=start_time_tup,
            end_time_tup=end_time_tup,
            pathlen_tup=pathlen_tup,
            del_type_tup=del_type_tup,
            cert_desp_tup=cert_desp_tup,
            filter_digests_tup=filter_digests_tup,
            monitor_digests_tup=monitor_digests_tup,
            max_num_priority_tup=max_num_priority_tup,
            max_socket_count_tup=max_socket_count_tup,
            max_exp_period_tup=max_exp_period_tup,
            max_send_byte_tup=max_send_byte_tup,
            max_send_pkt_tup=max_send_pkt_tup,
            max_recv_byte_tup=max_recv_byte_tup,
            max_recv_pkt_tup=max_recv_pkt_tup,
            max_burst_rate_byte_tup=max_burst_rate_byte_tup,
            max_burst_rate_pkt_tup=max_burst_rate_pkt_tup,
            valid_dest_tup=valid_dest_tup,
            src_ip_sproof_tup=src_ip_sproof_tup,
            csr_aux_info_str_tup=csr_aux_info_str_tup,
            cmdline_aux_info_str_tup=cmdline_aux_info_str_tup,
            csr_aux_limit_str_tup=csr_aux_limit_str_tup,
            cmdline_aux_limit_str_tup=cmdline_aux_limit_str_tup,
            signrst="certificate", ask=ask):
        print("Command aborted")
        return

    cert = ppksman.gen_cert(
        name=os.path.basename(path),
        cert_type=cert_type_tup[0],
        signer_privkey=signer_privkey_tup[0],
        signee_pubkey=signee_pubkey_tup[0],
        start_time=start_time_tup[0],
        end_time=end_time_tup[0],
        pathlen=pathlen_tup[0],
        del_type=del_type_tup[0],
        cert_desp=cert_desp_tup[0],
        filter_digests=safe_concat(filter_digests_tup[0]),
        monitor_digests=safe_concat(monitor_digests_tup[0]),
        max_num_priority=max_num_priority_tup[0],
        max_socket_count=max_socket_count_tup[0],
        max_exp_period=max_exp_period_tup[0],
        max_send_byte=max_send_byte_tup[0],
        max_send_pkt=max_send_pkt_tup[0],
        max_recv_byte=max_recv_byte_tup[0],
        max_recv_pkt=max_recv_pkt_tup[0],
        max_burst_rate_byte=safe_concat(max_burst_rate_byte_tup[0], ","),
        max_burst_rate_pkt=safe_concat(max_burst_rate_pkt_tup[0], ","),
        valid_dest=safe_concat(valid_dest_tup[0], ","),
        src_ip_sproof=src_ip_sproof_tup[0],
        aux_info_str=safe_combine_str(
            csr_aux_info_str_tup[0],cmdline_aux_info_str_tup[0]),
        aux_limit_str=safe_combine_str(
            csr_aux_limit_str_tup[0],cmdline_aux_limit_str_tup[0]),
        opt_filter_digests=filter_digests_tup[2],
        opt_monitor_digests=monitor_digests_tup[2],
        opt_max_num_priority=max_num_priority_tup[2],
        opt_max_socket_count=max_socket_count_tup[2],
        opt_max_exp_period=max_exp_period_tup[2],
        opt_max_send_byte=max_send_byte_tup[2],
        opt_max_send_pkt=max_send_pkt_tup[2],
        opt_max_recv_byte=max_recv_byte_tup[2],
        opt_max_recv_pkt=max_recv_pkt_tup[2],
        opt_max_burst_rate_byte=max_burst_rate_byte_tup[2],
        opt_max_burst_rate_pkt=max_burst_rate_pkt_tup[2],
        opt_valid_dest=valid_dest_tup[2],
        opt_src_ip_sproof=src_ip_sproof_tup[2])

    if cert is None:
        print("Certificate signing failed; state is not updated")
        return

    with open(path, "w") as fp:
        fp.write(cert.public_bytes(Encoding.PEM).decode())

    print("\nSigned certificate PEM:")
    print(cert.public_bytes(Encoding.PEM).decode(), end="")
    print("Certificate signing succeeded")
    return cert

def _update_argparse_gen_key(subparsers_gen):
    parser_gen_key = subparsers_gen.add_parser(
        "Key", aliases=["key", "k"],
        help="PPKS Manager generate key subcommand")
    parser_gen_key.add_argument(
        "keyname", type=str,
        help="Name for generated Ed25519 key (used in key lists)")
    parser_gen_key.add_argument(
        "-f", "--file", type=str,
        help="Alternative path to store the generated key")
    return

def _update_argparse_gen_csr(subparsers_gen):
    parser_gen_csr = subparsers_gen.add_parser(
        "CertificateSigningRequest", aliases=["CSR", "csr"],
        help="PPKS Manager generate certificate signing request subcommand")
    parser_gen_csr.add_argument(
        "cert_type",
        choices= [
            pconst.PKTLAB_CERT_TYPE_STR_SUBCMD,
            pconst.PKTLAB_CERT_TYPE_STR_PUBCMD,
            pconst.PKTLAB_CERT_TYPE_STR_EXPPRIV,
            pconst.PKTLAB_CERT_TYPE_STR_AGENT,
            pconst.PKTLAB_CERT_TYPE_STR_DELPRIV],
        help="Certificate signing request type to generate")
    parser_gen_csr.add_argument(
        "signee_privkey", type=str,
        help="Index of or path to private key to generate certificate signing request")
    parser_gen_csr.add_argument(
        "file", type=str,
        help="Path to store generated certificate signing request")
    parser_gen_csr.add_argument(
        "--pathlen", type=int,
        help="Pathlen in basic constraint extension of certificate signing request")

    # info field
    parser_gen_csr.add_argument(
        "--del_exppriv", action="store_true",
        help="Specify delegate experiment privilege in certificate signing request")
    parser_gen_csr.add_argument(
        "--del_reppriv", action="store_true",
        help="Specify delegate represent privilege in certificate signing request")
    parser_gen_csr.add_argument(
        "-c", "--cert_description", type=str,
        help="Certificate description to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "--aux_info_str", type=str,
        help="Auxiliary info string to be included in certificate signing request")

    # limit field
    parser_gen_csr.add_argument(
        "--filter_digest", nargs='+', type=str,
        help="List of SHA256 hash (in hex) of filter programs to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "--monitor_digest", nargs='+', type=str,
        help="List of SHA256 hash (in hex) of monitor programs "
             "to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "--max_num_priority", type=int,
        help="Maximum priority number to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "--max_socket_count", type=int,
        help="Maximum socket count can connect to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "--max_exp_period", type=int,
        help="Maximum experiment period (in pktlab ticks) to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "--max_send_byte", type=int,
        help="Maximum send byte count to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "--max_send_pkt", type=int,
        help="Maximum send packet count to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "--max_recv_byte", type=int,
        help="Maximum receive byte count to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "--max_recv_pkt", type=int,
        help="Maximum receive packet count to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "--max_burst_rate_byte", nargs='+', type=str,
        help="List of maximum burst rate in 'BYTES/TICKS' to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "--max_burst_rate_pkt", nargs='+', type=str,
        help="List of maximum burst rate in 'PKTS/TICKS' to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "--valid_dest", nargs='+', type=str,
        help="List of valid destinations (in subnet notation; e.g. '127.0.0.0/24') "
             "to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "--src_ip_sproof", type=int,
        help="Source IP sproof to be included in certificate signing request")
    parser_gen_csr.add_argument(
        "--aux_limit_str", type=str,
        help="Auxiliary limit string to be included in certificate signing request")

    # limit field set require
    parser_gen_csr.add_argument(
        "--opt_filter_digests", action="store_true",
        help="Mark filter program digests name value pair"
             " to be optional in certificate signing request")
    parser_gen_csr.add_argument(
        "--opt_monitor_digests", action="store_true",
        help="Mark monitor program digests name value pair"
             " to be optional in certificate signing request")
    parser_gen_csr.add_argument(
        "--opt_max_num_priority", action="store_true",
        help="Mark maximum priority number name value pair "
             "to be optional in certificate signing request")
    parser_gen_csr.add_argument(
        "--opt_max_socket_count", action="store_true",
        help="Mark maximum socket count name value pair "
             "to be optional in certificate signing request")
    parser_gen_csr.add_argument(
        "--opt_max_exp_period", action="store_true",
        help="Mark maximum experiment period name value pair "
             "to be optional in certificate signing request")
    parser_gen_csr.add_argument(
        "--opt_max_send_byte", action="store_true",
        help="Mark maximum send byte count name value pair "
             "to be optional in certificate signing request")
    parser_gen_csr.add_argument(
        "--opt_max_send_pkt", action="store_true",
        help="Mark maximum send packet count name value pair "
             "to be optional in certificate signing request")
    parser_gen_csr.add_argument(
        "--opt_max_recv_byte", action="store_true",
        help="Mark maximum receive byte count name value pair "
             "to be optional in certificate signing request")
    parser_gen_csr.add_argument(
        "--opt_max_recv_pkt", action="store_true",
        help="Mark maximum receive packet count name value pair "
             "to be optional in certificate signing request")
    parser_gen_csr.add_argument(
        "--opt_max_burst_rate_byte", action="store_true",
        help="Mark maximum byte burst rate name value pair "
             "to be optional in certificate signing request")
    parser_gen_csr.add_argument(
        "--opt_max_burst_rate_pkt", action="store_true",
        help="Mark maximum packet burst rate name value pair "
             "to be optional in certificate signing request")
    parser_gen_csr.add_argument(
        "--opt_valid_dest", action="store_true",
        help="Mark maximum valid destination name value pair "
             "to be optional in certificate signing request")
    parser_gen_csr.add_argument(
        "--opt_src_ip_sproof", action="store_true",
        help="Mark source IP sproof name value pair "
             "to be optional in certificate signing request")

    # misc options
    parser_gen_csr.add_argument(
        "-y", "--yes", action='store_true',
        help="Automatic yes to prompts")
    return

def _update_argparse_gen_cert(subparsers_gen):
    parser_gen_cert = subparsers_gen.add_parser(
        "Certificate", aliases=["certificate", "cert"],
        help="PPKS Manager generate certificate subcommand")
    parser_gen_cert.add_argument(
        "cert_type",
        choices= [
            pconst.PKTLAB_CERT_TYPE_STR_SUBCMD,
            pconst.PKTLAB_CERT_TYPE_STR_PUBCMD,
            pconst.PKTLAB_CERT_TYPE_STR_EXPPRIV,
            pconst.PKTLAB_CERT_TYPE_STR_DELPRIV,
            pconst.PKTLAB_CERT_TYPE_STR_AGENT],
        help="Certificate type to sign")
    parser_gen_cert.add_argument(
        "signer_privkey", type=str,
        help="Index of or path to signer private key to sign certificate")
    parser_gen_cert.add_argument(
        "start_time", type=int,
        help="Validity period notBefore in signed certificate")
    parser_gen_cert.add_argument(
        "end_time", type=int,
        help="Validity period notAfter in signed certificate")
    parser_gen_cert.add_argument(
        "file", type=str,
        help="Path to store signed certificate")
    parser_gen_cert.add_argument(
        "-k", "--signee_pubkey", type=str,
        help="Index of or path to signee public key to be included in certificate")
    parser_gen_cert.add_argument(
        "--pathlen", type=int,
        help="Pathlen in basic constraint extension of certificate")
    parser_gen_cert.add_argument(
        "-r", "--csr_path", type=str,
        help="Path to CSR for signing certifcate")

    # info field
    parser_gen_cert.add_argument(
        "--del_exppriv", action="store_true",
        help="Specify delegate experiment privilege in certificate")
    parser_gen_cert.add_argument(
        "--del_reppriv", action="store_true",
        help="Specify delegate represent privilege in certificate")
    parser_gen_cert.add_argument(
        "-c", "--cert_description", type=str,
        help="Certificate description to be included in certificate")
    parser_gen_cert.add_argument(
        "--aux_info_str", type=str,
        help="Auxiliary info string to be included in certificate")

    # limit field
    parser_gen_cert.add_argument(
        "--filter_digest", nargs='+', type=str,
        help="List of SHA256 hash (in hex) of filter programs to be included in certificate")
    parser_gen_cert.add_argument(
        "--monitor_digest", nargs='+', type=str,
        help="List of SHA256 hash (in hex) of monitor programs "
             "to be included in certificate")
    parser_gen_cert.add_argument(
        "--max_num_priority", type=int,
        help="Maximum priority number to be included in certificate")
    parser_gen_cert.add_argument(
        "--max_socket_count", type=int,
        help="Maximum socket count can connect to be included in certificate")
    parser_gen_cert.add_argument(
        "--max_exp_period", type=int,
        help="Maximum experiment period (in pktlab ticks) to be included in certificate")
    parser_gen_cert.add_argument(
        "--max_send_byte", type=int,
        help="Maximum send byte count to be included in certificate")
    parser_gen_cert.add_argument(
        "--max_send_pkt", type=int,
        help="Maximum send packet count to be included in certificate")
    parser_gen_cert.add_argument(
        "--max_recv_byte", type=int,
        help="Maximum receive byte count to be included in certificate")
    parser_gen_cert.add_argument(
        "--max_recv_pkt", type=int,
        help="Maximum receive packet count to be included in certificate")
    parser_gen_cert.add_argument(
        "--max_burst_rate_byte", nargs='+', type=str,
        help="List of maximum burst rate in 'BYTES/TICKS' to be included in certificate")
    parser_gen_cert.add_argument(
        "--max_burst_rate_pkt", nargs='+', type=str,
        help="List of maximum burst rate in 'PKTS/TICKS' to be included in certificate")
    parser_gen_cert.add_argument(
        "--valid_dest", nargs='+', type=str,
        help="List of valid destinations (in subnet notation; e.g. '127.0.0.0/24') "
             "to be included in certificate")
    parser_gen_cert.add_argument(
        "--src_ip_sproof", type=int,
        help="Whether enabling source IP sproof to be included in certificate")
    parser_gen_cert.add_argument(
        "--aux_limit_str", type=str,
        help="Auxiliary limit string to be included in certificate")

    # limit field set optional
    parser_gen_cert.add_argument(
        "--opt_filter_digests", action="store_true",
        help="Mark filter program digests name value pair"
             " to be optional in certificate")
    parser_gen_cert.add_argument(
        "--opt_monitor_digests", action="store_true",
        help="Mark monitor program digests name value pair"
             " to be optional in certificate")
    parser_gen_cert.add_argument(
        "--opt_max_num_priority", action="store_true",
        help="Mark maximum priority number name value pair "
             "to be optional in certificate")
    parser_gen_cert.add_argument(
        "--opt_max_socket_count", action="store_true",
        help="Mark maximum socket count name value pair "
             "to be optional in certificate")
    parser_gen_cert.add_argument(
        "--opt_max_exp_period", action="store_true",
        help="Mark maximum experiment period name value pair "
             "to be optional in certificate")
    parser_gen_cert.add_argument(
        "--opt_max_send_byte", action="store_true",
        help="Mark maximum send byte count name value pair "
             "to be optional in certificate")
    parser_gen_cert.add_argument(
        "--opt_max_send_pkt", action="store_true",
        help="Mark maximum send packet count name value pair "
             "to be optional in certificate")
    parser_gen_cert.add_argument(
        "--opt_max_recv_byte", action="store_true",
        help="Mark maximum receive byte count name value pair "
             "to be optional in certificate")
    parser_gen_cert.add_argument(
        "--opt_max_recv_pkt", action="store_true",
        help="Mark maximum receive packet count name value pair "
             "to be optional in certificate")
    parser_gen_cert.add_argument(
        "--opt_max_burst_rate_byte", action="store_true",
        help="Mark maximum byte burst rate name value pair "
             "to be optional in certificate")
    parser_gen_cert.add_argument(
        "--opt_max_burst_rate_pkt", action="store_true",
        help="Mark maximum packet burst rate name value pair "
             "to be optional in certificate")
    parser_gen_cert.add_argument(
        "--opt_valid_dest", action="store_true",
        help="Mark maximum valid destination name value pair "
             "to be optional in certificate")
    parser_gen_cert.add_argument(
        "--opt_src_ip_sproof", action="store_true",
        help="Mark source IP sproof name value pair "
             "to be optional in certificate")

    # misc options
    parser_gen_cert.add_argument(
        "-y", "--yes", action='store_true',
        help="Automatic yes to prompts")
    return

#
# EXPORTED FUNCTIONS
#

def is_gen_subcmd(PPKSMan_subcommand):
    subcmd_set = {"generate", "gen", "g"}
    if PPKSMan_subcommand.lower() in subcmd_set:
        return True
    return False

def update_argparse_gen(subparsers_ppksman):
    parser_gen = subparsers_ppksman.add_parser(
        "Generate", aliases=["generate", "gen", "g"],
        help="PPKS Manager generate subcommand")
    subparsers_gen = parser_gen.add_subparsers(required=True, dest="PPKSMan_gen_subcommand")

    _update_argparse_gen_key(subparsers_gen)
    _update_argparse_gen_csr(subparsers_gen)
    _update_argparse_gen_cert(subparsers_gen)
    return

def subcmd_gen(ppksman, args):
    """
    Main gen command
    """

    if args.PPKSMan_gen_subcommand.lower() in KEY_SUBCMD_SET:
        _genkey(ppksman, args.keyname, args.file)
    elif args.PPKSMan_gen_subcommand.lower() in CSR_SUBCMD_SET:
        print("Loading signee privkey")

        if is_index(args.signee_privkey):
            _, signee_privkey = load_key_ppksman(ppksman, int(args.signee_privkey))
            signee_privkey_name = "from key list index {}".format(args.signee_privkey)
        else:
            _, signee_privkey = load_key_file(args.signee_privkey)
            signee_privkey_name = "from file {}".format(args.signee_privkey)

        if signee_privkey is None:
            raise RuntimeError(
                "Cannot load signee privkey "+
                "(note specified key should only be in privkey list)")

        csr = _sign_csr(
            ppksman=ppksman,
            cert_type=args.cert_type,
            signee_privkey=signee_privkey,
            signee_privkey_name=signee_privkey_name,
            pathlen=args.pathlen,
            del_type=comp_del_type(
                args.del_exppriv, args.del_reppriv),
            cert_desp=args.cert_description,
            filter_digests=args.filter_digest,
            monitor_digests=args.monitor_digest,
            max_num_priority=args.max_num_priority,
            max_socket_count=args.max_socket_count,
            max_exp_period=args.max_exp_period,
            max_send_byte=args.max_send_byte,
            max_send_pkt=args.max_send_pkt,
            max_recv_byte=args.max_recv_byte,
            max_recv_pkt=args.max_recv_pkt,
            max_burst_rate_byte=args.max_burst_rate_byte,
            max_burst_rate_pkt=args.max_burst_rate_pkt,
            valid_dest=args.valid_dest,
            src_ip_sproof=args.src_ip_sproof,
            aux_info_str=args.aux_info_str,
            aux_limit_str=args.aux_limit_str,
            opt_filter_digests=args.opt_filter_digests,
            opt_monitor_digests=args.opt_monitor_digests,
            opt_max_num_priority=args.opt_max_num_priority,
            opt_max_socket_count=args.opt_max_socket_count,
            opt_max_exp_period=args.opt_max_exp_period,
            opt_max_send_byte=args.opt_max_send_byte,
            opt_max_send_pkt=args.opt_max_send_pkt,
            opt_max_recv_byte=args.opt_max_recv_byte,
            opt_max_recv_pkt=args.opt_max_recv_pkt,
            opt_max_burst_rate_byte=args.opt_max_burst_rate_byte,
            opt_max_burst_rate_pkt=args.opt_max_burst_rate_pkt,
            opt_valid_dest=args.opt_valid_dest,
            opt_src_ip_sproof=args.opt_src_ip_sproof,
            path=args.file, ask=not args.yes)
    elif args.PPKSMan_gen_subcommand.lower() in CERT_SUBCMD_SET:
        csr = None
        if args.csr_path is not None:
            csr = load_csr_file(args.csr_path)
            if not csr.is_signature_valid:
                raise RuntimeError("INVALID certificate signing request signature")

        print("Loading signer privkey")
        if is_index(args.signer_privkey):
            _, signer_privkey = load_key_ppksman(ppksman, int(args.signer_privkey))
            signer_privkey_name = "from key list index {}".format(args.signer_privkey)
        else:
            _, signer_privkey = load_key_file(args.signer_privkey)
            signer_privkey_name = "from file {}".format(args.signer_privkey)

        if signer_privkey is None:
            raise RuntimeError("Cannot load signer privkey")

        # signee pubkey can be supplied either from CSR or list/file
        if args.signee_pubkey is not None:
            print("Loading signee pubkey")

            if is_index(args.signee_pubkey):
                signee_pubkey, _ = load_key_ppksman(ppksman, int(args.signee_pubkey))
                signee_pubkey_name = "from key list index {}".format(args.signee_pubkey)
            else:
                signee_pubkey, _ = load_key_file(args.signee_pubkey)
                signee_pubkey_name = "from file {}".format(args.signee_pubkey)

            if signee_pubkey is None:
                raise RuntimeError("Cannot load signee pubkey")
        else:
            if args.csr_path is None:
                raise ValueError("Either CSR or signee pubkey must be supplied")

            signee_pubkey = None
            signee_pubkey_name = None

        cert = _sign_cert(
            ppksman=ppksman,
            csr=csr,
            cert_type=args.cert_type,
            signer_privkey=signer_privkey,
            signer_privkey_name=signer_privkey_name,
            signee_pubkey=signee_pubkey,
            signee_pubkey_name=signee_pubkey_name,
            start_time=args.start_time,
            end_time=args.end_time,
            pathlen=args.pathlen,
            del_type=comp_del_type(
                args.del_exppriv, args.del_reppriv),
            cert_desp=args.cert_description,
            filter_digests=args.filter_digest,
            monitor_digests=args.monitor_digest,
            max_num_priority=args.max_num_priority,
            max_socket_count=args.max_socket_count,
            max_exp_period=args.max_exp_period,
            max_send_byte=args.max_send_byte,
            max_send_pkt=args.max_send_pkt,
            max_recv_byte=args.max_recv_byte,
            max_recv_pkt=args.max_recv_pkt,
            max_burst_rate_byte=args.max_burst_rate_byte,
            max_burst_rate_pkt=args.max_burst_rate_pkt,
            valid_dest=args.valid_dest,
            src_ip_sproof=args.src_ip_sproof,
            aux_info_str=args.aux_info_str,
            aux_limit_str=args.aux_limit_str,
            opt_filter_digests=args.opt_filter_digests,
            opt_monitor_digests=args.opt_monitor_digests,
            opt_max_num_priority=args.opt_max_num_priority,
            opt_max_socket_count=args.opt_max_socket_count,
            opt_max_exp_period=args.opt_max_exp_period,
            opt_max_send_byte=args.opt_max_send_byte,
            opt_max_send_pkt=args.opt_max_send_pkt,
            opt_max_recv_byte=args.opt_max_recv_byte,
            opt_max_recv_pkt=args.opt_max_recv_pkt,
            opt_max_burst_rate_byte=args.opt_max_burst_rate_byte,
            opt_max_burst_rate_pkt=args.opt_max_burst_rate_pkt,
            opt_valid_dest=args.opt_valid_dest,
            opt_src_ip_sproof=args.opt_src_ip_sproof,
            path=args.file, ask=not args.yes)
    else:
        raise ValueError(
            "Unknown gen subcommand: {}".format(
                args.PPKSMan_gen_subcommand))
    return