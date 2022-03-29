import os

data_folder = './data/data1'
solution_file = './solution/solution.txt'

max_qos_config = 'config.ini'
demand_file = 'demand.csv'
qos_file = 'qos.csv'
sitebandwidth_file = 'site_bandwidth.csv'


with open (os.path.join(data_folder, max_qos_config)) as f:
    f.readline()
    max_qos = int(f.readline().split('=')[1])

with open (os.path.join(data_folder, demand_file)) as f:
    # 用户：{时间：demand}
    demands = {}

    # 时间
    times = []
    users = f.readline().rstrip().split(",")

    i = 1
    while(i < len(users)):
        demands[users[i]] = {}
        i = i + 1

    s = f.readlines()
    i = 0
    while(i<len(s)):
        s_ = s[i].rstrip().split(",")
        times.append(s_[0])
        j = 1
        while(j < len(s_)):
            demands[users[j]][s_[0]] = int(s_[j])
            j = j + 1
        i = i + 1


with open (os.path.join(data_folder, qos_file)) as f :
    # 用户：{边缘：qos}
    qos = {}

    users = f.readline().rstrip().split(",")

    i = 1
    while (i< len(users)):
        qos[users[i]] = {}
        i = i + 1

    s = f.readlines()

    i = 0
    while (i < len(s)):
        s_ = s[i].rstrip().split(",")
        j = 1
        while (j < len(s_)):
            qos[users[j]][s_[0]] = int(s_[j])
            j = j + 1
        i = i + 1


with open (os.path.join(data_folder, sitebandwidth_file)) as f :
    sitebandwidth = {}

    f.readline()

    s = f.readlines()

    i = 0
    while(i < len(s)) :
        s_ = s[i].rstrip().split(',')
        sitebandwidth[s_[0]] = int(s_[1])
        i = i + 1


time2index = {}

for i in range(0,len(times)):
    time2index[times[i]] = i


with open(solution_file) as f:

    # {site : {time:fenpei}}
    site_info = {}

    for site_name in sitebandwidth:
        if(site_name not in site_info):
            site_info[site_name] = {}
        for time in times:
            site_info[site_name][time ] = 0

    for time in times:
        # print(time)
        # 用户 ： {节点：资源}
        fenpei_info = {}
        for i in range(1, len(users)):

            s = f.readline()

            if(s == None):
                print('没有处理所有时刻')

            yong_hu, fen_peis = s.strip().split(':')

            value = fen_peis.split(',')
            for j in range(0, len(value), 2):
                if(len(value) >= 2):
                    bian_yuan = value[j].split('<')[-1]
                    fen_pei = int(value[j+1].split('>')[0])
                    if(yong_hu not in fenpei_info) :
                        fenpei_info[yong_hu] = {}
                    if(bian_yuan not in fenpei_info[yong_hu]) :
                        fenpei_info[yong_hu][bian_yuan] = 0

                    fenpei_info[yong_hu][bian_yuan] = fenpei_info[yong_hu][bian_yuan] + fen_pei
                else:
                    if(yong_hu not in fenpei_info) :
                        fenpei_info[yong_hu] = {}

        site_sets = set()
        for yonghu in fenpei_info.keys():
            yonghu_demand = 0
            for bian_yuan in fenpei_info[yonghu]:
                yonghu_demand = yonghu_demand + fenpei_info[yonghu][bian_yuan]
                if bian_yuan not in site_info:
                    site_info[bian_yuan] = {}

                if(time not in site_info[bian_yuan]):
                    site_info[bian_yuan][time] = 0

                if (qos[yonghu][bian_yuan] >= max_qos):
                        print("超过qos上限")

                site_info[bian_yuan][time] = site_info[bian_yuan][time] + fenpei_info[yonghu][bian_yuan]
                site_sets.add(bian_yuan)

            if(yonghu_demand != demands[yonghu][time]) :
                print("用户:" + yonghu)
                print("分配的需求:" + str(yonghu_demand))
                print("实际需求:" + str(demands[yonghu][time]))
                print("用户需求不匹配")

        # print(site_sets)
        # print(site_info)
        for site_name in site_sets:
            if(site_info[site_name][time] > sitebandwidth[site_name]):
                print(site_info[bian_yuan][time])
                print("超过边缘节点带宽上限")

    for site_name in site_info:
        site_info[site_name] = sorted(site_info[site_name].items(), key=lambda x: x[1])


    import math

    score = 0
    for site_name in site_info:
        score = score + site_info[site_name][math.ceil(len(times)*0.95) -1][1]

    print("score:" , score)


    from pyecharts import *

    page = Page()  # 实例化page类
    attr = []
    v1 = []
    v2 = []

    bar = Bar("score:" + str(score) + '\n' +
              'x轴:' + "第t时刻" + '\n' +
              'y轴:' + '带宽' + '\n' +
              '时刻总数:' + str(len(times)) + '\n' +
              'dataset:' + data_folder + '\n' +
               '顺序: 按边缘节点占用时刻总数' + '\n'
              'solution_file:' + solution_file, width=1000,height=200)

    page.add(bar)  # 添加要展示的图表，并设置显示位置

    site_names_timenum_order = {}
    for site_name in site_info:
        for t in site_info[site_name]:
            if(site_name not in site_names_timenum_order):
                site_names_timenum_order[site_name] = 0

            if(t[1] != 0):
                site_names_timenum_order[site_name] = 1 + site_names_timenum_order[site_name]

    site_names_timenum_order = sorted(site_names_timenum_order.items(), key=lambda x: x[1], reverse=True)

    i = 0
    for site in site_names_timenum_order:
        site_name = site[0]
        attr = []
        v1 = []
        v2 = []
        attr = [str(time2index[t[0]]) for t in site_info[site_name]]

        v1 = [t[1] for t in site_info[site_name]]
        v2 = [sitebandwidth[site_name] - t[1] for t in site_info[site_name]]
        bar = Bar( "边缘节点:" + site_name + '\n' +
                  '共' + str(site_names_timenum_order[i][1]) + '时刻有分配' '\n' , title_pos="60%",width=1900)
        bar.add("已用", attr, v1, is_stack=True, xaxis_rotate = 30,xaxis_label_textsize = 8)
        bar.add("剩余", attr, v2, is_stack=True, xaxis_rotate = 30,xaxis_label_textsize = 8)
        page.add(bar)
        i = i + 1

    print("===============")
    import matplotlib.pyplot as plt
    import numpy as np

    plt.figure(figsize=(35,20))

    sitename2index = {}
    print(len(sitebandwidth))
    print(len(times))

    sb = np.empty((len(sitebandwidth),  len(times)))
    sn_i = 0
    for sn in site_info:
        sitename2index[sn] = sn_i
        sn_i = sn_i + 1

    for sn in sitename2index:
        sn_i = sitename2index[sn]
        for t in site_info[sn]:
            t_i = time2index[t[0]]
            v = t[1]
            sb[sn_i][t_i] = v


    sitenames = list(sitename2index.keys())
    times = [time2index[t] for t in time2index.keys()]

    import seaborn as sns

    print(len(sb))
    ax = sns.heatmap(sb, linewidths=0.03, linecolor='white', cbar=True)  # 画热力图

    ax.set_xlabel('times')
    ax.set_ylabel('site_name')
    ax.set_xticklabels(times)
    print(len(sitenames))
    print(len(times))
    ax.set_yticklabels(sitenames, rotation=0)




