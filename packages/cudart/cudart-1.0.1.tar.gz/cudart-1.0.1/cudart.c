#include <Python.h>

static int module_exec(PyObject * self) {
    return 0;
}

static PyModuleDef_Slot module_slots[] = {
    {Py_mod_exec, module_exec},
    {0},
};

static PyModuleDef module_def = {PyModuleDef_HEAD_INIT, "cudart", NULL, 0, NULL, module_slots, NULL, NULL, NULL};

PyObject * PyInit_cudart() {
    return PyModuleDef_Init(&module_def);
}
