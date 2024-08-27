from __future__ import annotations

import secrets
import string


def rand_string(length: int) -> str | None:
    """Generates a random string of given length.

       Text format is based on Internet Small Computer System Interface (iSCSI) Protocol
       (RFC 7143) Section 6.1

    Args:
        length: length of the ramdom string

    Returns:
        None: if length is not integer
        string: a random string

    """
    if not isinstance(length, int):
        return None

    alphabet = string.ascii_letters + string.digits + '.-+@_=:/[],~'  # rfc7143#section-6.1
    # Allowed in targetcli:
    # https://github.com/open-iscsi/configshell-fb/blob/b4923ee5591d8b980003150e0ba6ffe512d8c9da/configshell/shell.py#L116
    generated_string = ''.join(secrets.choice(alphabet) for _ in range(length))

    return str(generated_string)
