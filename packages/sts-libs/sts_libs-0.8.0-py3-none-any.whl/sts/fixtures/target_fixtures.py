import time
from collections.abc import Generator

import pytest
from _pytest.fixtures import SubRequest

from sts import iscsi, lio
from sts.linux import log_kernel_version
from sts.loopdev import create_loopdev, delete_loopdev
from sts.utils.cmdline import run


@pytest.fixture(scope='class')
def _target_test() -> Generator:
    """Installs userspace utilities and does target cleanup before and after the test."""
    assert lio.lio_install()
    lio.log_versions()
    log_kernel_version()
    lio.lio_clearconfig()
    yield
    lio.lio_clearconfig()


@pytest.fixture
def loopdev_setup(_target_test: None, request: SubRequest) -> Generator:
    """Creates loopback device before the test and delete it after the test."""
    name = request.param['name']
    size = request.param['size']
    dev_path = create_loopdev(name, size)
    assert dev_path
    yield dev_path
    assert delete_loopdev(dev_path)


@pytest.fixture
def backstore_block_setup(loopdev_setup: Generator, request: SubRequest) -> Generator:
    """Creates block backstore before test and delete it after the test."""
    loop_dev = loopdev_setup
    name = request.param['name']

    bs = lio.BackstoreBlock(name=name)
    result = bs.create_backstore(dev=loop_dev)
    assert result.succeeded
    assert f'Created block storage object {name} using {loop_dev}.\n' in result.stdout
    yield bs
    assert bs.delete_backstore().succeeded


@pytest.fixture
def backstore_fileio_setup(_target_test: None, request: SubRequest) -> Generator:
    """Creates fileio backstore before test and delete it after the test."""
    name = request.param['name']
    size = request.param['size']
    file_or_dev = request.param['file_or_dev']
    size_in_byte = request.param['size_in_byte']

    bs = lio.BackstoreFileio(name=name)
    result = bs.create_backstore(size=size, file_or_dev=file_or_dev)
    assert result.succeeded
    assert f'Created fileio {name} with size {size_in_byte}\n' in result.stdout
    yield bs
    assert bs.delete_backstore().succeeded


@pytest.fixture
def backstore_ramdisk_setup(_target_test: None, request: SubRequest) -> Generator:
    """Creates ramdisk backstore before test and delete it after the test."""
    name = request.param['name']
    size = request.param['size']

    bs = lio.BackstoreRamdisk(name=name)
    result = bs.create_backstore(size=size)
    assert result.succeeded
    assert f'Created ramdisk {name} with size {size}.\n' in result.stdout
    yield bs
    assert bs.delete_backstore().succeeded


@pytest.fixture(scope='class')
def iscsi_target_setup(_target_test: None, request: SubRequest) -> Generator:
    """Creates iscsi target with acl and luns before test and delete it after the test."""
    t_iqn = request.param['t_iqn'] or 'iqn.2003-01.com.redhat:targetauthtest'
    i_iqn = request.param['i_iqn'] or None
    n_luns = request.param['n_luns'] or 0
    back_size = request.param['back_size'] or None

    assert lio.Iscsi(target_wwn=t_iqn).create_target().succeeded
    if i_iqn:
        assert lio.ACL(target_wwn=t_iqn, initiator_wwn=i_iqn).create_acl().succeeded
    if back_size and n_luns > 0:
        for n in range(n_luns):
            backstore = lio.BackstoreFileio(name=f'backstore{n}')
            assert backstore.create_backstore(size=back_size, file_or_dev=f'backstore_file{n}').succeeded
            assert lio.LUNs(target_wwn=t_iqn).create_lun(storage_object=backstore.path).succeeded

    yield lio.Iscsi(target_wwn=t_iqn)

    assert lio.Iscsi(target_wwn=t_iqn).delete_target().succeeded
    run('rm -rf ./backstore_file*')


@pytest.fixture
def configure_auth(request: SubRequest) -> Generator:
    """Set chap authentication."""
    t_iqn = request.param['t_iqn']
    i_iqn = request.param['i_iqn']
    chap_username = request.param['chap_username']
    chap_password = request.param['chap_password']
    chap_target_username = request.param['chap_target_username']
    chap_target_password = request.param['chap_target_password']
    tpg_or_acl = request.param['tpg_or_acl']

    iscsi_target = lio.Iscsi(target_wwn=t_iqn)
    tpg = lio.TPG(target_wwn=t_iqn)
    acl = lio.ACL(target_wwn=t_iqn, initiator_wwn=i_iqn)

    assert iscsi.disable_chap()
    assert acl.disable_auth().succeeded
    assert tpg.disable_auth_per_tpg().succeeded
    assert iscsi_target.disable_discovery_auth().succeeded
    # to avoid repeatedly restarting iscsid service too quickly
    time.sleep(10)
    assert iscsi_target.set_discovery_auth(chap_username, chap_password, chap_target_username, chap_target_password)
    assert tpg.set_auth(chap_username, chap_password, chap_target_username, chap_target_password).succeeded
    assert acl.set_auth(chap_username, chap_password, chap_target_username, chap_target_password)
    if tpg_or_acl == 'acl':
        assert tpg.disable_generate_node_acls().succeeded
    assert iscsi.set_chap(chap_username, chap_password, chap_target_username, chap_target_password)

    yield iscsi_target

    assert iscsi.disable_chap()
    assert acl.disable_auth().succeeded
    assert tpg.disable_auth_per_tpg().succeeded
    assert iscsi_target.disable_discovery_auth().succeeded
    # to avoid repeatedly restarting iscsid service too quickly
    time.sleep(10)
