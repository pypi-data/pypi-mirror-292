import os
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

def set_chinese_font():
    """
    ubuntu system:
    sudo apt-get install fonts-wqy-zenhei
    sudo apt-get install fonts-noto-cjk

    """
    import platform
    from matplotlib.font_manager import FontProperties
    # if os.name == 'posix':
    #     plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
    #     plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
    # elif os.name == 'nt':
    #     plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
    #     plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
    system = platform.system()
    if system == 'Windows':
        font_path = 'C:/Windows/Fonts/simhei.ttf'  # 黑体字体路径
        if os.path.exists(font_path):
            font_prop = FontProperties(fname=font_path)
            plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
            plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
        else:
            raise FileNotFoundError("SimHei 字体未找到，请安装该字体或修改为其他已安装的中文字体")
    elif system == 'Linux':
        font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
        if os.path.exists(font_path):
            font_prop = FontProperties(fname=font_path)
            plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
            plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
        else:
            raise FileNotFoundError("Noto Sans CJK 字体未找到，请安装该字体或修改为其他已安装的中文字体")
    else:
        raise EnvironmentError("不支持的操作系统")


def reduce_mem_usage(df):
    """
    reduce_mem_usage 函数通过调整数据类型，帮助我们减少数据在内存中占用的空间，需要先做数据预处理，EDA，最终才能够对数据进行减少内存的方式，为的是方便后期的处理
    iterate through all the columns of a dataframe and modify the data type to reduce memory usage.
    """
    start_mem = df.memory_usage().sum() / 1024 ** 2
    print('Memory usage of dataframe is {:.2f} MB'.format(start_mem))

    for col in df.columns:
        col_type = df[col].dtype

        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
        else:
            df[col] = df[col].astype('category')

    end_mem = df.memory_usage().sum() / 1024 ** 2
    print('Memory usage after optimization is: {:.2f} MB'.format(end_mem))
    print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem) / start_mem))
    return df

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
data_dir = os.path.join(parent_dir, "data")  # 给全局变量data_dir赋值

def initialize_sys_path():
    """
    设置Python模块搜索路径，确保当前脚本的父目录和模块目录被包含在内。
    """
    # 获取当前文件的目录
    current_dir = os.path.dirname(__file__)
    # 获取当前文件的父目录
    parent_dir = os.path.dirname(current_dir)
    data_dir = os.path.join(parent_dir, "data")
    
    # 确保父目录在sys.path中
    # TODO 将父路径切换成项目根路径识别并添加到sys搜索路径当中
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    if data_dir not in sys.path:
        sys.path.insert(0, data_dir)
        
    # 定义模块目录路径
    module_dir = os.path.join(parent_dir, "module")
    
    # 确保模块目录在sys.path中
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
    
    # 打印当前的sys.path，用于调试
    print("Running test package initialization")
    print(sys.path)


if __name__ == "__main__":
    # 调用初始化函数
    initialize_sys_path()