# -*- coding: utf-8 -*-
"""
Authors: Hung-Hsin Chen <chenhh@par.cse.nsysu.edu.tw>
License: GPL v2
"""
import platform
import numpy as np
import pandas as pd
from datetime import date
import time
import glob
import os
from PySPPortfolio.pysp_portfolio import *
from exp_cvar import (run_min_ms_cvar_eventsp_simulation,
                      run_min_cvar_sp2_yearly_simulation,
                      run_min_cvar_sip2_yearly_simulation)
from gen_results import (retry_read_pickle, retry_write_pickle)


def get_results_dir(prob_type):
    """
    Parameter:
    ----------------
    prob_type: str, {min_cvar_sp, min_cvar_sip}

    Returns:
    ----------------
    return the results directory of given problem type
    """
    if prob_type in ("min_ms_cvar_eventsp", "min_cvar_sp2_yearly",
                     "min_cvar_sip2_yearly",):
        return os.path.join(EXP_SP_PORTFOLIO_DIR, prob_type)
    else:
        raise ValueError("unknown prob_type: {}".format(prob_type))


def get_year_pairs():
    """
    month pairs from 2005 to 2014
    """

    # roi_path = os.path.join(SYMBOLS_PKL_DIR,
    #                         'TAIEX_2005_largest50cap_panel.pkl')
    # if not os.path.exists(roi_path):
    #     raise ValueError("{} roi panel does not exist.".format(roi_path))
    #
    # # shape: (n_period, n_stock, {'simple_roi', 'close_price'})
    # roi_panel = pd.read_pickle(roi_path)
    #
    # # shape: (n_period, n_stock)
    # exp_rois = roi_panel.loc[START_DATE:END_DATE]
    #
    # year_pairs = []
    # for year in xrange(2005, 2014 + 1):
    #     start, end = date(year, 1, 1), date(year, 12, 31)
    #     dates = exp_rois.loc[start:end].items
    #     year_pairs.append((dates[0].to_datetime().date(),
    #                             dates[-1].to_datetime().date()))
    #
    # data =pd.to_pickle(year_pairs, os.path.join(TMP_DIR,
    #                                             'exp_dates_yearly.pkl'))
    year_pairs = pd.read_pickle(os.path.join(DATA_DIR,
                                              'exp_dates_yearly.pkl'))

    return year_pairs


def all_experiment_parameters(prob_type, max_scenario_cnts):
    """
    file_name of all experiment parameters
    (n_stock, win_length, n_scenario, bias, cnt, alpha, start_date, end_date)
    """
    if prob_type in ("min_ms_cvar_eventsp",):
        days = range(50, 240+10, 10)
        alphas = ["0.50", "0.60", "0.70", "0.80", "0.90"]
    elif prob_type in ("min_cvar_sp2_yearly",):
        days = range(50, 240+10, 10)
        alphas = ["0.50", "0.60", "0.70", "0.80", "0.90",
                  "0.55", "0.65", "0.75", "0.85", "0.95"]
    elif prob_type in ("min_cvar_sip2_yearly",):
        days = range(60, 240+10, 10)
        alphas = ["0.50", "0.60", "0.70", "0.80", "0.90",
                  "0.55", "0.65", "0.75", "0.85", "0.95"]

    all_params = []
    for pair in get_year_pairs():
        for day in days:
            for alpha in alphas:
                for cnt in xrange(1, max_scenario_cnts + 1):
                    all_params.append((5, day, 200, "unbiased", cnt, alpha,
                               pair[0], pair[1]))
    return set(all_params)


def checking_finished_parameters(prob_type, max_scenario_cnts):
    """
    return unfinished experiment parameters.
    "min_ms_cvar_eventsp_20070702_20070731_m5_w120_s200_unbiased_1_a0.50.pkl"
    ['min', 'ms', 'cvar', 'eventsp', '20070702', '20070731', 'm5', 'w120',
    's200', 'unbiased', '1', 'a0.50.pkl']

    """
    dir_path = get_results_dir(prob_type)

    # get all params
    all_params = all_experiment_parameters(prob_type, max_scenario_cnts)

    if prob_type in ("min_ms_cvar_eventsp", "min_cvar_sp2_yearly",
                     "min_cvar_sip2_yearly",):
        # min_ms_cvar_eventsp_20050103_20050105_m5_w70_s200_unbiased_1_a0.95
        # min_cvar_sp2_yearly_20050103_20050105_m5_w70_s200_unbiased_1_a0.95
        pkls = glob.glob(os.path.join(dir_path, "{}_20*.pkl".format(
            prob_type)))

    for pkl in pkls:
        name = pkl[pkl.rfind(os.sep) + 1: pkl.rfind('.')]
        exp_params = name.split('_')
        if prob_type in ("min_ms_cvar_eventsp", "min_cvar_sp2_yearly"):
            d1, d2 = exp_params[4], exp_params[5]
            params = exp_params[6:]
            start_date = date(int(d1[:4]), int(d1[4:6]), int(d1[6:8]))
            end_date = date(int(d2[:4]), int(d2[4:6]), int(d2[6:8]))
        elif prob_type in ("min_cvar_sip2_yearly",):
            d1, d2 = exp_params[4], exp_params[5]
            params = exp_params[7:]
            start_date = date(int(d1[:4]), int(d1[4:6]), int(d1[6:8]))
            end_date = date(int(d2[:4]), int(d2[4:6]), int(d2[6:8]))

        n_stock = int(params[0][params[0].rfind('m') + 1:])
        win_length = int(params[1][params[1].rfind('w') + 1:])
        n_scenario = int(params[2][params[2].rfind('s') + 1:])
        bias = params[3]
        scenario_cnt = int(params[4])
        alpha = params[5][params[5].rfind('a') + 1:]

        data_param = (n_stock, win_length, n_scenario, bias, scenario_cnt,
                      alpha, start_date, end_date)
        # print all_params
        if data_param in all_params:
            all_params.remove(data_param)

    # return unfinished params
    return all_params

def checking_working_parameters(prob_type, max_scenario_cnts, retry_cnt=5):
    """
    if a parameter is under working and not write to pkl,
    it is recorded to a file

    working dict:
        - key: str,  "|".join(str(v) for v in param)
        - value: machine node
    """
    dir_path = get_results_dir(prob_type)
    log_file = '{}_working.pkl'.format(prob_type)

    # get all params
    all_params = all_experiment_parameters(prob_type, max_scenario_cnts)

    # storing a dict, key: param, value: platform_name
    file_path = os.path.join(dir_path, log_file)
    if not os.path.exists(file_path):
        # no working parameters
        print ("{} no working log file.".format(prob_type))
        return all_params

    data = retry_read_pickle(file_path)
    for param_key, node in data.items():
        # key:  (n_stock, win_length, _scenario, biased, cnt, alpha, start_date,
        # end_date)
        keys = param_key.split('|')

        param = (int(keys[0]), int(keys[1]), int(keys[2]), keys[3],
                 int(keys[4]), keys[5],
                 date(*map(lambda x:int(x), keys[6].split('-'))),
                 date(*map(lambda x: int(x), keys[7].split('-'))))
        if param in all_params:
            all_params.remove(param)
            print ("working {}: {} is running on {}.".format(
                prob_type, param, node))
    print ("#. of running parameters: {}".format(len(data)))

    # unfinished params
    return all_params


def dispatch_experiment_parameters(prob_type, max_scenario_cnts):
    dir_path = get_results_dir(prob_type)

    # storing a dict, {key: param, value: platform_name}
    log_file = '{}_working.pkl'.format(prob_type)

    # reading working pkl
    log_path = os.path.join(dir_path, log_file)
    params1 = checking_finished_parameters(prob_type, max_scenario_cnts)
    params2 = checking_working_parameters(prob_type, max_scenario_cnts)
    unfinished_params = params1.intersection(params2)

    print ("dispatch: {}, #. unfinished parameters: {}".format(
        prob_type, len(unfinished_params)))

    while len(unfinished_params) > 0:
        # each loop we have to
        params1 = checking_finished_parameters(prob_type, max_scenario_cnts)
        params2 = checking_working_parameters(prob_type, max_scenario_cnts)
        unfinished_params = params1.intersection(params2)

        print ("dispatch: {}, current #. of unfinished parameters: {}".format(
            prob_type, len(unfinished_params)))

        # if len(unfinished_params) <= 100:
        #     for u_param in unfinished_params:
        #         print ("unfinished: {}".format(u_param))

        param = unfinished_params.pop()
        n_stock, win_length, n_scenario, bias, cnt, alpha, start_date, \
        end_date = param
        alpha = float(alpha)
        bias = True if bias == "biased" else False

        # log  parameter to file
        if not os.path.exists(log_path):
            working_dict = {}
        else:
            working_dict = retry_read_pickle(log_path)

        param_key = "|".join(str(v) for v in param)
        working_dict[param_key] = platform.node()
        retry_write_pickle(working_dict, log_path)

        # run experiment
        try:
            if prob_type == "min_ms_cvar_eventsp":
                run_min_ms_cvar_eventsp_simulation(
                    n_stock, win_length, n_scenario, bias, cnt, alpha,
                    start_date=start_date, end_date=end_date,
                    solver_io='lp')
            elif prob_type == "min_cvar_sp2_yearly":
                run_min_cvar_sp2_yearly_simulation(
                    n_stock, win_length, n_scenario, bias, cnt, alpha,
                    start_date=start_date, end_date=end_date,
                    )
            elif prob_type == "min_cvar_sip2_yearly":
                run_min_cvar_sip2_yearly_simulation(
                    n_stock, win_length, n_scenario, bias, cnt, alpha,
                    start_date=start_date, end_date=end_date,
                )
        except Exception as e:
            print ("dispatch: run experiment:", param, e)
        finally:
            working_dict = retry_read_pickle(log_path)
            if param_key in working_dict.keys():
                del working_dict[param_key]
            else:
                print ("dispatch: can't find {} in working dict.".format(
                    param_key))
            retry_write_pickle(working_dict, log_path)


if __name__ == '__main__':
    # print get_year_pairs()
    # print len(all_experiment_parameters("min_ms_cvar_eventsp", 1))
    # res = checking_finished_parameters("min_ms_cvar_eventsp", 1)
    # checking_working_parameters("min_ms_cvar_eventsp", 1)
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--prob_type", required=True, type=str)
    parser.add_argument("-c", "--max_scenario_cnt", required=True, type=int)
    args = parser.parse_args()
    dispatch_experiment_parameters(args.prob_type, args.max_scenario_cnt)
