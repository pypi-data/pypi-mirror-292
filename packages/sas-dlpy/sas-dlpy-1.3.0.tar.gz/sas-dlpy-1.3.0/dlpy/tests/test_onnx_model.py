#!/usr/bin/env python
# encoding: utf-8
#
# Copyright SAS Institute
#
#  Licensed under the Apache License, Version 2.0 (the License);
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

# NOTE: This test requires a running CAS server.  You must use an ~/.authinfo
#       file to specify your username and password.  The CAS host and port must
#       be specified using the CASHOST and CASPORT environment variables.
#       A specific protocol ('cas', 'http', 'https', or 'auto') can be set using
#       the CASPROTOCOL environment variable.

import os
import swat
import swat.utils.testing as tm
from swat.cas.table import CASTable
from dlpy.model import Model, Optimizer, AdamSolver, Sequence
from dlpy.sequential import Sequential
from dlpy.timeseries import TimeseriesTable
from dlpy.layers import (InputLayer, Conv2d, Pooling, Dense, OutputLayer,
                         Recurrent, Keypoints, BN, Res, Concat, Reshape)
from dlpy.utils import caslibify
from dlpy.applications import Tiny_YoloV2
import unittest


class TestModel(unittest.TestCase):
    '''
    Please locate the images.sashdat file under the datasources to the DLPY_DATA_DIR.
    '''
    server_type = None
    s = None
    server_sep = '/'
    data_dir = None
    data_dir_local = None

    def setUp(self):
        swat.reset_option()
        swat.options.cas.print_messages = False
        swat.options.interactive_mode = False

        self.s = swat.CAS()
        self.server_type = tm.get_cas_host_type(self.s)
        self.server_sep = '\\'
        if self.server_type.startswith("lin") or self.server_type.startswith("osx"):
            self.server_sep = '/'

        if 'DLPY_DATA_DIR' in os.environ:
            self.data_dir = os.environ.get('DLPY_DATA_DIR')
            if self.data_dir.endswith(self.server_sep):
                self.data_dir = self.data_dir[:-1]
            self.data_dir += self.server_sep

        if 'DLPY_DATA_DIR_LOCAL' in os.environ:
            self.data_dir_local = os.environ.get('DLPY_DATA_DIR_LOCAL')
            if self.data_dir_local.endswith(self.server_sep):
                self.data_dir_local = self.data_dir_local[:-1]
            self.data_dir_local += self.server_sep

    def test_model1(self):
        try:
            import onnx
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")

        model1 = Sequential(self.s, model_table='Simple_CNN1')
        model1.add(InputLayer(3, 224, 224))
        model1.add(Conv2d(8, 7))
        model1.add(Pooling(2))
        model1.add(Conv2d(8, 7))
        model1.add(Pooling(2))
        model1.add(Dense(16))
        model1.add(OutputLayer(act='softmax', n=2))

        if self.data_dir is None:
            unittest.TestCase.skipTest(self, "DLPY_DATA_DIR is not set in the environment variables")

        caslib, path, tmp_caslib = caslibify(self.s, path=self.data_dir+'images.sashdat', task='load')

        self.s.table.loadtable(caslib=caslib,
                               casout={'name': 'eee', 'replace': True},
                               path=path)

        r = model1.fit(data='eee', inputs='_image_', target='_label_', max_epochs=1)
        self.assertTrue(r.severity == 0)

        import tempfile
        tmp_dir_to_dump = tempfile.gettempdir()

        model1.deploy(tmp_dir_to_dump, output_format='onnx')

        import os
        os.remove(os.path.join(tmp_dir_to_dump, "Simple_CNN1.onnx"))

        if (caslib is not None) and tmp_caslib:
            self.s.retrieve('table.dropcaslib', message_level='error', caslib=caslib)
        
    def test_model2(self):
        try:
            import onnx
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")

        model1 = Sequential(self.s, model_table='Simple_CNN1')
        model1.add(InputLayer(3, 224, 224))
        model1.add(Conv2d(8, 7))
        pool1 = Pooling(2)
        model1.add(pool1)
        conv1 = Conv2d(1, 7, src_layers=[pool1])
        conv2 = Conv2d(1, 7, src_layers=[pool1])
        model1.add(conv1)
        model1.add(conv2)
        model1.add(Concat(act='identity', src_layers=[conv1, conv2]))
        model1.add(Pooling(2))
        model1.add(Dense(2))
        model1.add(OutputLayer(act='softmax', n=2))

        if self.data_dir is None:
            unittest.TestCase.skipTest(self, "DLPY_DATA_DIR is not set in the environment variables")

        caslib, path, tmp_caslib = caslibify(self.s, path=self.data_dir+'images.sashdat', task='load')

        self.s.table.loadtable(caslib=caslib,
                               casout={'name': 'eee', 'replace': True},
                               path=path)

        r = model1.fit(data='eee', inputs='_image_', target='_label_', max_epochs=1)
        self.assertTrue(r.severity == 0)

        import tempfile
        tmp_dir_to_dump = tempfile.gettempdir()

        model1.deploy(tmp_dir_to_dump, output_format='onnx')

        import os
        os.remove(os.path.join(tmp_dir_to_dump, "Simple_CNN1.onnx"))

        if (caslib is not None) and tmp_caslib:
            self.s.retrieve('table.dropcaslib', message_level='error', caslib=caslib)

    def test_model3(self):
        try:
            import onnx
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")

        model1 = Sequential(self.s, model_table='Simple_CNN1')
        model1.add(InputLayer(3, 224, 224))
        model1.add(Conv2d(8, 7))
        pool1 = Pooling(2)
        model1.add(pool1)
        conv1 = Conv2d(1, 1, act='identity', src_layers=[pool1])
        model1.add(conv1)
        model1.add(Res(act='relu', src_layers=[conv1, pool1]))
        model1.add(Pooling(2))
        model1.add(Dense(2))
        model1.add(OutputLayer(act='softmax', n=2))

        if self.data_dir is None:
            unittest.TestCase.skipTest(self, "DLPY_DATA_DIR is not set in the environment variables")

        caslib, path, tmp_caslib = caslibify(self.s, path=self.data_dir+'images.sashdat', task='load')

        self.s.table.loadtable(caslib=caslib,
                               casout={'name': 'eee', 'replace': True},
                               path=path)

        #
        # unittest.TestCase.skipTest(self, "Skipping temporarily due to server error.")

        r = model1.fit(data='eee', inputs='_image_', target='_label_', max_epochs=1)
        self.assertTrue(r.severity == 0)

        import tempfile
        tmp_dir_to_dump = tempfile.gettempdir()

        model1.deploy(tmp_dir_to_dump, output_format='onnx')

        import os
        os.remove(os.path.join(tmp_dir_to_dump, "Simple_CNN1.onnx"))

        if (caslib is not None) and tmp_caslib:
            self.s.retrieve('table.dropcaslib', message_level='error', caslib=caslib)
        
    def test_model4(self):
        try:
            import onnx
            from onnx import numpy_helper
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")

        import numpy as np

        model1 = Sequential(self.s, model_table='Simple_CNN1')
        model1.add(InputLayer(3, 224, 224))
        model1.add(Conv2d(8, 7, act='identity', include_bias=False))
        model1.add(Reshape(height=448, width=448, depth=2, act='IDENTITY'))
        model1.add(Reshape(height=448, width=448, depth=2, act='RECTIFIER'))
        model1.add(Conv2d(8, 7, act='identity', include_bias=False))
        model1.add(BN(act='relu'))
        model1.add(Dense(2))
        model1.add(OutputLayer(act='softmax', n=2))

        if self.data_dir is None:
            unittest.TestCase.skipTest(self, "DLPY_DATA_DIR is not set in the environment variables")

        caslib, path, tmp_caslib = caslibify(self.s, path=self.data_dir+'images.sashdat', task='load')

        self.s.table.loadtable(caslib=caslib,
                               casout={'name': 'eee', 'replace': True},
                               path=path)

        r = model1.fit(data='eee', inputs='_image_', target='_label_', max_epochs=1)
        self.assertTrue(r.severity == 0)

        if self.data_dir_local is None:
            unittest.TestCase.skipTest(self, "DLPY_DATA_DIR_LOCAL is not set in the environment variables")

        #model1.deploy(self.data_dir_local, output_format='onnx')

        import tempfile
        tmp_dir_to_dump = tempfile.gettempdir()

        model1.deploy(tmp_dir_to_dump, output_format='onnx')
        import os
        model_path = os.path.join(tmp_dir_to_dump, 'Simple_CNN1.onnx')

        m = onnx.load(model_path)
        self.assertEqual(m.graph.node[1].op_type, 'Reshape')
        init = numpy_helper.to_array(m.graph.initializer[1])
        self.assertTrue(np.array_equal(init, [ -1,  2, 448, 448]))

        import os
        os.remove(os.path.join(tmp_dir_to_dump, "Simple_CNN1.onnx"))

        if (caslib is not None) and tmp_caslib:
            self.s.retrieve('table.dropcaslib', message_level = 'error', caslib = caslib)
        
    def test_model5(self):
        try:
            import onnx
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")

        model1 = Sequential(self.s, model_table='Simple_CNN1')
        model1.add(InputLayer(3, 224, 224))
        model1.add(Conv2d(8, 7, act='identity', include_bias=False))
        model1.add(BN(act='relu'))
        model1.add(Pooling(2))
        model1.add(Conv2d(8, 7, act='identity', include_bias=False))
        model1.add(BN(act='relu'))
        model1.add(Pooling(2))
        model1.add(Conv2d(8, 7))
        model1.add(Conv2d(8, 7))
        model1.add(Dense(2))
        model1.add(OutputLayer(act='softmax', n=2))

        if self.data_dir is None:
            unittest.TestCase.skipTest(self, "DLPY_DATA_DIR is not set in the environment variables")

        caslib, path, tmp_caslib = caslibify(self.s, path=self.data_dir+'images.sashdat', task='load')

        self.s.table.loadtable(caslib=caslib,
                               casout={'name': 'eee', 'replace': True},
                               path=path)

        r = model1.fit(data='eee', inputs='_image_', target='_label_', max_epochs=1)
        self.assertTrue(r.severity == 0)

        import tempfile
        tmp_dir_to_dump = tempfile.gettempdir()

        model1.deploy(tmp_dir_to_dump, output_format='onnx')

        import os
        os.remove(os.path.join(tmp_dir_to_dump, "Simple_CNN1.onnx"))

        if (caslib is not None) and tmp_caslib:
            self.s.retrieve('table.dropcaslib', message_level='error', caslib=caslib)
        
    def test_model6(self):
        try:
            import onnx
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")

        m = onnx.load(os.path.join(os.path.dirname(__file__), 'datasources', 'model.onnx'))
        model1 = Model.from_onnx_model(self.s, m)
        model1.print_summary()

    def test_model7(self):
        try:
            import onnx
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")

        m = onnx.load(os.path.join(os.path.dirname(__file__), 'datasources', 'model.onnx'))
        model1 = Model.from_onnx_model(self.s, m, offsets=[1, 1, 1,], scale=2, std='std')
        model1.print_summary()

    def test_model8(self):
        try:
            import onnx
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")

        if self.data_dir_local is None:
            unittest.TestCase.skipTest(self, "DLPY_DATA_DIR_LOCAL is not set in "
                                             "the environment variables")

        m = onnx.load(os.path.join(self.data_dir_local, 'Simple_CNN1.onnx'))
        model1 = Model.from_onnx_model(self.s, m, offsets=[1, 1, 1,], scale=2, std='std')
        model1.print_summary()

    def test_model9(self):
        try:
            import onnx
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")

        m = onnx.load(os.path.join(os.path.dirname(__file__), 'datasources', 'pytorch_net1.onnx'))
        model1 = Model.from_onnx_model(self.s, m, offsets=[1, 1, 1,], scale=2, std='std')
        model1.print_summary()

    def test_model10(self):
        try:
            import onnx
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")

        m = onnx.load(os.path.join(os.path.dirname(__file__), 'datasources', 'pytorch_net2.onnx'))
        model1 = Model.from_onnx_model(self.s, m, offsets=[1, 1, 1,], scale=2, std='std')
        model1.print_summary()

    def test_model11(self):
        # test specifying output layer in Model.from_onnx_model
        try:
            import onnx
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")

        if self.data_dir_local is None:
            unittest.TestCase.skipTest(self, "DLPY_DATA_DIR_LOCAL is not set in "
                                             "the environment variables")

        m = onnx.load(os.path.join(self.data_dir_local, 'Simple_CNN1.onnx'))
        output_layer = OutputLayer(n=100)
        model1 = Model.from_onnx_model(conn=self.s,
                                       onnx_model=m,
                                       offsets=[1, 1, 1,],
                                       scale=2,
                                       std='std',
                                       output_layer=output_layer)

        self.assertTrue(model1.layers[-1].config['n'] == 100)

    def test_model12(self):
        # test specifying output layer in Model.from_onnx_model
        try:
            import onnx
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")

        if self.data_dir_local is None:
            unittest.TestCase.skipTest(self, "DLPY_DATA_DIR_LOCAL is not set in "
                                             "the environment variables")

        m = onnx.load(os.path.join(self.data_dir_local, 'Simple_CNN1.onnx'))
        output_layer = OutputLayer(name='test_output', n=50)
        model1 = Model.from_onnx_model(conn=self.s,
                                       onnx_model=m,
                                       offsets=[1, 1, 1,],
                                       scale=2,
                                       std='std',
                                       output_layer=output_layer)

        self.assertTrue(model1.layers[-1].name == 'test_output')
        self.assertTrue(model1.layers[-1].config['n'] == 50)

    def test_model13(self):
        # test dropout
        try:
            import onnx
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")

        model1 = Sequential(self.s, model_table='Simple_CNN1')
        model1.add(InputLayer(3, 224, 224))
        model1.add(Conv2d(8, 7, act='IDENTITY', dropout=0.5, include_bias=False))
        model1.add(BN(act='relu'))
        model1.add(Pooling(2, pool='MEAN', dropout=0.5))
        model1.add(Conv2d(8, 7, act='IDENTITY', dropout=0.5, include_bias=False))
        model1.add(BN(act='relu'))
        model1.add(Pooling(2, pool='MEAN', dropout=0.5))
        model1.add(Conv2d(8, 7, act='identity', include_bias=False))
        model1.add(BN(act='relu'))
        model1.add(Dense(16, act='IDENTITY', dropout=0.1))
        model1.add(OutputLayer(act='softmax', n=2))

        if self.data_dir is None:
            unittest.TestCase.skipTest(self, "DLPY_DATA_DIR is not set in the environment variables")

        caslib, path, tmp_caslib = caslibify(self.s, path=self.data_dir+'images.sashdat', task='load')

        self.s.table.loadtable(caslib=caslib,
                               casout={'name': 'eee', 'replace': True},
                               path=path)

        r = model1.fit(data='eee', inputs='_image_', target='_label_', max_epochs=2)
        self.assertTrue(r.severity == 0)

        import tempfile
        tmp_dir_to_dump = tempfile.gettempdir()
        model1.deploy(tmp_dir_to_dump, output_format='onnx')

        import os
        os.remove(os.path.join(tmp_dir_to_dump, "Simple_CNN1.onnx"))

        if (caslib is not None) and tmp_caslib:
            self.s.retrieve('table.dropcaslib', message_level='error', caslib=caslib)

    def test_model14(self):
        # test output layer with full_connect=False
        try:
            import onnx
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")

        model1 = Sequential(self.s, model_table='Simple_CNN1')
        model1.add(InputLayer(3, 224, 224))
        model1.add(Conv2d(8, 7))
        model1.add(Conv2d(8, 7))
        model1.add(Pooling(2))
        model1.add(Conv2d(8, 7))
        model1.add(Conv2d(8, 7))
        model1.add(Pooling(2))
        model1.add(Dense(16))
        model1.add(Dense(2))
        model1.add(OutputLayer(act='softmax', n=2, full_connect=False))

        if self.data_dir is None:
            unittest.TestCase.skipTest(self, "DLPY_DATA_DIR is not set in the environment variables")

        caslib, path, tmp_caslib = caslibify(self.s, path=self.data_dir+'images.sashdat', task='load')

        self.s.table.loadtable(caslib=caslib,
                               casout={'name': 'eee', 'replace': True},
                               path=path)

        r = model1.fit(data='eee', inputs='_image_', target='_label_', max_epochs=1)
        self.assertTrue(r.severity == 0)

        import tempfile
        tmp_dir_to_dump = tempfile.gettempdir()

        model1.deploy(tmp_dir_to_dump, output_format='onnx')

        import os
        os.remove(os.path.join(tmp_dir_to_dump, "Simple_CNN1.onnx"))

        if (caslib is not None) and tmp_caslib:
            self.s.retrieve('table.dropcaslib', message_level='error', caslib=caslib)

    def test_model15(self):
        # test RECTIFIER activation for concat layer 
        try:
            import onnx
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")

        model1 = Sequential(self.s, model_table='Simple_CNN1')
        model1.add(InputLayer(3, 224, 224))
        model1.add(Conv2d(8, 7))
        pool1 = Pooling(2)
        model1.add(pool1)
        conv1 = Conv2d(1, 7, src_layers=[pool1])
        conv2 = Conv2d(1, 7, src_layers=[pool1])
        model1.add(conv1)
        model1.add(conv2)
        model1.add(Concat(act='RECTIFIER', src_layers=[conv1, conv2]))
        model1.add(Pooling(2))
        model1.add(Dense(2))
        model1.add(OutputLayer(act='softmax', n=2))

        if self.data_dir is None:
            unittest.TestCase.skipTest(self, "DLPY_DATA_DIR is not set in the environment variables")

        caslib, path, tmp_caslib = caslibify(self.s, path=self.data_dir+'images.sashdat', task='load')

        self.s.table.loadtable(caslib=caslib,
                               casout={'name': 'eee', 'replace': True},
                               path=path)

        r = model1.fit(data='eee', inputs='_image_', target='_label_', max_epochs=1)
        self.assertTrue(r.severity == 0)

        import tempfile
        tmp_dir_to_dump = tempfile.gettempdir()

        model1.deploy(tmp_dir_to_dump, output_format='onnx')

        import os
        os.remove(os.path.join(tmp_dir_to_dump, "Simple_CNN1.onnx"))

        if (caslib is not None) and tmp_caslib:
            self.s.retrieve('table.dropcaslib', message_level='error', caslib=caslib)

    def test_model16(self):
        # test dropout with non-identity activations
        try:
            import onnx
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")

        model1 = Sequential(self.s, model_table='Simple_CNN1')
        model1.add(InputLayer(3, 224, 224))
        model1.add(Conv2d(8, 7, act='RECTIFIER', dropout=0.5, include_bias=False))
        model1.add(Pooling(2, pool='MEAN', dropout=0.5))
        model1.add(Conv2d(8, 7, act='RECTIFIER', dropout=0.5, include_bias=False))
        model1.add(Pooling(2, pool='MEAN', dropout=0.5))
        model1.add(Conv2d(8, 7, act='IDENTITY', include_bias=False))
        model1.add(BN(act='RECTIFIER'))
        model1.add(Dense(16, act='RECTIFIER', dropout=0.1))
        model1.add(OutputLayer(act='softmax', n=2))

        if self.data_dir is None:
            unittest.TestCase.skipTest(self, "DLPY_DATA_DIR is not set in the environment variables")

        caslib, path, tmp_caslib = caslibify(self.s, path=self.data_dir+'images.sashdat', task='load')

        self.s.table.loadtable(caslib=caslib,
                               casout={'name': 'eee', 'replace': True},
                               path=path)

        r = model1.fit(data='eee', inputs='_image_', target='_label_', max_epochs=1)
        self.assertTrue(r.severity == 0)

        import tempfile
        tmp_dir_to_dump = tempfile.gettempdir()
        model1.deploy(tmp_dir_to_dump, output_format='onnx')

        import os
        os.remove(os.path.join(tmp_dir_to_dump, "Simple_CNN1.onnx"))

        if (caslib is not None) and tmp_caslib:
            self.s.retrieve('table.dropcaslib', message_level='error', caslib=caslib)

    def test_model17(self):
        # test GlobalAveragePooling
        try:
            import onnx
        except:
            unittest.TestCase.skipTest(self, "onnx not found in the libraries")
            
        from dlpy.applications import ResNet18_SAS

        model1 = ResNet18_SAS(self.s, model_table='ResNet18')

        if self.data_dir is None:
            unittest.TestCase.skipTest(self, "DLPY_DATA_DIR is not set in the environment variables")

        caslib, path, tmp_caslib = caslibify(self.s, path=self.data_dir+'images.sashdat', task='load')

        self.s.table.loadtable(caslib=caslib,
                               casout={'name': 'eee', 'replace': True},
                               path=path)

        r = model1.fit(data='eee', inputs='_image_', target='_label_', max_epochs=1)
        self.assertTrue(r.severity == 0)

        import tempfile
        tmp_dir_to_dump = tempfile.gettempdir()
        model1.deploy(tmp_dir_to_dump, output_format='onnx')

        import os
        os.remove(os.path.join(tmp_dir_to_dump, "ResNet18.onnx"))

        if (caslib is not None) and tmp_caslib:
            self.s.retrieve('table.dropcaslib', message_level='error', caslib=caslib)

    def test_mobilenetv2(self):
        # test loading of existing ONNX model
        try:
            import onnx
            from dlpy.model_conversion.onnx_transforms import (Transformer, OpTypePattern,
                                                               ConstToInitializer,
                                                               InitReshape, InitUnsqueeze,
                                                               FuseMulAddBN)
            from dlpy.model_conversion.onnx_graph import OnnxGraph
            from onnx import helper, numpy_helper
        except:
            unittest.TestCase.skipTest(self, 'onnx package not found')

        from dlpy.model import Model

        if self.data_dir is None:
            unittest.TestCase.skipTest(self, "DLPY_DATA_DIR_LOCAL is not set in the environment variables")


        path = os.path.join(self.data_dir, 'mobilenetv2-1.0.onnx')

        onnx_model = onnx.load_model(path)
        model1 = Model.from_onnx_model(self.s,
                                       onnx_model,
                                       output_model_table='mobilenetv2',
                                       offsets=255*[0.485, 0.456, 0.406],
                                       norm_stds=255*[0.229, 0.224, 0.225])

    def tearDown(self):
        # tear down tests
        try:
            self.s.terminate()
        except swat.SWATError:
            pass
        del self.s
        swat.reset_option()


if __name__ == '__main__':
    unittest.main()
