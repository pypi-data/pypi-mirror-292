#include <Python.h>
#include <numpy/arrayobject.h>
#include <math.h>
#define PI 3.14159265358979323846

/*
Calculate the angular difference between two numbers of double precision.

@param double *AngleStart array of size n angles. This is the start angle if smallestAngle is false.
@param double *AngleEnd array of size n angles. This is the end angle if smallestAngle is false.
@param int nAngles Number of angles in array
@param int smallestAngle Whether to calculate the angular difference between the start and end angles or the smallest angle.
@param double Difference Angular difference
*/
double AngularDifferenceDouble(const double AngleStart, const double AngleEnd, const double MaxValue, int smallestAngle)
{
    double Difference = fmod(fabs(AngleStart - AngleEnd), MaxValue);
    if (smallestAngle)
        Difference = fmin(Difference, MaxValue - Difference);
    else if (AngleStart > AngleEnd)
        Difference = MaxValue - Difference;
    return Difference;
}

/*
Calculate the angular difference between two numbers of float precision.

@param float AngleStart angle. This is the start angle if smallestAngle is false.
@param float AngleEnd angle. This is the end angle if smallestAngle is false.
@param float MaxValue angle.
@param int nAngles Number of angles in array
@param int smallestAngle Whether to calculate the angular difference between the start and end angles or the smallest angle.
@param float Difference Angular difference
*/
float AngularDifferenceFloat(const float AngleStart, const float AngleEnd, const float MaxValue, int smallestAngle)
{
    float Difference = fmod(fabsf(AngleStart - AngleEnd), MaxValue);
    if (smallestAngle)
        Difference = fmin(Difference, MaxValue - Difference);
    else if (AngleStart > AngleEnd)
        Difference = MaxValue - Difference;
    return Difference;
}

/*
Calculate the angular difference between two numbers of float precision.

@param float *AngleStart array of size n angles. This is the start angle if smallestAngle is false.
@param float *AngleEnd array of size n angles. This is the end angle if smallestAngle is false.
@param int nAngles Number of angles in array
@param int smallestAngle Whether to calculate the angular difference between the start and end angles or the smallest angle.
@param float Difference Angular difference */
void AngularDifferencesFloat(const float *AngleStart, const float *AngleEnd, const float MaxValue, int nAngles, int smallestAngle, float *Difference)
{
    int i;
    for (i = 0; i < nAngles; ++i)
    {
        Difference[i] = fmod(fabsf(AngleStart[i] - AngleEnd[i]), MaxValue);
        if (smallestAngle)
            Difference[i] = fmin(Difference[i], MaxValue - Difference[i]);
        else if (AngleStart[i] > AngleEnd[i])
            Difference[i] = MaxValue - Difference[i];
    }
}

/*
Calculate the angular difference between two numbers of float precision.

@param double *AngleStart array of size n angles. This is the start angle if smallestAngle is false.
@param double *AngleEnd array of size n angles. This is the end angle if smallestAngle is false.
@param int nAngles Number of angles in array
@param int smallestAngle Whether to calculate the angular difference between the start and end angles or the smallest angle.
@param double Difference Angular difference */
void AngularDifferencesDouble(const double *AngleStart, const double *AngleEnd, const double MaxValue, int nAngles, int smallestAngle, double *Difference)
{
    int i;
    for (i = 0; i < nAngles; ++i)
    {
        Difference[i] = fmod(fabs(AngleStart[i] - AngleEnd[i]), MaxValue);
        if (smallestAngle)
            Difference[i] = fmin(Difference[i], MaxValue - Difference[i]);
        else if (AngleStart[i] > AngleEnd[i])
            Difference[i] = MaxValue - Difference[i];
    }
}

/*
Convert a point from X, X, m to Y, Y, m in double precision

@param double *ddmPoint array of size nx3
@param int nPoints Number of angles in array
@param double *rrmPoint array of size nx3
*/
void XXM2YYMDouble(const double *rrmPoint, int nPoints, const double transform, double *ddmPoint)
{
    int iPoint, i;
    for (iPoint = 0; iPoint < nPoints; ++iPoint)
    {
        i = iPoint * 3;
        ddmPoint[i + 0] = rrmPoint[i + 0] * transform;
        ddmPoint[i + 1] = rrmPoint[i + 1] * transform;
        ddmPoint[i + 2] = rrmPoint[i + 2];
    }
}

/*
Convert a point from X, X, m to Y, Y, m in float precision

@param float *ddmPoint array of size nx3
@param int nPoints Number of angles in array
@param float *rrmPoint array of size nx3
*/
void XXM2YYMFloat(const float *rrmPoint, int nPoints, const float transform, float *ddmPoint)
{
    int iPoint, i;
    for (iPoint = 0; iPoint < nPoints; ++iPoint)
    {
        i = iPoint * 3;
        ddmPoint[i + 0] = rrmPoint[i + 0] * transform;
        ddmPoint[i + 1] = rrmPoint[i + 1] * transform;
        ddmPoint[i + 2] = rrmPoint[i + 2];
    }
}

static PyObject *DegAngularDifferenceWrapper(PyObject *self, PyObject *args)
{
    double degAngleStart, degAngleEnd;
    int smallestAngle;

    // Parse the input tuple
    if (!PyArg_ParseTuple(args, "ddi", &degAngleStart, &degAngleEnd, &smallestAngle))
        return NULL;

    if (!((smallestAngle == 0) || (smallestAngle == 1)))
    {
        PyErr_SetString(PyExc_ValueError, "smallestAngle must be True or False");
        return NULL;
    }

    if (sizeof(degAngleEnd) == sizeof(double))
    {
        double maxValue = 360.0;
        double result_data = AngularDifferenceDouble(degAngleStart, degAngleEnd, maxValue, smallestAngle);
        return Py_BuildValue("d", result_data); // Convert double to PyObject*
    }
    else if (sizeof(degAngleEnd) == sizeof(float))
    {
        float maxValue = 360.0;
        float result_data = AngularDifferenceFloat(degAngleStart, degAngleEnd, maxValue, smallestAngle);
        return Py_BuildValue("f", result_data); // Convert float to PyObject*
    }
    else
    {
        PyErr_SetString(PyExc_ValueError, "Only 32 and 64 bit float types accepted.");
        return NULL;
    }
}

static PyObject *RadAngularDifferenceWrapper(PyObject *self, PyObject *args)
{
    double degAngleStart, degAngleEnd;
    int smallestAngle;

    // Parse the input tuple
    if (!PyArg_ParseTuple(args, "ddi", &degAngleStart, &degAngleEnd, &smallestAngle))
        return NULL;

    if (!((smallestAngle == 0) || (smallestAngle == 1)))
    {
        PyErr_SetString(PyExc_ValueError, "smallestAngle must be True or False");
        return NULL;
    }

    if (sizeof(degAngleEnd) == sizeof(double))
    {
        double maxValue = 2.0 * PI;
        double result_data = AngularDifferenceDouble(degAngleStart, degAngleEnd, maxValue, smallestAngle);
        return Py_BuildValue("d", result_data); // Convert double to PyObject*
    }
    else if (sizeof(degAngleEnd) == sizeof(float))
    {
        float maxValue = 2.0 * PI;
        float result_data = AngularDifferenceFloat(degAngleStart, degAngleEnd, maxValue, smallestAngle);
        return Py_BuildValue("f", result_data); // Convert float to PyObject*
    }
    else
    {
        PyErr_SetString(PyExc_ValueError, "Only 32 and 64 bit float types accepted.");
        return NULL;
    }
}

static PyObject *DegAngularDifferencesWrapper(PyObject *self, PyObject *args)
{
    PyArrayObject *degAngleStart, *degAngleEnd;
    int smallestAngle;

    // Parse the input tuple
    if (!PyArg_ParseTuple(args, "O!O!i", &PyArray_Type, &degAngleStart, &PyArray_Type, &degAngleEnd, &smallestAngle))
        return NULL;

    // checks
    if (!((smallestAngle == 0) || (smallestAngle == 1)))
    {
        PyErr_SetString(PyExc_ValueError, "smallestAngle must be True or False");
        return NULL;
    }
    if (!(PyArray_ISCONTIGUOUS(degAngleStart)) || !(PyArray_ISCONTIGUOUS(degAngleEnd)))
    {
        PyErr_SetString(PyExc_ValueError, "Input arrays must be a C contiguous.");
        return NULL;
    }
    if (PyArray_NDIM(degAngleStart) != PyArray_NDIM(degAngleEnd))
    {
        PyErr_SetString(PyExc_ValueError, "Input arrays have non-matching dimensions.");
        return NULL;
    }
    if (PyArray_SIZE(degAngleStart) != PyArray_SIZE(degAngleEnd))
    {
        PyErr_SetString(PyExc_ValueError, "Input arrays are of unequal size.");
        return NULL;
    }
    if (PyArray_TYPE(degAngleStart) != PyArray_TYPE(degAngleEnd))
    {
        PyErr_SetString(PyExc_ValueError, "Input arrays must have the same type.");
        return NULL;
    }

    PyObject *result_array = PyArray_SimpleNew(PyArray_NDIM(degAngleEnd), PyArray_SHAPE(degAngleEnd), PyArray_TYPE(degAngleEnd));
    if (result_array == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Could not create output array.");
        return NULL;
    }
    npy_intp nPoints = PyArray_SIZE(degAngleStart);
    if (PyArray_TYPE(degAngleEnd) == NPY_DOUBLE)
    {
        double *data1 = (double *)PyArray_DATA(degAngleStart);
        double *data2 = (double *)PyArray_DATA(degAngleEnd);
        double *result_data = (double *)PyArray_DATA((PyArrayObject *)result_array);
        AngularDifferencesDouble(data1, data2, 360.0, nPoints, smallestAngle, result_data);
    }
    else if (PyArray_TYPE(degAngleEnd) == NPY_FLOAT)
    {
        float *data1 = (float *)PyArray_DATA(degAngleStart);
        float *data2 = (float *)PyArray_DATA(degAngleEnd);
        float *result_data = (float *)PyArray_DATA((PyArrayObject *)result_array);
        AngularDifferencesFloat(data1, data2, 360.0, nPoints, smallestAngle, result_data);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError, "Only 32 and 64 bit float types accepted.");
        return NULL;
    }
    return result_array;
}

static PyObject *RadAngularDifferencesWrapper(PyObject *self, PyObject *args)
{
    PyArrayObject *radAngleStart, *radAngleEnd;
    int smallestAngle;

    // Parse the input tuple
    if (!PyArg_ParseTuple(args, "O!O!i", &PyArray_Type, &radAngleStart, &PyArray_Type, &radAngleEnd, &smallestAngle))
        return NULL;

    // checks
    if (!((smallestAngle == 0) || (smallestAngle == 1)))
    {
        PyErr_SetString(PyExc_ValueError, "smallestAngle must be True or False");
        return NULL;
    }
    if (!(PyArray_ISCONTIGUOUS(radAngleStart)) || !(PyArray_ISCONTIGUOUS(radAngleEnd)))
    {
        PyErr_SetString(PyExc_ValueError, "Input arrays must be a C contiguous.");
        return NULL;
    }
    if (PyArray_NDIM(radAngleStart) != PyArray_NDIM(radAngleEnd))
    {
        PyErr_SetString(PyExc_ValueError, "Input arrays have non-matching dimensions.");
        return NULL;
    }
    if (PyArray_SIZE(radAngleStart) != PyArray_SIZE(radAngleEnd))
    {
        PyErr_SetString(PyExc_ValueError, "Input arrays are of unequal size.");
        return NULL;
    }
    if (PyArray_TYPE(radAngleStart) != PyArray_TYPE(radAngleEnd))
    {
        PyErr_SetString(PyExc_ValueError, "Input arrays must have the same type.");
        return NULL;
    }

    PyObject *result_array = PyArray_SimpleNew(PyArray_NDIM(radAngleEnd), PyArray_SHAPE(radAngleStart), PyArray_TYPE(radAngleEnd));
    if (result_array == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Could not create output array.");
        return NULL;
    }
    npy_intp nPoints = PyArray_SIZE(radAngleStart);
    if (PyArray_TYPE(radAngleEnd) == NPY_DOUBLE)
    {
        double *data1 = (double *)PyArray_DATA(radAngleStart);
        double *data2 = (double *)PyArray_DATA(radAngleEnd);
        double *result_data = (double *)PyArray_DATA((PyArrayObject *)result_array);
        AngularDifferencesDouble(data1, data2, 2.0 * PI, nPoints, smallestAngle, result_data);
    }
    else if (PyArray_TYPE(radAngleEnd) == NPY_FLOAT)
    {
        float *data1 = (float *)PyArray_DATA(radAngleStart);
        float *data2 = (float *)PyArray_DATA(radAngleEnd);
        float *result_data = (float *)PyArray_DATA((PyArrayObject *)result_array);
        AngularDifferencesFloat(data1, data2, 2.0 * PI, nPoints, smallestAngle, result_data);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError, "Only 32 and 64 bit float types accepted.");
        return NULL;
    }
    return result_array;
}

static PyObject *RRM2DDMWrapper(PyObject *self, PyObject *args)
{
    PyArrayObject *rrmPoint;

    // Parse the input tuple
    if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &rrmPoint))
        return NULL;

    // Checks
    if (!(PyArray_ISCONTIGUOUS(rrmPoint)))
    {
        PyErr_SetString(PyExc_ValueError, "Input arrays must be a C contiguous.");
        return NULL;
    }

    PyObject *result_array = PyArray_SimpleNew(PyArray_NDIM(rrmPoint), PyArray_SHAPE(rrmPoint), PyArray_TYPE(rrmPoint));
    if (result_array == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Could not create output array.");
        return NULL;
    }
    if (PyArray_TYPE(rrmPoint) == NPY_DOUBLE)
    {
        double *data1 = (double *)PyArray_DATA(rrmPoint);
        double *result_data = (double *)PyArray_DATA((PyArrayObject *)result_array);
        XXM2YYMDouble(data1, PyArray_SIZE(rrmPoint) / 3, 180.0 / PI, result_data);
    }
    else if (PyArray_TYPE(rrmPoint) == NPY_FLOAT)
    {
        float *data1 = (float *)PyArray_DATA(rrmPoint);
        float *result_data = (float *)PyArray_DATA((PyArrayObject *)result_array);
        XXM2YYMFloat(data1, PyArray_SIZE(rrmPoint) / 3, 180.0 / PI, result_data);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError, "Only 32 and 64 bit float types accepted.");
        return NULL;
    }
    return result_array;
}

static PyObject *DDM2RRMWrapper(PyObject *self, PyObject *args)
{
    PyArrayObject *ddmPoint;

    // Parse the input tuple
    if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &ddmPoint))
        return NULL;

    // Checks
    if (!(PyArray_ISCONTIGUOUS(ddmPoint)))
    {
        PyErr_SetString(PyExc_ValueError, "Input arrays must be a C contiguous.");
        return NULL;
    }

    PyObject *result_array = PyArray_SimpleNew(PyArray_NDIM(ddmPoint), PyArray_SHAPE(ddmPoint), PyArray_TYPE(ddmPoint));
    if (result_array == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Could not create output array.");
        return NULL;
    }
    if (PyArray_TYPE(ddmPoint) == NPY_DOUBLE)
    {
        double *data1 = (double *)PyArray_DATA(ddmPoint);
        double *result_data = (double *)PyArray_DATA((PyArrayObject *)result_array);
        XXM2YYMDouble(data1, PyArray_SIZE(ddmPoint) / 3, PI / 180.0, result_data);
    }
    else if (PyArray_TYPE(ddmPoint) == NPY_FLOAT)
    {
        float *data1 = (float *)PyArray_DATA(ddmPoint);
        float *result_data = (float *)PyArray_DATA((PyArrayObject *)result_array);
        XXM2YYMFloat(data1, PyArray_SIZE(ddmPoint) / 3, PI / 180.0, result_data);
    }
    else
    {
        PyErr_SetString(PyExc_ValueError, "Only 32 and 64 bit float types accepted.");
        return NULL;
    }
    return result_array;
}

// Method definition object for this extension, these argumens mean:
// ml_name: The name of the method
// ml_meth: Function pointer to the method implementation
// ml_flags: Flags indicating special features of this method, such as
//           accepting arguments, accepting keyword arguments, being a class method, or being a static method of a class.
// ml_doc:  The docstring for the method
static PyMethodDef MyMethods[] = {
    {"deg_angular_differences", DegAngularDifferencesWrapper, METH_VARARGS, "Angular difference between two angles in degrees"},
    {"rad_angular_differences", RadAngularDifferencesWrapper, METH_VARARGS, "Angular difference between two angles in radians"},
    {"deg_angular_difference", DegAngularDifferenceWrapper, METH_VARARGS, "Angular difference between two angles in radians"},
    {"rad_angular_difference", RadAngularDifferenceWrapper, METH_VARARGS, "Angular difference between two angles in radians"},
    {"RRM2DDM", RRM2DDMWrapper, METH_VARARGS, "Converts arrays of [rad, rad, m] to [deg, deg, m]"},
    {"DDM2RRM", DDM2RRMWrapper, METH_VARARGS, "Converts arrays of [rad, rad, m] to [deg, deg, m]"},
    {NULL, NULL, 0, NULL}};

// Module definition
static struct PyModuleDef helpers = {
    PyModuleDef_HEAD_INIT,
    "helpers",
    "Module containing helper / miscellaneous functions",
    -1,
    MyMethods};

// Module initialization function
PyMODINIT_FUNC PyInit_helpers(void)
{
    import_array(); // Initialize the NumPy C API
    return PyModule_Create(&helpers);
}
