//
// Created by wangnan on 1/4/17.
//
#ifndef RELIA_API_H
#define RELIA_API_H
#include <Python.h>



void *create_petri_net(PyObject *wrap_context_func);
void delete_petri_net(void *pn_ptr);
unsigned int add_transition(void *pn_ptr, int pytype, /*0 for imme, 1 for exp*/
                            PyObject *pyguard_func,
                            double pyparam, PyObject *pyparam_func,
                            unsigned int priority);

void add_arc(void *pn_ptr, int arc_type, /*0 for in, 1 for out, 2 for inhibitor*/
             unsigned int trans_index, unsigned int place_index,
             unsigned int pymulti, PyObject *pymulti_func);

void set_init_token(void *pn_ptr, unsigned int place_index, unsigned int token_num);
unsigned int add_inst_reward(void *pn_ptr, PyObject* pyreward_func);
bool solve_steady_state(void *pn_ptr);
double get_inst_reward(void *pn_ptr, unsigned int reward_index);
unsigned int get_token_num(PyObject* wrapped_context, unsigned int place_index);
bool is_trans_enabled(PyObject* wrapped_context, unsigned int trans_index);
bool has_enbaled_trans(PyObject* wrapped_context);
#endif //RELIA_API_H
