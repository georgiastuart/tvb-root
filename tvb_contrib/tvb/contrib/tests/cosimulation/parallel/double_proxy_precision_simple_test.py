# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2020, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

import numpy as np
import numpy.random as rgn

from tvb.tests.library.base_testcase import BaseTestCase
from tvb.contrib.tests.cosimulation.parallel.function_tvb import TvbSim


class TestDoubleProxyPrecisionSimple(BaseTestCase):
    """
    test the transmission of information between two model with proxy in simple case
    """

    def test_double_precision_simple(self):
        weight = np.array([[1, 1], [1, 1]])
        delay = np.array([[10.0, 10.0], [10.0, 10.0]])
        max = np.int(np.max(delay)*10+1)
        init_value = np.array([[[0.1,0.0], [0.1,0.0]]] * max)
        initial_condition = init_value.reshape((max, 2, weight.shape[0], 1))
        resolution_simulation = 0.1
        synchronization_time = 0.1 * 4
        proxy_id_1 = [0]
        proxy_id_2 = [1]

        # simulation with one proxy
        rgn.seed(42)
        sim_1 = TvbSim(weight, delay, proxy_id_1, resolution_simulation,
                       synchronization_time, initial_condition=initial_condition)
        time, result_1 = sim_1(synchronization_time)

        # simulation_2 with one proxy
        rgn.seed(42)
        sim_2 = TvbSim(weight, delay, proxy_id_2, resolution_simulation,
                       synchronization_time, initial_condition=initial_condition)
        time, result_2 = sim_2(synchronization_time)

        # full simulation
        rgn.seed(42)
        sim_ref = TvbSim(weight, delay, [], resolution_simulation,
                         synchronization_time, initial_condition=initial_condition)
        time, result_ref = sim_ref(synchronization_time)

        # COMPARE PROXY 1
        diff_1 = np.where(np.squeeze(result_ref[:, proxy_id_2, :], axis=2)[0] !=
                          np.squeeze(result_1[0][:, proxy_id_2, :], axis=2)[0])
        assert diff_1[0].size == 0
        # COMPARE PROXY 2
        diff_2 = np.where(np.squeeze(result_ref[:, proxy_id_1, :], axis=2)[0] !=
                          np.squeeze(result_2[0][:, proxy_id_1, :], axis=2)[0])
        assert diff_2[0].size == 0

        for i in range(0, 100):
            time, result_2 = sim_2(synchronization_time, [time, result_1[0][:, proxy_id_2][:, :, 0]])

            # compare with raw monitor delayed by synchronization_time
            diff_1 = np.where(result_ref != result_2[1])
            assert diff_1[0].size ==0

            time, result_1 = sim_1(synchronization_time, [time, result_ref[:, proxy_id_1][:, :, 0]])

            # compare with raw monitor delayed by synchronization_time
            diff_1 = np.where(result_ref != result_1[1])
            assert diff_1[0].size ==0

            time, result_ref = sim_ref(synchronization_time)

            # COMPARE PROXY 1
            diff_1 = np.where(np.squeeze(result_ref[:, proxy_id_2, :], axis=2)[0] !=
                              np.squeeze(result_1[0][:, proxy_id_2, :], axis=2)[0])
            assert diff_1[0].size == 0
            # COMPARE PROXY 2
            diff_2 = np.where(np.squeeze(result_ref[:, proxy_id_1, :], axis=2)[0] !=
                              np.squeeze(result_2[0][:, proxy_id_1, :], axis=2)[0])
            assert diff_2[0].size == 0
