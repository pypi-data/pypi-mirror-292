# **溢出解析工具**

针对训练过程中的溢出检测场景（当《[精度数据采集](./dump.md)》开启溢出检测dump时），对于输入正常但输出存在溢出的API，会在训练执行目录下将溢出的API信息按照前向和反向分类，dump并保存为`dump.json`，前向过程溢出的API可通过该工具对`dump.json`进行解析，输出溢出API为正常溢出还是非正常溢出，从而帮助用户快速判断。

工具支持PyTorch版本：1.11/2.0/2.1/2.2。

操作步骤如下：

1. 安装工具。

   详见《[MindStudio精度调试工具](../../README.md)》的“工具安装”章节。

2. 执行溢出API解析操作。

   ```bash
   msprobe -f pytorch run_overflow_check -api_info ./dump.json
   ```
   
| 参数名称                   | 说明                                               | 是否必选 |
| -------------------------- | -------------------------------------------------- | -------- |
| -api_info或--api_info_file | 指定API信息文件dump.json。                         | 是       |
| -j或--jit_compile          | 开启jit编译。                                      | 否       |
| -d或--device               | 指定Device ID，选择UT代码运行所在的卡，默认值为0。 | 否       |

反向过程溢出的API暂不支持该功能。
