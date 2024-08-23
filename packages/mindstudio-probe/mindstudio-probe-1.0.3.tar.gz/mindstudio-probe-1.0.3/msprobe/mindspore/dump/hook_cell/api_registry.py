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

import mindspore as ms
from msprobe.mindspore.dump.hook_cell.wrap_functional import get_functional_ops, setup_hooks, \
    HOOKFunctionalOP, HOOKMintOP, HOOKMintNNFunctionalOP
from msprobe.mindspore.dump.hook_cell.wrap_tensor import get_tensor_ops, wrap_tensor_ops_and_bind, HOOKTensor
from msprobe.core.common.utils import Const


class ApiRegistry:
    def __init__(self):
        self.tensor_ori_attr = {}
        self.functional_ori_attr = {}
        self.mint_ops_ori_attr = {}
        self.mint_func_ops_ori_attr = {}
        self.norm_inner_ops_ori_attr = {}

        self.tensor_hook_attr = {}
        self.functional_hook_attr = {}
        self.mint_ops_hook_attr = {}
        self.mint_func_ops_hook_attr = {}
        self.norm_inner_ops_hook_attr = {}

        self.norm_inner_ops = ["norm", "square", "sqrt", "is_complex"]

    @staticmethod
    def store_ori_attr(ori_api_group, api_list, api_ori_attr):
        for api in api_list:
            if Const.SEP in api:
                sub_module_name, sub_op = api.rsplit(Const.SEP, 1)
                sub_module = getattr(ori_api_group, sub_module_name)
                api_ori_attr[api] = getattr(sub_module, sub_op)
            else:
                api_ori_attr[api] = getattr(ori_api_group, api)

    @staticmethod
    def set_api_attr(api_group, attr_dict):
        for api, api_attr in attr_dict.items():
            if Const.SEP in api:
                sub_module_name, sub_op = api.rsplit(Const.SEP, 1)
                sub_module = getattr(api_group, sub_module_name, None)
                if sub_module is not None:
                    setattr(sub_module, sub_op, api_attr)
            else:
                setattr(api_group, api, api_attr)

    def norm_inner_op_set_hook_func(self):
        self.set_api_attr(ms.ops, self.norm_inner_ops_hook_attr)

    def norm_inner_op_set_ori_func(self):
        self.set_api_attr(ms.ops, self.norm_inner_ops_ori_attr)

    def api_set_hook_func(self):
        self.set_api_attr(ms.Tensor, self.tensor_hook_attr)
        self.set_api_attr(ms.ops, self.functional_hook_attr)
        self.set_api_attr(ms.mint, self.mint_ops_hook_attr)
        self.set_api_attr(ms.mint.nn.functional, self.mint_func_ops_hook_attr)

    def api_set_ori_func(self):
        self.set_api_attr(ms.Tensor, self.tensor_ori_attr)
        self.set_api_attr(ms.ops, self.functional_ori_attr)
        self.set_api_attr(ms.mint, self.mint_ops_ori_attr)
        self.set_api_attr(ms.mint.nn.functional, self.mint_func_ops_ori_attr)

    def initialize_hook(self, hook):
        self.store_ori_attr(ms.Tensor, get_tensor_ops(), self.tensor_ori_attr)
        wrap_tensor_ops_and_bind(hook)
        for attr_name in dir(HOOKTensor):
            if attr_name.startswith(Const.ATTR_NAME_PREFIX):
                self.tensor_hook_attr[attr_name[Const.ATTR_NAME_PREFIX_LEN:]] = getattr(HOOKTensor, attr_name)

        functional_ops, mint_ops, mint_func_ops = get_functional_ops()
        self.store_ori_attr(ms.ops, self.norm_inner_ops, self.norm_inner_ops_ori_attr)
        self.store_ori_attr(ms.ops, functional_ops, self.functional_ori_attr)
        self.store_ori_attr(ms.mint, mint_ops, self.mint_ops_ori_attr)
        self.store_ori_attr(ms.mint.nn.functional, mint_func_ops, self.mint_func_ops_ori_attr)
        setup_hooks(hook)
        for attr_name in dir(HOOKFunctionalOP):
            if attr_name.startswith(Const.ATTR_NAME_PREFIX):
                self.functional_hook_attr[attr_name[Const.ATTR_NAME_PREFIX_LEN:]] = getattr(HOOKFunctionalOP, attr_name)
                if attr_name[Const.ATTR_NAME_PREFIX_LEN:] in self.norm_inner_ops:
                    self.norm_inner_ops_hook_attr[attr_name[Const.ATTR_NAME_PREFIX_LEN:]] = getattr(HOOKFunctionalOP, attr_name)
        for attr_name in dir(HOOKMintOP):
            if attr_name.startswith(Const.ATTR_NAME_PREFIX):
                self.mint_ops_hook_attr[attr_name[Const.ATTR_NAME_PREFIX_LEN:]] = getattr(HOOKMintOP, attr_name)
        for attr_name in dir(HOOKMintNNFunctionalOP):
            if attr_name.startswith(Const.ATTR_NAME_PREFIX):
                self.mint_func_ops_hook_attr[attr_name[Const.ATTR_NAME_PREFIX_LEN:]] = getattr(HOOKMintNNFunctionalOP, attr_name)


api_register = ApiRegistry()
