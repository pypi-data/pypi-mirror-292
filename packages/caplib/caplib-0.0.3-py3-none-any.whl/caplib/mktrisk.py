# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 14:47:26 2022

@author: dingq
"""
from caplibproto.dqproto import *

from caplib.processrequest import * 

#Calculate Change of Risk Factors
def calculate_risk_factor_change(risk_factor_values, change_type):
    '''
    Calculate the change of risk factor from one time to the other.

    Parameters
    ----------
    risk_factor_values : TYPE
        DESCRIPTION.
    change_type : TYPE
        DESCRIPTION.

    Raises
    ------
    Exception
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    '''
    p_type = RiskFactorChangeType.DESCRIPTOR.values_by_name[change_type.upper()].number 
    p_samples = list(risk_factor_values)
    pb_input = dqCreateProtoRiskFactorChangeCalculationInput(p_type, p_samples)
    req_name = 'RISK_FACTOR_CHANGE_CALCULATOR'
    res_msg = ProcessRequest(req_name, pb_input.SerializeToString())
    pb_output = RiskFactorChangeCalculationOutput()
    pb_output.ParseFromString(res_msg)        
    if pb_output.success == False:
        raise Exception(pb_output.err_msg)   
    return pb_output.result

#Simulate Risk Factors
def simulate_risk_factor(risk_factor_changes, change_type, base):
    '''
    Simulate scenarios for a risk factor given its historical changes and current value.

    Parameters
    ----------
    risk_factor_changes : TYPE
        DESCRIPTION.
    change_type : TYPE
        DESCRIPTION.
    base : TYPE
        DESCRIPTION.

    Raises
    ------
    Exception
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    '''
    p_type = RiskFactorChangeType.DESCRIPTOR.values_by_name[change_type.upper()].number 
    p_changes = list(risk_factor_values)
    p_base = float(base)
    pb_input = dqCreateProtoRiskFactorSimulationInput(p_type, p_changes, p_base)    
    req_name = 'RISK_FACTOR_SIMULATOR'
    res_msg = ProcessRequest(req_name, pb_input.SerializeToString()) 
    pb_output = RiskFactorSimulationOutput()
    pb_output.ParseFromString(res_msg)           
    if pb_output.success == False:
        raise Exception(pb_output.err_msg)
    return pb_output.result
    
#Expected Shortfall
def calculate_expected_shortfall(pnls, prob, mirror):
    '''
    Calculate the expected shortfall from a distribution of PnLs.

    Parameters
    ----------
    pnls : TYPE
        DESCRIPTION.
    prob : TYPE
        DESCRIPTION.
    mirror : TYPE
        DESCRIPTION.

    Raises
    ------
    Exception
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.
    TYPE
        DESCRIPTION.

    '''
    p_profit_loss_samples = dqCreateProtoVector(list(pnls))
    p_probability = float(prob)
    p_calc_es_mirrored = bool(mirror)
    pb_input = dqCreateProtoCalculateExpectedShortfallInput(p_profit_loss_samples, 
                                                            p_probability, 
                                                            p_calc_es_mirrored)
    req_name = 'CALCULATE_EXPECTED_SHORT_FALL'
    res_msg = ProcessRequest(req_name, pb_input.SerializeToString())  
    pb_output = CalculateExpectedShortfallOutput()
    pb_output.ParseFromString(res_msg)           
    if pb_output.success == False:
        raise Exception(pb_output.err_msg)
    return pb_output.expected_shortfall, pb_output.expected_shortfall_mirrored

#Value At Risk
def calculate_value_at_risk(pnls, prob, mirror):
    '''
    Calculate the value at risk (VaR) from a distribution of PnLs.

    Parameters
    ----------
    pnls : TYPE
        DESCRIPTION.
    prob : TYPE
        DESCRIPTION.
    mirror : TYPE
        DESCRIPTION.

    Raises
    ------
    Exception
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.
    TYPE
        DESCRIPTION.

    '''    
    p_profit_loss_samples = dqCreateProtoVector(list(pnls))    
    p_probability = float(prob)
    p_calc_var_mirrored = bool(mirror)
    pb_input = dqCreateProtoCalculateValueAtRiskInput(p_profit_loss_samples, 
                                                      p_probability, 
                                                      p_calc_var_mirrored)
    req_name = 'CALCULATE_VALUE_AT_RISK'
    res_msg = ProcessRequest(req_name, pb_input.SerializeToString())   
    pb_output = CalculateValueAtRiskOutput()
    pb_output.ParseFromString(res_msg)           
    if pb_output.success == False:
        raise Exception(pb_output.err_msg)
    return pb_output.value_at_risk, pb_output.value_at_risk_mirrored