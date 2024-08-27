#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from sts import iscsi
from sts.utils.cmdline import run

arguments_list = [
    {
        't_iqn': 'iqn.2003-01.com.redhat:targettest1',
        'i_iqn': 'iqn.2003-01.com.redhat:initiatortest1',
        'n_luns': 256,
        'back_size': '1M',
    },
    {
        't_iqn': 'iqn.2003-01.com.redhat:targettest2',
        'i_iqn': 'iqn.2003-01.com.redhat:initiatortest2',
        'n_luns': 1,
        'back_size': '1G',
    },
    {
        't_iqn': 'iqn.2003-01.com.redhat:targettest3',
        'i_iqn': 'iqn.2003-01.com.redhat:initiatortest3',
        'n_luns': 0,
        'back_size': '1G',
    },
]


@pytest.mark.parametrize('iscsi_target_setup', arguments_list, indirect=True)
@pytest.mark.usefixtures('iscsi_target_setup')
def test_iscsi_target() -> None:
    iscsiadm = iscsi.IscsiAdm(debug_level=8)
    assert iscsiadm.discovery().succeeded
    assert iscsiadm.node_login()
    assert iscsiadm.node_logoutall()

    run('rm -rf ./backstore_file*')
