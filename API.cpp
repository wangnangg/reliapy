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
    std::cout << "create petri net solution:" << pn << std::endl;
    return pn;
}

void delete_petri_net(void *pn_ptr)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    PyObject *wrap_context_func = (PyObject *) pn->tag;
    Py_DECREF(wrap_context_func);
    std::cout << "delete petri net:" << pn << std::endl;
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
    }
    return PyFloat_AsDouble(obj);
}

template<>
bool ConvertBasicTypeFromPy(PyObject *obj)
{
    return PyObject_IsTrue(obj);
}

template<>
unsigned int ConvertBasicTypeFromPy(PyObject *obj)
{
    return PyLong_AsUnsignedLong(obj);
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
        Py_INCREF(callback_func);
        Py_INCREF(wrap_context_func);
    }

    ~PyCallBack()
    {
        Py_XDECREF(callback_func);
        Py_XDECREF(wrap_context_func);
    }

    RetType operator()(PetriNetContext *context)
    {
        PyObject *capsule = PyCapsule_New(context, NULL, NULL);
        PyObject *wrap_func_arg = Py_BuildValue("(O)", capsule);
        PyObject *wrapped_state = PyEval_CallObject(wrap_context_func, wrap_func_arg);
        PyObject *callback_func_arg = Py_BuildValue("(O)", wrapped_state);
        PyObject *callback_result = PyEval_CallObject(callback_func, callback_func_arg);
        RetType result = ConvertBasicTypeFromPy<RetType>(callback_result);
        return result;
    }
};

unsigned int add_transition(void *pn_ptr, int pytype, /*0 for imme, 1 for exp*/
                            PyObject *pyguard_func,
                            double pyparam, PyObject *pyparam_func,
                            unsigned int priority)
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
    std::cout << "add transition: type:" << pytype <<
              ", guard:" << guard.get_type() <<
              ", param:" << param.get_type() <<
              ", priority:" << priority << std::endl;
    return index;
}


void add_arc(void *pn_ptr, int arc_type, /*0 for in, 1 for out, 2 for inhibitor*/
             unsigned int trans_index, unsigned int place_index,
             unsigned int pymulti, PyObject *pymulti_func)
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

    std::cout << "add arc: type:" << arc_type <<
              ", trans_index:" << trans_index <<
              ", place_index:" << place_index <<
              ", multi:" << multi.get_type() << std::endl;
}

void set_init_token(void *pn_ptr, unsigned int place_index, unsigned int token_num)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    pn->petri_net.set_init_token(place_index, token_num);

    std::cout << "set init token: " << place_index << ", " << token_num << std::endl;
}

unsigned int add_inst_reward(void *pn_ptr, PyObject *pyreward_func)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    PyCallBack<double> wrapped_reward_func((PyObject *) pn->tag, pyreward_func);
    unsigned int index = pn->add_inst_reward_func(wrapped_reward_func);
    std::cout << "add inst reward: " << index << std::endl;
    return index;
}

bool solve_steady_state(void *pn_ptr)
{
    std::cout << "start solve" << std::endl;
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    pn->petri_net.finalize();
    auto stop_conditoin = pn->solve_steady_state();
    std::cout << "solved in :" << stop_conditoin.get_used_iter() << std::endl;
    return stop_conditoin.is_precision_reached();
}

double get_inst_reward(void *pn_ptr, unsigned int reward_index)
{
    PetriNetSolution *pn = (PetriNetSolution *) pn_ptr;
    double reward = pn->get_inst_reward(reward_index);
    std::cout << "reward:" << reward_index << ", " << reward << std::endl;
    return reward;
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



