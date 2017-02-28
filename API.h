//
// Created by wangnan on 1/4/17.
//
#ifndef RELIA_API_H
#define RELIA_API_H

#include <Python.h>
#include "Type.h"
#include <vector>
#include <string>
void *create_petri_net(PyObject *wrap_context_func);

void delete_petri_net(void *pn_ptr);

unsigned int add_transition(void *pn_ptr, int pytype, /*0 for imme, 1 for exp*/
                            PyObject *pyguard_func,
                            double pyparam, PyObject *pyparam_func,
                            unsigned int priority) throw(Exception);

void add_arc(void *pn_ptr, int arc_type, /*0 for in, 1 for out, 2 for inhibitor*/
             unsigned int trans_index, unsigned int place_index,
             unsigned int pymulti, PyObject *pymulti_func) throw(Exception);

void set_init_token(void *pn_ptr, unsigned int place_index, unsigned int token_num);


void solve_steady_state(void *pn_ptr) throw(Exception);

void solve_transient_state(void *pn_ptr, double time) throw(Exception);


unsigned int get_token_num(PyObject *wrapped_context, unsigned int place_index);

bool is_trans_enabled(PyObject *wrapped_context, unsigned int trans_index);

bool has_enbaled_trans(PyObject *wrapped_context);

void option_set_ss_method(void *pn_ptr, int method);

void option_set_ts_method(void *pn_ptr, int method);

void option_set_sor_omega(void *pn_ptr, double omega);

void option_set_max_iter(void *pn_ptr, unsigned int iter);

void option_set_precision(void *pn_ptr, double prec);

void config_logger(void *pn_ptr, const char *file);

void set_halt_condition(void *pn_ptr, PyObject *halt_cond_func) throw(Exception);

unsigned int add_inst_reward(void *pn_ptr, PyObject *pyreward_func) throw(Exception);
unsigned int add_cum_reward(void *pn_ptr, PyObject *pyreward_func) throw(Exception);
double get_inst_reward(void *pn_ptr, unsigned int reward_index);
double get_cum_reward(void *pn_ptr, unsigned int reward_index);


std::string fire_transition(void *pn_ptr, unsigned int trans_index, const std::string& marking);
bool is_trans_enabled_in_marking(void *pn_ptr, unsigned int trans_index, const std::string& marking);
std::string export_petri_net(void *pn_ptr);
std::string export_init_marking(void *pn_ptr);

double get_acyclic_mtta(void *pn_ptr);


#endif //RELIA_API_H
