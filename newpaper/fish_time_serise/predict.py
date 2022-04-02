alabama_university_time_series = [13055, 13563, 13867, 14696, 15460, 15311, 15603,
                                  15861, 16807, 16919, 16388, 15433, 15497, 15145,
                                  15163, 15984, 16859, 18150, 18970, 19328, 19337,
                                  18876]


def fetch_fuzzy_class(val, u_v):
    """
    模糊化，输入val真实值，添加模糊值
    :param val:时间序列真实值
    :param u_v:论域划分情况 如[(13000, 14000), (14000, 15000), (15000, 16000), (16000, 17000), (17000, 18000), (18000, 19000), (19000, 20000)]
    :return:糊逻辑关系组，如13055对应(13000，14000)，返回{'actual_data': 13055, 'fuzzy_class': 0}
    """
    for u_min, u_max in u_v:
        if u_min <= val <= u_max:
            dict_object = {'actual_data': val, 'fuzzy_class': u_v.index((u_min, u_max))}
            return dict_object


def lunyumid(val, u_v):
    """
    获取论域区间中点
    :param val: 真实值 {'actual_data': val, 'fuzzy_class': class)}
    :param u_v: 划分论域 列表形式 [(),()]
    :return:
    """
    for u_min, u_max in u_v:
        if u_min <= val <= u_max:
            return 0.5 * (u_min + u_max)


def fetch_fuzzy_relations(val1, val2, historical_relations_fuzzy):
    """
    建立模糊逻辑关系
    :param val1: 历史t-2模糊值 class1
    :param val2: 历史t-1模糊值 'fuzzy_class': class2
    :param historical_relations_fuzzy: 2阶模糊关系序列及对应值 [(At-2, At-1, At, At_actual_data)]
    :return: 返回满足（class1，class2）的序列
    """
    r_list = []
    for i in range(len(historical_relations_fuzzy) - 1):
        if historical_relations_fuzzy[i][0] == val1 and historical_relations_fuzzy[i][1] == val2:
            # print(fuzzy_relation_vector[i])
            r_list.append(historical_relations_fuzzy[i])
    return r_list


def mv_predict(historical_data_fuzzied, historical_relations_fuzzy, u_vectorized):
    """
    mv预测方法 f(t) = (w*m(t1) + m(t2) + ……  + m(t_lamda)) / (w + t_lamda - 1) 前lamda年对应模糊区间中点
    :return:
    """
    w = 1.5  # 太大了就差不多是t-1的值了
    mv_forecasted = []
    for j in range(1, len(historical_data_fuzzied) - 1):
        val1 = historical_data_fuzzied[j - 1]
        val2 = historical_data_fuzzied[j]  # 所有的模糊逻辑 {'actual_data': 13055, 'fuzzy_class': 0}
        # val1 = historical_data_fuzzied[j - 1]
        # val2 = historical_data_fuzzied[j - 2].get('actual_data')

        _r_list = fetch_fuzzy_relations(val1.get('fuzzy_class'), val2.get('fuzzy_class'), historical_relations_fuzzy)
        # val:  0  r_list:  [(0, 0, 0,data), (0, 0, 1,data)]
        mv_forecasted.append((w * lunyumid(val2.get('actual_data'), u_vectorized) +
                              lunyumid(val1.get('actual_data'), u_vectorized)) / (w + 1))
        # historical_data_fuzzied[j + 1]["mv_forecasted"] = ((w * lunyumid(val2.get('actual_data'), u_vectorized) +
        #                                                     lunyumid(val1.get('actual_data'), u_vectorized)) / (w + 1))
    return mv_forecasted


def EBN_predict(historical_data_fuzzied, historical_relations_fuzzy, u_vectorized):
    """

    :param historical_data_fuzzied:
    :param historical_relations_fuzzy:
    :param u_vectorized:
    :return:
    """
    EBN_forecasted = []
    for j in range(1, len(historical_data_fuzzied) - 1):
        val1 = historical_data_fuzzied[j - 1]
        val2 = historical_data_fuzzied[j]  # 所有的模糊逻辑 {'actual_data': 13055, 'fuzzy_class': 0}
        _r_list = fetch_fuzzy_relations(val1.get('fuzzy_class'), val2.get('fuzzy_class'), historical_relations_fuzzy)
        _sum = 0.0
        # if len(_r_list):
        for i in range(len(_r_list)):  # 遍历所有模糊关系组
            _sum += (u_vectorized[_r_list[i][-2]][0] + u_vectorized[_r_list[i][-2]][1]) / 4  # 所在模糊区间的中点的一半
            sub = u_vectorized[_r_list[i][-2]]
            val3 = _r_list[i][-1]
            sub = (sub[0], sub[0] + (sub[1] - sub[0]) / 3, sub[0] + (sub[1] - sub[0]) * 2 / 3, sub[1])  # 三等分的模糊区间

            for k in range(len(sub) - 1):
                if sub[k] <= val3 <= sub[k + 1]:
                    _sum += (sub[k] + sub[k + 1]) / 4

        _sum /= len(_r_list)
        # else:
        #     _sum = 0.5 * (val1.get('actual_data') + val2.get('actual_data'))
        EBN_forecasted.append(_sum)
        # historical_data_fuzzied[j + 1]["EBN_forecasted"] = _sum
    return EBN_forecasted


def fuzzyset_predict(historical_data_fuzzied, historical_relations_fuzzy, u_vectorized):
    """

    :return:
    """
    fuzzyset_forecasted = []
    for j in range(1, len(historical_data_fuzzied) - 1):
        val1 = historical_data_fuzzied[j - 1]
        val2 = historical_data_fuzzied[j]  # 所有的模糊逻辑 {'actual_data': 13055, 'fuzzy_class': 0}
        _r_list = fetch_fuzzy_relations(val1.get('fuzzy_class'), val2.get('fuzzy_class'), historical_relations_fuzzy)
        _sum = 0.0
        if len(_r_list):
            for i in range(len(_r_list)):
                _sum += (u_vectorized[_r_list[i][2]][0] + u_vectorized[_r_list[i][2]][1]) * 0.5
            _sum /= len(_r_list)
            fuzzyset_forecasted.append(_sum)
            # historical_data_fuzzied[j + 1]["fuzzyset_forecasted"] = _sum
        else:
            i = val2.get('fuzzy_class')
            fuzzyset_forecasted.append(0.5 * (u_vectorized[i][0] + u_vectorized[i][1]))
            # historical_data_fuzzied[j + 1]["fuzzyset_forecasted"] = 0.5 * (u_vectorized[i][0] + u_vectorized[i][1])

        # val1 = historical_data_fuzzied[j - 1]
        # val2 = historical_data_fuzzied[j - 2].get('actual_data')
        # val2 = alabama_university_time_series[j - 2]
        # _r_list = fetch_fuzzy_relations(val.get('fuzzy_class'), historical_relations_fuzzy)
        # # val:  0  r_list:  [(0, 0, 0), (0, 0, 1), (0, 1, 2)]
        # fuzzyset_forecasted.append((w * val1.get('actual_data') + lunyumid(val2, u_vectorized)) / (w + 1))
    return fuzzyset_forecasted


def MSE(target, prediction):
    error = []
    for i in range(0, len(prediction) - 0):
        error.append(target[i] - prediction[i])
    # print("errors: ", error)
    squaredError = []
    absError = []
    for val in error:
        squaredError.append(val * val)  # target-prediction之差平方
        absError.append(abs(val))  # 误差绝对值
    print(len(error))

    # print("Square Error: ", squaredError)
    # print("Absolute Value of Error: ", absError)
    # print("MSE = ", sum(squaredError) / len(squaredError))  # 均方误差MSE
    # print("RMSE = ", math.sqrt(sum(squaredError) / len(squaredError)))  # 均方根误差RMSE
    # print("MAE = ", sum(absError) / len(absError))  # 平均绝对误差MAE
    # targetDeviation = []
    # targetMean = sum(target) / len(target)  # target平均值
    # for val in target:
    #     targetDeviation.append((val - targetMean) * (val - targetMean))
    # print("Target Variance = ", sum(targetDeviation) / len(targetDeviation))  # 方差
    #
    # print("Target Standard Deviation = ", math.sqrt(sum(targetDeviation) / len(targetDeviation)))  # 标准差

    mes = sum(squaredError) / len(squaredError)
    return mes
