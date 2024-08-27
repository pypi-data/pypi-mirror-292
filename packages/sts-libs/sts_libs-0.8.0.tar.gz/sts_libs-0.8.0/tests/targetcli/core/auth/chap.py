from __future__ import annotations

import os
from random import randint
from typing import TYPE_CHECKING

from sts.utils.string_extras import rand_string

if TYPE_CHECKING:
    from collections.abc import Generator

import pytest

from sts import iscsi, lio

TARGET_IQN = os.getenv('TARGET_IQN', default='iqn.2003-01.com.redhat:targetauthtest')
INITIATOR_IQN = os.getenv('INITIATOR_IQN', default='iqn.2003-01.com.redhat:initiatorauthtest')

# note: password for target and initiator should be different, or else auth error will occur
CHAP_USERNAME = os.getenv('DISC_CHAP_USERNAME', default='redhat')
CHAP_PASSWORD = os.getenv('DISC_CHAP_PASSWORD', default='redhat_password')
CHAP_TARGET_USERNAME = os.getenv('DISC_CHAP_TARGET_USERNAME', default='mutual_redhat')
CHAP_TARGET_PASSWORD = os.getenv('DISC_CHAP_TARGET_PASSWORD', default='mutual_redhat_password')

# Arguments for tpg authentication test
argument_tpg = [
    {  # Configures 1-way CHAP for iSCSI tests
        't_iqn': TARGET_IQN,
        'i_iqn': INITIATOR_IQN,
        'chap_username': CHAP_USERNAME,
        'chap_password': CHAP_PASSWORD,
        'chap_target_username': '',
        'chap_target_password': '',
        'tpg_or_acl': 'tpg',
    },
    {  # Configures 2-way CHAP for iSCSI tests
        't_iqn': TARGET_IQN,
        'i_iqn': INITIATOR_IQN,
        'chap_username': CHAP_USERNAME,
        'chap_password': CHAP_PASSWORD,
        'chap_target_username': CHAP_TARGET_USERNAME,
        'chap_target_password': CHAP_TARGET_PASSWORD,
        'tpg_or_acl': 'tpg',
    },
    {  # Configures 2-way CHAP for iSCSI tests with a single character as userid and password
        't_iqn': TARGET_IQN,
        'i_iqn': INITIATOR_IQN,
        'chap_username': 'a',
        'chap_password': '0',
        'chap_target_username': 'A',
        'chap_target_password': '1',
        'tpg_or_acl': 'tpg',
    },
    {  # Configures 2-way CHAP for iSCSI tests with 254 characters as userid and password
        't_iqn': TARGET_IQN,
        'i_iqn': INITIATOR_IQN,
        'chap_username': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-+@_=:/[],'
        '~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-+@_=:/[],'
        '~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-+@_=:/[],'
        '~abcdefghijklmnopqrs.-+@_=:/[],~',
        'chap_password': '.-+@_=:/[],~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-+@_=:/[],'
        '~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-+@_=:/[],'
        '~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-+@_=:/[],'
        '~abcdefghijklmnopqrs',
        'chap_target_username': '0123456789.-+@_=:/[],~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-+@_=:/['
        '],~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-+@_=:/[],'
        '~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-+@_=:/[],'
        '~abcdefghijklmnopqrs',
        'chap_target_password': '.-+@_=:/[],~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-+@_=:/[],'
        '~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-+@_=:/[],'
        '~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-+@_=:/[],'
        '~abcdefghijklmnopqrs0123456789',
        'tpg_or_acl': 'tpg',
    },
    {  # Configures 2-way CHAP for iSCSI tests with random credentials
        't_iqn': TARGET_IQN,
        'i_iqn': INITIATOR_IQN,
        'chap_username': rand_string(randint(1, 255)),
        'chap_password': rand_string(randint(1, 255)),
        'chap_target_username': rand_string(randint(1, 255)),
        'chap_target_password': rand_string(randint(1, 255)),
        'tpg_or_acl': 'tpg',
    },
]

# Arguments for acl authentication test
argument_acl = [
    {  # Configures 1-way CHAP for iSCSI tests
        't_iqn': TARGET_IQN,
        'i_iqn': INITIATOR_IQN,
        'chap_username': CHAP_USERNAME,
        'chap_password': CHAP_PASSWORD,
        'chap_target_username': '',
        'chap_target_password': '',
        'tpg_or_acl': 'acl',
    },
    {  # Configures 2-way CHAP for iSCSI tests
        't_iqn': TARGET_IQN,
        'i_iqn': INITIATOR_IQN,
        'chap_username': CHAP_USERNAME,
        'chap_password': CHAP_PASSWORD,
        'chap_target_username': CHAP_TARGET_USERNAME,
        'chap_target_password': CHAP_TARGET_PASSWORD,
        'tpg_or_acl': 'acl',
    },
]

# Arguments for iscsi target setup
argument_iscsi_target = [
    {
        't_iqn': TARGET_IQN,
        'i_iqn': INITIATOR_IQN,
        'n_luns': 2,
        'back_size': '2M',
    },
]


@pytest.mark.parametrize('iscsi_target_setup', argument_iscsi_target, indirect=True)
@pytest.mark.usefixtures('_iscsi_test', 'iscsi_target_setup')
class TestChapAuth:
    """Test class for testing CHAP authentication."""

    iscsi_target: lio.Iscsi = None

    @pytest.fixture(autouse=True, scope='class')
    def _setup(self, iscsi_target_setup: Generator) -> None:
        self.__class__.iscsi_target = iscsi_target_setup
        iscsi.set_initiatorname(argument_iscsi_target[0]['i_iqn'])

    @pytest.mark.parametrize('configure_auth', argument_tpg, indirect=True)
    @pytest.mark.usefixtures('configure_auth')
    def test_tpg_auth(self) -> None:
        """Tests TPG authentication."""
        iscsiadm = iscsi.IscsiAdm(debug_level=8)
        assert iscsiadm.discovery().succeeded
        arguments_login = {'-p': '127.0.0.1', '-T': TARGET_IQN, '-I': 'default', '--login': None}
        assert iscsiadm.node_login(**arguments_login).succeeded
        arguments_logout = {'-p': '127.0.0.1', '-T': TARGET_IQN, '-I': 'default', '--logout': None}
        assert iscsiadm.node_logout(**arguments_logout).succeeded

    @pytest.mark.parametrize('configure_auth', argument_acl, indirect=True)
    @pytest.mark.usefixtures('configure_auth')
    def test_acl_auth(self) -> None:
        """Tests ACL authentication."""
        # no-gen-acls, auth per-acl
        iscsiadm = iscsi.IscsiAdm(debug_level=8)
        assert iscsiadm.discovery().succeeded
        arguments_login = {'-p': '127.0.0.1', '-T': TARGET_IQN, '-I': 'default', '--login': None}
        assert iscsiadm.node_login(**arguments_login).succeeded
        arguments_logout = {'-p': '127.0.0.1', '-T': TARGET_IQN, '-I': 'default', '--logout': None}
        assert iscsiadm.node_logout(**arguments_logout).succeeded
