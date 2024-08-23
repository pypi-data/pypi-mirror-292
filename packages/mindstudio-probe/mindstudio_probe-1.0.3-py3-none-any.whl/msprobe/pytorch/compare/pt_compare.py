import os.path
import torch
from msprobe.core.common.const import FileCheckConst, Const
from msprobe.core.common.log import logger
from msprobe.core.common.exceptions import FileCheckException
from msprobe.core.compare.acc_compare import Comparator 
from msprobe.core.common.utils import create_directory, check_configuration_param, task_dumppath_get, \
    check_compare_param, FileChecker
from msprobe.core.common.utils import CompareException


class PTComparator (Comparator):
    def __init__(self):
        self.frame_name = PTComparator.__name__
    
    def read_npy_data(self, dir_path, file_name):
        data_path = os.path.join(dir_path, file_name)
        path_checker = FileChecker(data_path, FileCheckConst.FILE, FileCheckConst.READ_ABLE,
                                FileCheckConst.PT_SUFFIX, False)
        data_path = path_checker.common_check()
        data_value = torch.load(data_path, map_location=torch.device('cpu')).detach()       # detach for less memory
        if data_value.dtype == torch.bfloat16:
            data_value = data_value.to(torch.float32)
        data_value = data_value.numpy()
        return data_value  
    
    
def compare(input_param, output_path, stack_mode=False, auto_analyze=True, fuzzy_match=False):
    try:
        summary_compare, md5_compare = task_dumppath_get(input_param)
        check_configuration_param(stack_mode, auto_analyze, fuzzy_match)
        create_directory(output_path)
        check_compare_param(input_param, output_path, summary_compare, md5_compare)
    except (CompareException, FileCheckException) as error:
        logger.error('Compare failed. Please check the arguments and do it again!')
        raise CompareException(error.code) from error
    pt_comparator = PTComparator()
    pt_comparator.compare_core(input_param, output_path, stack_mode=stack_mode,
                 auto_analyze=auto_analyze, fuzzy_match=fuzzy_match, summary_compare=summary_compare,
                 md5_compare=md5_compare)
