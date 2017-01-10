//

// Created by wangnan on 1/4/17.
//
#include "API.h"
#include "PetriNet.h"
#include <iostream>
#include "PetriNetSolution.h"

void *create_petri_net(PyObject *wrap_context_func)
{
    PetriNetSolution *pn = new PetriNetSolution();
    Py_INCREF(wrap_context_func);
    pn->tag = wrap_context_func;
    return pn;
}

void delete_petri_net(void *pn_ptr)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    PyObject *wrap_context_func = (PyObject *) pn->tag;
    Py_DECREF(wrap_context_func);
    delete pn;
}


template<typename T>
T ConvertBasicTypeFromPy(PyObject *obj);

template<>
double ConvertBasicTypeFromPy(PyObject *obj)
{
    if (PyLong_CheckExact(obj))
    {
        return PyLong_AsDouble(obj);
    }else if (PyFloat_CheckExact(obj))
    {
        return PyFloat_AsDouble(obj);
    }
    throw Exception("Error. Expecting a Float value from callback function.");
}

template<>
bool ConvertBasicTypeFromPy(PyObject *obj)
{
    if(PyBool_Check(obj))
    {
        return PyObject_IsTrue(obj);
    }
    throw Exception("Error. Expecting a Bool value from callback function.");
}

template<>
unsigned int ConvertBasicTypeFromPy(PyObject *obj)
{
    if(PyLong_CheckExact(obj))
    {
        return PyLong_AsUnsignedLong(obj);
    }
    throw Exception("Error. Expecting a Integer value from callback function.");
}

template<typename RetType>
class PyCallBack
{
    PyObject *callback_func;
    PyObject *wrap_context_func;
public:
    PyCallBack() = delete;

    PyCallBack(const PyCallBack &other)
    {
        callback_func = other.callback_func;
        wrap_context_func = other.wrap_context_func;
        Py_INCREF(callback_func);
        Py_INCREF(wrap_context_func);
    }

    PyCallBack(PyCallBack &&other)
    {
        callback_func = other.callback_func;
        wrap_context_func = other.wrap_context_func;
        other.callback_func = NULL;
        other.wrap_context_func = NULL;
    }


    PyCallBack(PyObject *wrap_context, PyObject *callback) : callback_func(callback), wrap_context_func(wrap_context)
    {
        if(!PyCallable_Check(callback))
        {
           throw Exception("Callback function is not callable.");
        }
        Py_INCREF(callback_func);
        Py_INCREF(wrap_context_func);
    }

    ~PyCallBack()
    {
        Py_XDECREF(callback_func);
        Py_XDECREF(wrap_context_func);
    }

    PyCallBack& operator=(const PyObject &other) = delete;
    PyCallBack& operator=(PyObject &&other) = delete;

    RetType operator()(PetriNetContext *context)
    {
        PyObject *capsule = PyCapsule_New(context, NULL, NULL);
        PyObject *wrap_func_arg = Py_BuildValue("(O)", capsule);
        PyObject *wrapped_state = PyEval_CallObject(wrap_context_func, wrap_func_arg);
        Py_DECREF(wrap_func_arg);
        PyObject *callback_func_arg = Py_BuildValue("(O)", wrapped_state);
        PyObject *callback_result = PyEval_CallObject(callback_func, callback_func_arg);
        Py_DECREF(callback_func_arg);
        Py_DECREF(wrapped_state);
        Py_DECREF(capsule);
        if(callback_result == NULL)
        {//exception happened
            throw Exception("Exception happened in callback function.");
        }
        RetType result = ConvertBasicTypeFromPy<RetType>(callback_result);
        return result;
    }
};

unsigned int add_transition(void *pn_ptr, int pytype, /*0 for imme, 1 for exp*/
                            PyObject *pyguard_func,
                            double pyparam, PyObject *pyparam_func,
                            unsigned int priority) throw(Exception)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    ConstOrVar<bool> guard;
    if (pyguard_func == Py_None)
    {
        guard = true;
    } else
    {
        PyCallBack<bool> wrapped_guard_func((PyObject *) pn->tag, pyguard_func);
        guard = wrapped_guard_func;
    }
    ConstOrVar<double> param;
    if (pyparam_func == Py_None)
    {
        param = pyparam;
    } else
    {
        PyCallBack<double> wrapped_param_func((PyObject *) pn->tag, pyparam_func);
        param = wrapped_param_func;
    }
    unsigned int index = pn->petri_net.add_transition((TransType) pytype, guard, param, priority);
    return index;
}


void add_arc(void *pn_ptr, int arc_type, /*0 for in, 1 for out, 2 for inhibitor*/
             unsigned int trans_index, unsigned int place_index,
             unsigned int pymulti, PyObject *pymulti_func) throw(Exception)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    ConstOrVar<unsigned int> multi;
    if (pymulti_func == Py_None)
    {
        multi = pymulti;
    } else
    {
        PyCallBack<unsigned int> wrapped_multi((PyObject *) pn->tag, pymulti_func);
        multi = wrapped_multi;
    }
    pn->petri_net.add_arc((ArcType) arc_type, trans_index, place_index, multi);
}

void set_init_token(void *pn_ptr, unsigned int place_index, unsigned int token_num)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    pn->petri_net.set_init_token(place_index, token_num);
}

//TODO: convergence feedback
bool solve_steady_state(void *pn_ptr)throw(Exception)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    pn->petri_net.finalize();
    pn->solve_steady_state();
    return true;
}



unsigned int get_token_num(PyObject *wrapped_context, unsigned int place_index)
{
    PetriNetContext *context = (PetriNetContext *) PyCapsule_GetPointer(wrapped_context, NULL);
    return context->petri_net->get_token_num(place_index, context);
}

bool is_trans_enabled(PyObject *wrapped_context, unsigned int trans_index)
{
    PetriNetContext *context = (PetriNetContext *) PyCapsule_GetPointer(wrapped_context, NULL);
    return context->petri_net->is_transition_enabled(trans_index, context);
}

bool has_enbaled_trans(PyObject *wrapped_context)
{
    PetriNetContext *context = (PetriNetContext *) PyCapsule_GetPointer(wrapped_context, NULL);
    return context->petri_net->has_enabled_trans(context);
}

void option_set_ss_method(void *pn_ptr, int method)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    pn->set_ss_method((Option::SSMethod)method);
}

void option_set_ts_method(void *pn_ptr, int method)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    pn->set_ts_method((Option::TSMethod)method);
}

void option_set_sor_omega(void *pn_ptr, double omega)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    pn->set_sor_omega(omega);
}

void option_set_max_iter(void *pn_ptr, unsigned int iter)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    pn->set_max_iter(iter);

}

void option_set_precision(void *pn_ptr, double prec)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    pn->set_precision(prec);
}

unsigned int add_inst_reward(void *pn_ptr, PyObject *pyreward_func) throw(Exception)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    PyCallBack<double> wrapped_reward_func((PyObject *) pn->tag, pyreward_func);
    unsigned int index = pn->add_inst_reward_func(wrapped_reward_func);
    return index;
}
unsigned int add_cum_reward(void *pn_ptr, PyObject *pyreward_func)throw(Exception)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    PyCallBack<double> wrapped_reward_func((PyObject *) pn->tag, pyreward_func);
    unsigned int index = pn->add_cum_reward_func(wrapped_reward_func);
    return index;
}

double get_inst_reward(void *pn_ptr, unsigned int reward_index)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    double reward = pn->get_inst_reward(reward_index);
    LOG2("inst reward (" << reward_index <<", " << reward << ")" );
    return reward;
}

double get_cum_reward(void *pn_ptr, unsigned int reward_index)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    double reward = pn->get_cum_reward(reward_index);
    LOG2("cum reward (" << reward_index <<", " << reward << ")" );
    return reward;
}

void set_halt_condition(void *pn_ptr, PyObject *halt_cond_func)throw(Exception)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    PyCallBack<bool> wrapped_halt_func((PyObject *) pn->tag, halt_cond_func);
    pn->petri_net.set_halt_condition(wrapped_halt_func);
}
