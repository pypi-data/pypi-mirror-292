#我的代码运行在jupyter lab中，所以不要使用print输出数据，

USER_PYTHON_PROMPT = '''
    {user_input}
    我已经写好开始的代码：
    import openpyxl
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    workbook = openpyxl.load_workbook({filename})
    active_sheet = workbook.active
    df = pd.DataFrame(active_sheet.values)
    df.columns = df.iloc[0]
    df = df[1:]
    需要分析的数据已经保存在df中，请在已经写好的代码基础上续写代码, 请只写一段代码，
    如果输出是数据集，放置在名为output_df的DataFrame，使用print语句输出，不要输出结果到文件
    如果输出是图表，使用plt保存到合适的png文件中
'''

USER_FORMULAR_PROMPT = '''
    {user_input}
    请给出可以直接在execl中计算的公式
'''

USER_SUGGESTION_PROMPT = '''
    {user_input}
    请给出详细的分析步骤，但是不需要python代码
'''

USER_OP_PROMPT = '''
    {user_input}
    请把我当初excel初学者，不要给我任何代码，给完成上述要求的详细分步操作
'''

INITIAL_PYTHON_PROMPT = '''
    你是一名python数据分析师，指导我使用python对excel文件{filename}进行分析,
    我要分析的excel，读入dataframe，df.describe() 的输出是，
    {data_profile}
'''

INITIAL_FORMULAR_PROMPT = '''
    你是一名excel专家，指导我书写公式对excel进行计算,公式必须可以直接在excel中运行
    我要分析的excel，读入dataframe，df.describe() 的输出是，
    {data_profile}

    下面请按照我的要求给出excel公式进行数据计算
'''

INITIAL_SUGGESTION_PROMPT = '''
    你是一名数据分析员，指导我针对目标对excel进行分析，请直接给我分析的思路，
    我要分析的excel，读入dataframe，df.describe() 的输出是，
    {data_profile}
    下面请按照我的目标给出对excel进行分析的思路，注意不要给出python代码，给出思路即可
'''

INITIAL_OP_PROMPT = '''
    你是一个EXCEL高手，指导我操作excel
    我要分析的excel，读入dataframe，df.describe() 的输出是，
    {data_profile}
'''

USER_DESC_PROMPT = '''
    excel各列的数据情况如下所述：
    {user_desc}
'''