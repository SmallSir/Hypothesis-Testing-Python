import pandas as pd
import numpy as np
from scipy.stats import ttest_ind

#将地区按照美国习惯转化成为简写
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}
def get_list_of_university_towns():
    '''将university_towns.txt中的数据进行清洗
        将州后面[]信息删除
        将地区后面的()删除
    '''
    state = None
    state_town = []
    with open('university_towns.txt') as file:
        for  line in file:
            thisline = line[:-1]#每一行的最后一个是一个换行符
            if thisline[-6:] == '[edit]': #如果满足条件则此时的thisline为州
                state = thisline[:-6]
                continue
            if '(' in thisline: #满足条件认定为是地区
                town = thisline[:thisline.index('(')-1]
            else:
                town = thisline
            state_town.append([state,town])
    df = pd.DataFrame(state_town,columns=['State','RegionName'])
    return df


def get_reccession_start():
    '''
    此函数根据资料计算经济衰退开始的时间，返回的值为年限以及季度
    经济衰退的定义是连续三个季度的经济出现下滑，那么第一季度判定为经济衰退的开始时间
    '''
    gdplev = pd.ExcelFile('gdplev.xls')
    gdplev = gdplev.parse('Sheet1',skiprows=219) #选择从219开始的原因是，我们只判断2000年以后的数据
    gdplev = gdplev[['1999q4', 9926.1]] #让查询的目标主停留在规定的两行
    gdplev.columns = ['Quarter','GDP']
    for i in range(2,len(gdplev)):
        if gdplev.iloc[i-2][1] > gdplev.iloc[i-1][1] and gdplev.iloc[i-1][1] > gdplev.iloc[i][1]:
            return gdplev.iloc[i-2][0]


def get_recession_end():
    '''
    该函数根据资料计算经济衰退结束的时间，返回的值为年限以及季度
    经济衰退结束定义是，连续三个季度的经济出现上涨，但是这应该是在经济衰退后的季度时间
    '''
    gdplev = pd.ExcelFile('gdplev.xls')
    gdplev = gdplev.parse('Sheet1', skiprows=219)  # 选择从219开始的原因是，我们只判断2000年以后的数据
    gdplev = gdplev[['1999q4', 9926.1]]  # 让查询的目标主停留在规定的两行
    gdplev.columns = ['Quarter', 'GDP']
    start = get_reccession_start()
    start_index = gdplev[gdplev['Quarter'] == start].index.tolist()[0] #返回值转成列表取第一个
    gdplev = gdplev[start_index:]
    for i in range(2,len(gdplev)):
        if gdplev.iloc[i-2][1] < gdplev.iloc[i-1][1] and gdplev.iloc[i-1][1] < gdplev.iloc[i][1]:
            return gdplev.iloc[i][0]


def get_recession_bottom():
    '''
    此函数根据资料计算出在经济衰退期间最低点是什么时候
    '''
    gdplev = pd.ExcelFile('gdplev.xls')
    gdplev = gdplev.parse("Sheet1", skiprows=219)
    gdplev = gdplev[['1999q4', 9926.1]]
    gdplev.columns = ['Quarter','GDP']
    start = get_reccession_start()
    start_index  = gdplev[gdplev['Quarter'] == start].index.tolist()[0]
    end = get_recession_end()
    end_index  = gdplev[gdplev['Quarter'] == end].index.tolist()[0]
    gdplev = gdplev[start_index:end_index+1]
    bottom = gdplev['GDP'].min()
    bottom_index = gdplev[gdplev['GDP'] == bottom].index.tolist()[0]-start_index
    return gdplev.iloc[bottom_index]['Quarter']

def new_col_name():
    '''
    该函数主要是新的行名
    '''
    years = list(range(2000,2017))
    quars = ['q1','q2','q3','q4']
    quars_year = []
    for i in years:
        for x in quars:
            quars_year.append((str(i) + x))
    return quars_year[:67] #按照要求返回2000q1到2016q3的值
def convert_housing_data_to_quarters():
    '''
    该函数是将住房数据转换为并其作为平均值返回，只要2000q1到20016q3的列，同时只留下
    国家和地区名称
    其中平均值按照每个季度所包括的月份获得
    '''
    data = pd.read_csv('City_Zhvi_AllHomes.csv')
    data.drop(['Metro', 'CountyName', 'RegionID', 'SizeRank'], axis=1, inplace=True)
    data['State'] = data['State'].map(states)
    data.set_index(['State','RegionName'],inplace=True)
    col = list(data.columns)
    col = col[0:45] #删除多于不需要的数据
    data.drop(col,axis=1,inplace = True)
    qs = [list(data.columns)[x:x + 3] for x in range(0, len(list(data.columns)), 3)]#获得每个季度所包括的月份
    column_names = new_col_name()
    for col, q in zip(column_names, qs):
        data[col] = data[q].mean(axis=1) #季度与所设计的月份对应

    data = data[column_names]
    return data

def run_ttest():
    data = convert_housing_data_to_quarters().copy() #获得每个季度的平均值
    data = data.loc[:, get_reccession_start():get_recession_bottom()]#获取在经济衰退至底部的平均值
    data = data.reset_index()
    def price_ratio(row):
        return (row[get_reccession_start()] - row[get_recession_bottom()]) / row[get_reccession_start()]
    data['up&down'] = data.apply(price_ratio, axis=1)
    uni_town = get_list_of_university_towns()['RegionName']
    uni_town = set(uni_town)
    def is_uni_town(row):
        if row['RegionName'] in uni_town:
            return 1
        else:
            return 0
    data['is_uni'] = data.apply(is_uni_town, axis=1)
    not_uni = data[data['is_uni'] == 0].loc[:, 'up&down'].dropna()
    is_uni = data[data['is_uni'] == 1].loc[:, 'up&down'].dropna()
    def better():
        if not_uni.mean() < is_uni.mean():
            return 'non-university town'
        else:
            return 'university town'
    p_val = list(ttest_ind(not_uni, is_uni))[1]
    result = (True, p_val, better())
    return result
if __name__ == '__main__':
    print(run_ttest())