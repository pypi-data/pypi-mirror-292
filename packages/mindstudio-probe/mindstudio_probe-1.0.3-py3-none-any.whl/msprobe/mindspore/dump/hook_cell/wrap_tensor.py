# Copyright 2024 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

import os
import mindspore as ms
from msprobe.mindspore.dump.hook_cell.hook_cell import HOOKCell
from msprobe.core.common.utils import Const, load_yaml


cur_path = os.path.dirname(os.path.realpath(__file__))
yaml_path = os.path.join(cur_path, "support_wrap_ops.yaml")


TensorFunc = {}
for f in dir(ms.Tensor):
    TensorFunc[f] = getattr(ms.Tensor, f)


def get_tensor_ops():
    yaml_data = load_yaml(yaml_path)
    wrap_tensor_ops = yaml_data.get('tensor')
    _tensor_ops = dir(ms.Tensor)
    return set(wrap_tensor_ops) & set(_tensor_ops)


class HOOKTensor(object):
    pass


class TensorOPTemplate(HOOKCell):

    def __init__(self, op_name, hook):
        self.op_name_ = op_name
        self.prefix_op_name_ = "Tensor." + str(op_name) + Const.SEP
        super().__init__(hook)

    def construct(self, *args, **kwargs):
        return TensorFunc[str(self.op_name_)](*args, **kwargs)


def wrap_tensor_op(op_name, hook):
    def tensor_op_template(*args, **kwargs):
        return TensorOPTemplate(op_name, hook)(*args, **kwargs)
    return tensor_op_template


def wrap_tensor_ops_and_bind(hook):
    _tensor_ops = get_tensor_ops()
    for op_name in _tensor_ops:
        if callable(TensorFunc[op_name]):
            setattr(HOOKTensor, Const.ATTR_NAME_PREFIX + str(op_name), wrap_tensor_op(op_name, hook))
