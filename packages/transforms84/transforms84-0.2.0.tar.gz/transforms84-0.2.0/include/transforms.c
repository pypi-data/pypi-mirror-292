#include <Python.h>
#include <numpy/arrayobject.h>
#define NCOORDSINPOINT 3

/*
Geodetic to ECEF transformation of float precision.
https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#From_geodetic_to_ECEF_coordinates

@param double *rrmLLA array of size nx3 latitude (phi), longitude (gamma),
height (h) [rad, rad, m]
@param size_t nPoints Number of LLA points
@param double a semi-major axis
@param double b semi-minor axis
@param double *mmmXYZ array of size nx3 X, Y, Z [rad, rad, m]
*/
void geodetic2ECEFFloat(const float* rrmLLA,
    size_t nPoints,
    double a,
    double b,
    float* mmmXYZ)
{
    float e2 = 1 - (b * b) / (a * a);
    size_t iPoint, i;
    float N;
    for (iPoint = 0; iPoint < nPoints; ++iPoint) {
        i = iPoint * NCOORDSINPOINT;
        N = a / sqrt(1 - e2 * (sin(rrmLLA[i + 0]) * sin(rrmLLA[i + 0])));
        mmmXYZ[i + 0] = (N + rrmLLA[i + 2]) * cos(rrmLLA[i + 0]) * cos(rrmLLA[i + 1]);
        mmmXYZ[i + 1] = (N + rrmLLA[i + 2]) * cos(rrmLLA[i + 0]) * sin(rrmLLA[i + 1]);
        mmmXYZ[i + 2] = ((1 - e2) * N + rrmLLA[i + 2]) * sin(rrmLLA[i + 0]);
    }
}

/*
Geodetic to ECEF transformation of double precision.
https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#From_geodetic_to_ECEF_coordinates

@param double *rrmLLA array of size nx3 latitude (phi), longitude (gamma),
height (h) [rad, rad, m]
@param size_t nPoints Number of LLA points
@param double a semi-major axis
@param double b semi-minor axis
@param double *mmmXYZ array of size nx3 X, Y, Z [m, m, m]
*/
void geodetic2ECEFDouble(const double* rrmLLA,
    size_t nPoints,
    double a,
    double b,
    double* mmmXYZ)
{
    double e2 = 1 - (b * b) / (a * a);
    size_t iPoint, i;
    double N;
    for (iPoint = 0; iPoint < nPoints; ++iPoint) {
        i = iPoint * NCOORDSINPOINT;
        N = a / sqrt(1 - e2 * sin(rrmLLA[i + 0]) * sin(rrmLLA[i + 0]));
        mmmXYZ[i + 0] = (N + rrmLLA[i + 2]) * cos(rrmLLA[i + 0]) * cos(rrmLLA[i + 1]);
        mmmXYZ[i + 1] = (N + rrmLLA[i + 2]) * cos(rrmLLA[i + 0]) * sin(rrmLLA[i + 1]);
        mmmXYZ[i + 2] = ((1 - e2) * N + rrmLLA[i + 2]) * sin(rrmLLA[i + 0]);
    }
}

/*
ECEF to geodetic transformation of float precision.
https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#The_application_of_Ferrari's_solution

@param double *mmmXYZ array of size nx3 X, Y, Z [m, m, m]
@param size_t nPoints Number of ECEF points
@param double a semi-major axis
@param double b semi-minor axis
@param double *rrmLLA array of size nx3 latitude (phi), longitude (gamma),
height (h) [rad, rad, m]
*/
void ECEF2geodeticFloat(const float* mmmXYZ,
    size_t nPoints,
    double a,
    double b,
    float* rrmLLA)
{
    float e2 = ((a * a) - (b * b)) / (a * a);
    float ed2 = ((a * a) - (b * b)) / (b * b);
    size_t iPoint, i;
    for (iPoint = 0; iPoint < nPoints; ++iPoint) {
        i = iPoint * NCOORDSINPOINT;
        float p = sqrt(mmmXYZ[i + 0] * mmmXYZ[i + 0] + mmmXYZ[i + 1] * mmmXYZ[i + 1]);
        float F = 54 * b * b * mmmXYZ[i + 2] * mmmXYZ[i + 2];
        float G = p * p + (1 - e2) * mmmXYZ[i + 2] * mmmXYZ[i + 2] - e2 * (a * a - b * b);
        float c = e2 * e2 * F * p * p / (G * G * G);
        float s = cbrt(1 + c + sqrt(c * c + 2 * c));
        float k = s + 1 + 1 / s;
        float P = F / (3 * k * k * G * G);
        float Q = sqrt(1 + 2 * e2 * e2 * P);
        float r0 = -P * e2 * p / (1 + Q) + sqrt(0.5 * a * a * (1 + 1 / Q) - P * (1 - e2) * mmmXYZ[i + 2] * mmmXYZ[i + 2] / (Q * (1 + Q)) - 0.5 * P * p * p);
        float U = sqrt((p - e2 * r0) * (p - e2 * r0) + mmmXYZ[i + 2] * mmmXYZ[i + 2]);
        float V = sqrt((p - e2 * r0) * (p - e2 * r0) + (1 - e2) * mmmXYZ[i + 2] * mmmXYZ[i + 2]);
        float z0 = b * b * mmmXYZ[i + 2] / (a * V);
        rrmLLA[i + 0] = atan((mmmXYZ[i + 2] + ed2 * z0) / p);
        rrmLLA[i + 1] = atan2(mmmXYZ[i + 1], mmmXYZ[i + 0]);
        rrmLLA[i + 2] = U * (1 - b * b / (a * V));
    }
}

/*
ECEF to geodetic transformation of double precision.
https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#The_application_of_Ferrari's_solution

@param double *mmmXYZ array of size nx3 X, Y, Z [m, m, m]
@param size_t nPoints Number of ECEF points
@param double a semi-major axis
@param double b semi-minor axis
@param double *rrmLLA array of size nx3 latitude (phi), longitude (gamma),
height (h) [rad, rad, m]
*/
void ECEF2geodeticDouble(const double* mmmXYZ,
    size_t nPoints,
    double a,
    double b,
    double* rrmLLA)
{
    double e2 = ((a * a) - (b * b)) / (a * a);
    double ed2 = ((a * a) - (b * b)) / (b * b);
    size_t iPoint, i;
    for (iPoint = 0; iPoint < nPoints; ++iPoint) {
        i = iPoint * NCOORDSINPOINT;
        double p = sqrt(mmmXYZ[i + 0] * mmmXYZ[i + 0] + mmmXYZ[i + 1] * mmmXYZ[i + 1]);
        double F = 54 * b * b * mmmXYZ[i + 2] * mmmXYZ[i + 2];
        double G = p * p + (1 - e2) * mmmXYZ[i + 2] * mmmXYZ[i + 2] - e2 * (a * a - b * b);
        double c = e2 * e2 * F * p * p / (G * G * G);
        double s = cbrt(1 + c + sqrt(c * c + 2 * c));
        double k = s + 1 + 1 / s;
        double P = F / (3 * k * k * G * G);
        double Q = sqrt(1 + 2 * e2 * e2 * P);
        double r0 = -P * e2 * p / (1 + Q) + sqrt(0.5 * a * a * (1 + 1 / Q) - P * (1 - e2) * mmmXYZ[i + 2] * mmmXYZ[i + 2] / (Q * (1 + Q)) - 0.5 * P * p * p);
        double U = sqrt((p - e2 * r0) * (p - e2 * r0) + mmmXYZ[i + 2] * mmmXYZ[i + 2]);
        double V = sqrt((p - e2 * r0) * (p - e2 * r0) + (1 - e2) * mmmXYZ[i + 2] * mmmXYZ[i + 2]);
        double z0 = b * b * mmmXYZ[i + 2] / (a * V);
        rrmLLA[i + 0] = atan((mmmXYZ[i + 2] + ed2 * z0) / p);
        rrmLLA[i + 1] = atan2(mmmXYZ[i + 1], mmmXYZ[i + 0]);
        rrmLLA[i + 2] = U * (1 - b * b / (a * V));
    }
}

/*
ECEF to ENU transformation of float precision.
https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#From_ECEF_to_ENU

@param double *rrmLLALocalOrigin array of size nx3 of local reference point X,
Y, Z [m, m, m]
@param double *mmmXYZTarget array of size nx3 of target point X, Y, Z [m, m, m]
@param size_t nPoints Number of target points
@param double a semi-major axis
@param double b semi-minor axis
@param double *mmmLocal array of size nx3 X, Y, Z [m, m, m]
*/
void ECEF2ENUFloat(const float* rrmLLALocalOrigin,
    const float* mmmXYZTarget,
    size_t nTargets,
    int isOriginSizeOfTargets,
    double a,
    double b,
    float* mmmLocal)
{
    int nOriginPoints = (nTargets - 1) * isOriginSizeOfTargets + 1;
    float* mmmXYZLocalOrigin = (float*)malloc(nOriginPoints * NCOORDSINPOINT * sizeof(float));
    geodetic2ECEFFloat(rrmLLALocalOrigin, nOriginPoints, a, b, mmmXYZLocalOrigin);
    float DeltaX, DeltaY, DeltaZ;
    size_t iPoint, iTarget, iOrigin;
    for (iPoint = 0; iPoint < nTargets; ++iPoint) {
        iTarget = iPoint * NCOORDSINPOINT;
        iOrigin = iTarget * isOriginSizeOfTargets;
        DeltaX = mmmXYZTarget[iTarget + 0] - mmmXYZLocalOrigin[iOrigin + 0];
        DeltaY = mmmXYZTarget[iTarget + 1] - mmmXYZLocalOrigin[iOrigin + 1];
        DeltaZ = mmmXYZTarget[iTarget + 2] - mmmXYZLocalOrigin[iOrigin + 2];
        mmmLocal[iTarget + 0] = -sin(rrmLLALocalOrigin[iOrigin + 1]) * DeltaX + cos(rrmLLALocalOrigin[iOrigin + 1]) * DeltaY;
        mmmLocal[iTarget + 1] = -sin(rrmLLALocalOrigin[iOrigin + 0]) * cos(rrmLLALocalOrigin[iOrigin + 1]) * DeltaX + -sin(rrmLLALocalOrigin[iOrigin + 0]) * sin(rrmLLALocalOrigin[iOrigin + 1]) * DeltaY + cos(rrmLLALocalOrigin[iOrigin + 0]) * DeltaZ;
        mmmLocal[iTarget + 2] = cos(rrmLLALocalOrigin[iOrigin + 0]) * cos(rrmLLALocalOrigin[iOrigin + 1]) * DeltaX + cos(rrmLLALocalOrigin[iOrigin + 0]) * sin(rrmLLALocalOrigin[iOrigin + 1]) * DeltaY + sin(rrmLLALocalOrigin[iOrigin + 0]) * DeltaZ;
    }
    free(mmmXYZLocalOrigin);
}

/*
ECEF to ENU transformation of double precision.
https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#From_ECEF_to_ENU

@param double *rrmLLALocalOrigin array of size nx3 of local reference point X,
Y, Z [m, m, m]
@param double *mmmXYZTarget array of size nx3 of target point X, Y, Z [m, m, m]
@param size_t nPoints Number of target points
@param double a semi-major axis
@param double b semi-minor axis
@param double *mmmLocal array of size nx3 X, Y, Z [m, m, m]
*/
void ECEF2ENUDouble(const double* rrmLLALocalOrigin,
    const double* mmmXYZTarget,
    size_t nTargets,
    int isOriginSizeOfTargets,
    double a,
    double b,
    double* mmmLocal)
{
    int nOriginPoints = (nTargets - 1) * isOriginSizeOfTargets + 1;
    double* mmmXYZLocalOrigin = (double*)malloc(nOriginPoints * NCOORDSINPOINT * sizeof(double));
    geodetic2ECEFDouble(
        rrmLLALocalOrigin, nOriginPoints, a, b, mmmXYZLocalOrigin);
    double DeltaX, DeltaY, DeltaZ;
    size_t iPoint, iTarget, iOrigin;
    for (iPoint = 0; iPoint < nTargets; ++iPoint) {
        iTarget = iPoint * NCOORDSINPOINT;
        iOrigin = iTarget * isOriginSizeOfTargets;
        DeltaX = mmmXYZTarget[iTarget + 0] - mmmXYZLocalOrigin[iOrigin + 0];
        DeltaY = mmmXYZTarget[iTarget + 1] - mmmXYZLocalOrigin[iOrigin + 1];
        DeltaZ = mmmXYZTarget[iTarget + 2] - mmmXYZLocalOrigin[iOrigin + 2];
        mmmLocal[iTarget + 0] = -sin(rrmLLALocalOrigin[iOrigin + 1]) * DeltaX + cos(rrmLLALocalOrigin[iOrigin + 1]) * DeltaY;
        mmmLocal[iTarget + 1] = -sin(rrmLLALocalOrigin[iOrigin + 0]) * cos(rrmLLALocalOrigin[iOrigin + 1]) * DeltaX + -sin(rrmLLALocalOrigin[iOrigin + 0]) * sin(rrmLLALocalOrigin[iOrigin + 1]) * DeltaY + cos(rrmLLALocalOrigin[iOrigin + 0]) * DeltaZ;
        mmmLocal[iTarget + 2] = cos(rrmLLALocalOrigin[iOrigin + 0]) * cos(rrmLLALocalOrigin[iOrigin + 1]) * DeltaX + cos(rrmLLALocalOrigin[iOrigin + 0]) * sin(rrmLLALocalOrigin[iOrigin + 1]) * DeltaY + sin(rrmLLALocalOrigin[iOrigin + 0]) * DeltaZ;
    }
    free(mmmXYZLocalOrigin);
}

/*
ECEF to ENU transformation of float precision.
https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#From_ENU_to_ECEF
https://www.lddgo.net/en/coordinate/ecef-enu

@param double *rrmLLALocalOrigin array of size nx3 of local reference point
latitude, longitude, height [rad, rad, m]
@param float *mmmXYZTarget array of size nx3 of target point X, Y, Z [m, m, m]
@param size_t nPoints Number of target points
@param double a semi-major axis
@param double b semi-minor axis
@param float *mmmLocal array of size nx3 X, Y, Z [m, m, m]
*/
void ENU2ECEFFloat(const float* rrmLLALocalOrigin,
    const float* mmmTargetLocal,
    size_t nTargets,
    int isOriginSizeOfTargets,
    double a,
    double b,
    float* mmmXYZTarget)
{
    int nOriginPoints = (nTargets - 1) * isOriginSizeOfTargets + 1;
    float* mmmXYZLocalOrigin = (float*)malloc(nOriginPoints * NCOORDSINPOINT * sizeof(float));
    geodetic2ECEFFloat(rrmLLALocalOrigin, nOriginPoints, a, b, mmmXYZLocalOrigin);
    size_t iPoint, iTarget, iOrigin;
    for (iPoint = 0; iPoint < nTargets; ++iPoint) {
        iTarget = iPoint * NCOORDSINPOINT;
        iOrigin = iTarget * isOriginSizeOfTargets;
        mmmXYZTarget[iTarget + 0] = -sin(rrmLLALocalOrigin[iOrigin + 1]) * mmmTargetLocal[iTarget + 0] + -sin(rrmLLALocalOrigin[iOrigin + 0]) * cos(rrmLLALocalOrigin[iOrigin + 1]) * mmmTargetLocal[iTarget + 1] + cos(rrmLLALocalOrigin[iOrigin + 0]) * cos(rrmLLALocalOrigin[iOrigin + 1]) * mmmTargetLocal[iTarget + 2] + mmmXYZLocalOrigin[iOrigin + 0];
        mmmXYZTarget[iTarget + 1] = cos(rrmLLALocalOrigin[iOrigin + 1]) * mmmTargetLocal[iTarget + 0] + -sin(rrmLLALocalOrigin[iOrigin + 0]) * sin(rrmLLALocalOrigin[iOrigin + 1]) * mmmTargetLocal[iTarget + 1] + cos(rrmLLALocalOrigin[iOrigin + 0]) * sin(rrmLLALocalOrigin[iOrigin + 1]) * mmmTargetLocal[2] + mmmXYZLocalOrigin[iOrigin + 1];
        mmmXYZTarget[iTarget + 2] = cos(rrmLLALocalOrigin[iOrigin + 0]) * mmmTargetLocal[iTarget + 1] + sin(rrmLLALocalOrigin[iOrigin + 0]) * mmmTargetLocal[2] + mmmXYZLocalOrigin[iOrigin + 2];
    }
    free(mmmXYZLocalOrigin);
}

/*
ECEF to ENU transformation of double precision.
https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#From_ENU_to_ECEF
https://www.lddgo.net/en/coordinate/ecef-enu

@param double *rrmLLALocalOrigin array of size nx3 of local reference point
latitude, longitude, height [rad, rad, m]
@param double *mmmLocal array of size nx3 X, Y, Z [m, m, m]
@param size_t nPoints Number of target points
@param double a semi-major axis
@param double b semi-minor axis
@param double *mmmXYZTarget array of size nx3 of target point X, Y, Z [m, m, m]
*/
void ENU2ECEFDouble(const double* rrmLLALocalOrigin,
    const double* mmmTargetLocal,
    size_t nTargets,
    int isOriginSizeOfTargets,
    double a,
    double b,
    double* mmmXYZTarget)
{
    int nOriginPoints = (nTargets - 1) * isOriginSizeOfTargets + 1;
    double* mmmXYZLocalOrigin = (double*)malloc(nOriginPoints * NCOORDSINPOINT * sizeof(double));
    geodetic2ECEFDouble(
        rrmLLALocalOrigin, nOriginPoints, a, b, mmmXYZLocalOrigin);
    size_t iPoint, iTarget, iOrigin;
    for (iPoint = 0; iPoint < nTargets; ++iPoint) {
        iTarget = iPoint * NCOORDSINPOINT;
        iOrigin = iTarget * isOriginSizeOfTargets;
        mmmXYZTarget[iTarget + 0] = -sin(rrmLLALocalOrigin[iOrigin + 1]) * mmmTargetLocal[iTarget + 0] + -sin(rrmLLALocalOrigin[iOrigin + 0]) * cos(rrmLLALocalOrigin[iOrigin + 1]) * mmmTargetLocal[iTarget + 1] + cos(rrmLLALocalOrigin[iOrigin + 0]) * cos(rrmLLALocalOrigin[iOrigin + 1]) * mmmTargetLocal[iTarget + 2] + mmmXYZLocalOrigin[iOrigin + 0];
        mmmXYZTarget[iTarget + 1] = cos(rrmLLALocalOrigin[iOrigin + 1]) * mmmTargetLocal[iTarget + 0] + -sin(rrmLLALocalOrigin[iOrigin + 0]) * sin(rrmLLALocalOrigin[iOrigin + 1]) * mmmTargetLocal[iTarget + 1] + cos(rrmLLALocalOrigin[iOrigin + 0]) * sin(rrmLLALocalOrigin[iOrigin + 1]) * mmmTargetLocal[2] + mmmXYZLocalOrigin[iOrigin + 1];
        mmmXYZTarget[iTarget + 2] = cos(rrmLLALocalOrigin[iOrigin + 0]) * mmmTargetLocal[iTarget + 1] + sin(rrmLLALocalOrigin[iOrigin + 0]) * mmmTargetLocal[iTarget + 2] + mmmXYZLocalOrigin[iOrigin + 2];
    }
    free(mmmXYZLocalOrigin);
}

/*
ENU to AER transformation of float precision.
https://x-lumin.com/wp-content/uploads/2020/09/Coordinate_Transforms.pdf <-
includes additional errors and factors that could be implemented
https://www.lddgo.net/en/coordinate/ecef-enu

@param float *mmmLocal array of size nx3 X, Y, Z [m, m, m]
@param size_t nPoints Number of target points
@param float *rrmAER array of size nx3 of target point azimuth, elevation,
range [rad, rad, m]
*/
void ENU2AERFloat(const float* mmmENU, size_t nPoints, float* rrmAER)
{
    size_t iPoint, i;
    for (iPoint = 0; iPoint < nPoints; ++iPoint) {
        i = iPoint * NCOORDSINPOINT;
        rrmAER[i + 0] = atan2(mmmENU[i + 0], mmmENU[i + 1]);
        rrmAER[i + 2] = sqrt(mmmENU[i + 0] * mmmENU[i + 0] + mmmENU[i + 1] * mmmENU[i + 1] + mmmENU[i + 2] * mmmENU[i + 2]);
        rrmAER[i + 1] = asin(mmmENU[i + 2] / rrmAER[i + 2]);
    }
}

/*
ENU to AER transformation of double precision.
https://x-lumin.com/wp-content/uploads/2020/09/Coordinate_Transforms.pdf
https://www.lddgo.net/en/coordinate/ecef-enu

@param double *mmmLocal array of size nx3 X, Y, Z [m, m, m]
@param size_t nPoints Number of target points
@param double *rrmAER array of size nx3 of target point azimuth, elevation,
range [rad, rad, m]
*/
void ENU2AERDouble(const double* mmmENU, size_t nPoints, double* rrmAER)
{
    size_t iPoint, i;
    for (iPoint = 0; iPoint < nPoints; ++iPoint) {
        i = iPoint * NCOORDSINPOINT;
        rrmAER[i + 0] = atan2(mmmENU[i + 0], mmmENU[i + 1]);
        rrmAER[i + 2] = sqrt(mmmENU[i + 0] * mmmENU[i + 0] + mmmENU[i + 1] * mmmENU[i + 1] + mmmENU[i + 2] * mmmENU[i + 2]);
        rrmAER[i + 1] = asin(mmmENU[i + 2] / rrmAER[i + 2]);
    }
}

/*
AER to ENU transformation of float precision.
https://x-lumin.com/wp-content/uploads/2020/09/Coordinate_Transforms.pdf

@param float *rrmAER array of size nx3 of target point azimuth, elevation,
range [rad, rad, m]
@param size_t nPoints Number of target points
@param float *mmmLocal array of size nx3 X, Y, Z [m, m, m]
*/
void AER2ENUFloat(const float* rrmAER, size_t nPoints, float* mmmENU)
{
    size_t iPoint, i;
    for (iPoint = 0; iPoint < nPoints; ++iPoint) {
        i = iPoint * NCOORDSINPOINT;
        mmmENU[i + 0] = cos(rrmAER[i + 1]) * sin(rrmAER[i + 0]) * rrmAER[i + 2];
        mmmENU[i + 1] = cos(rrmAER[i + 1]) * cos(rrmAER[i + 0]) * rrmAER[i + 2];
        mmmENU[i + 2] = sin(rrmAER[i + 1]) * rrmAER[i + 2];
    }
}

/*
AER to ENU transformation of double precision.
https://x-lumin.com/wp-content/uploads/2020/09/Coordinate_Transforms.pdf

@param double *rrmAER array of size nx3 of target point azimuth, elevation,
range [rad, rad, m]
@param size_t nPoints Number of target points
@param double *mmmLocal array of size nx3 X, Y, Z [m, m, m]
*/
void AER2ENUDouble(const double* rrmAER, size_t nPoints, double* mmmENU)
{
    size_t iPoint, i;
    for (iPoint = 0; iPoint < nPoints; ++iPoint) {
        i = iPoint * NCOORDSINPOINT;
        mmmENU[i + 0] = cos(rrmAER[i + 1]) * sin(rrmAER[i + 0]) * rrmAER[i + 2];
        mmmENU[i + 1] = cos(rrmAER[i + 1]) * cos(rrmAER[i + 0]) * rrmAER[i + 2];
        mmmENU[i + 2] = sin(rrmAER[i + 1]) * rrmAER[i + 2];
    }
}

static PyObject*
geodetic2ECEFWrapper(PyObject* self, PyObject* args)
{
    PyArrayObject* rrmLLA;
    double a, b;

    // checks
    if (!PyArg_ParseTuple(args, "O!dd", &PyArray_Type, &rrmLLA, &a, &b))
        return NULL;
    if (!(PyArray_ISCONTIGUOUS(rrmLLA))) {
        PyErr_SetString(PyExc_ValueError, "Input arrays must be a C contiguous.");
        return NULL;
    }
    if ((PyArray_SIZE(rrmLLA) % NCOORDSINPOINT) != 0) {
        PyErr_SetString(PyExc_ValueError, "Input arrays must be a multiple of 3.");
        return NULL;
    }

    PyObject* result_array = PyArray_SimpleNew(
        PyArray_NDIM(rrmLLA), PyArray_SHAPE(rrmLLA), PyArray_TYPE(rrmLLA));
    if (result_array == NULL)
        return NULL;
    size_t nPoints = PyArray_SIZE(rrmLLA) / NCOORDSINPOINT;
    if (PyArray_TYPE(rrmLLA) == NPY_DOUBLE) {
        double* data1 = (double*)PyArray_DATA(rrmLLA);
        double* result_data = (double*)PyArray_DATA((PyArrayObject*)result_array);
        geodetic2ECEFDouble(data1, nPoints, a, b, result_data);
    } else if (PyArray_TYPE(rrmLLA) == NPY_FLOAT) {
        float* data1 = (float*)PyArray_DATA(rrmLLA);
        float* result_data = (float*)PyArray_DATA((PyArrayObject*)result_array);
        geodetic2ECEFFloat(data1, nPoints, a, b, result_data);
    } else {
        PyErr_SetString(PyExc_ValueError,
            "Only 32 and 64 bit float types accepted.");
        return NULL;
    }
    return result_array;
}

static PyObject*
ECEF2geodeticWrapper(PyObject* self, PyObject* args)
{
    PyArrayObject* mmmXYZ;
    double a, b;

    // checks
    if (!PyArg_ParseTuple(args, "O!dd", &PyArray_Type, &mmmXYZ, &a, &b))
        return NULL;
    if (!(PyArray_ISCONTIGUOUS(mmmXYZ))) {
        PyErr_SetString(PyExc_ValueError, "Input arrays must be a C contiguous.");
        return NULL;
    }
    if ((PyArray_SIZE(mmmXYZ) % NCOORDSINPOINT) != 0) {
        PyErr_SetString(PyExc_ValueError, "Input arrays must be a multiple of 3.");
        return NULL;
    }

    PyObject* result_array = PyArray_SimpleNew(
        PyArray_NDIM(mmmXYZ), PyArray_SHAPE(mmmXYZ), PyArray_TYPE(mmmXYZ));
    if (result_array == NULL)
        return NULL;
    size_t nPoints = PyArray_SIZE(mmmXYZ) / NCOORDSINPOINT;
    if (PyArray_TYPE(mmmXYZ) == NPY_DOUBLE) {
        double* data1 = (double*)PyArray_DATA(mmmXYZ);
        double* result_data = (double*)PyArray_DATA((PyArrayObject*)result_array);
        ECEF2geodeticDouble(data1, nPoints, a, b, result_data);
    } else if (PyArray_TYPE(mmmXYZ) == NPY_FLOAT) {
        float* data1 = (float*)PyArray_DATA(mmmXYZ);
        float* result_data = (float*)PyArray_DATA((PyArrayObject*)result_array);
        ECEF2geodeticFloat(data1, nPoints, a, b, result_data);
    } else {
        PyErr_SetString(PyExc_ValueError,
            "Only 32 and 64 bit float types accepted.");
        return NULL;
    }
    return result_array;
}

static PyObject*
ECEF2ENUWrapper(PyObject* self, PyObject* args)
{
    PyArrayObject *rrmLLALocalOrigin, *mmmXYZTarget;
    double a, b;

    // checks
    if (!PyArg_ParseTuple(args,
            "O!O!dd",
            &PyArray_Type,
            &rrmLLALocalOrigin,
            &PyArray_Type,
            &mmmXYZTarget,
            &a,
            &b))
        return NULL;
    if (!(PyArray_ISCONTIGUOUS(rrmLLALocalOrigin)) || !(PyArray_ISCONTIGUOUS(mmmXYZTarget))) {
        PyErr_SetString(PyExc_ValueError, "Input arrays must be a C contiguous.");
        return NULL;
    }
    if (!((PyArray_NDIM(rrmLLALocalOrigin) == PyArray_NDIM(mmmXYZTarget)) && (PyArray_SIZE(rrmLLALocalOrigin) == PyArray_SIZE(mmmXYZTarget)) || ((PyArray_Size(rrmLLALocalOrigin) == NCOORDSINPOINT) && (PyArray_SIZE(rrmLLALocalOrigin) < PyArray_SIZE(mmmXYZTarget))))) {
        PyErr_SetString(PyExc_ValueError,
            "Input arrays must have matching size and dimensions or "
            "the origin must be of size three.");
        return NULL;
    }
    if ((PyArray_SIZE(rrmLLALocalOrigin) % NCOORDSINPOINT) != 0 || (PyArray_SIZE(mmmXYZTarget) % NCOORDSINPOINT) != 0) {
        PyErr_SetString(PyExc_ValueError, "Input arrays must be a multiple of 3.");
        return NULL;
    }
    if (PyArray_TYPE(rrmLLALocalOrigin) != PyArray_TYPE(mmmXYZTarget)) {
        PyErr_SetString(PyExc_ValueError, "Input arrays must have the same type.");
        return NULL;
    }

    PyObject* result_array = PyArray_SimpleNew(PyArray_NDIM(mmmXYZTarget),
        PyArray_SHAPE(mmmXYZTarget),
        PyArray_TYPE(mmmXYZTarget));
    if (result_array == NULL)
        return NULL;
    size_t nPoints = PyArray_SIZE(mmmXYZTarget) / NCOORDSINPOINT;
    int isOriginSizeOfTargets = (PyArray_Size(rrmLLALocalOrigin) == PyArray_Size(mmmXYZTarget));
    if (PyArray_TYPE(rrmLLALocalOrigin) == NPY_DOUBLE) {
        double* data1 = (double*)PyArray_DATA(rrmLLALocalOrigin);
        double* data2 = (double*)PyArray_DATA(mmmXYZTarget);
        double* result_data = (double*)PyArray_DATA((PyArrayObject*)result_array);
        ECEF2ENUDouble(
            data1, data2, nPoints, isOriginSizeOfTargets, a, b, result_data);
    } else if (PyArray_TYPE(rrmLLALocalOrigin) == NPY_FLOAT) {
        float* data1 = (float*)PyArray_DATA(rrmLLALocalOrigin);
        float* data2 = (float*)PyArray_DATA(mmmXYZTarget);
        float* result_data = (float*)PyArray_DATA((PyArrayObject*)result_array);
        ECEF2ENUFloat(
            data1, data2, nPoints, isOriginSizeOfTargets, a, b, result_data);
    } else {
        PyErr_SetString(PyExc_ValueError,
            "Only 32 and 64 bit float types accepted.");
        return NULL;
    }
    return result_array;
}

static PyObject*
ENU2ECEFWrapper(PyObject* self, PyObject* args)
{
    PyArrayObject *rrmLLALocalOrigin, *mmmLocal;
    double a, b;

    // checks
    if (!PyArg_ParseTuple(args,
            "O!O!dd",
            &PyArray_Type,
            &rrmLLALocalOrigin,
            &PyArray_Type,
            &mmmLocal,
            &a,
            &b))
        return NULL;
    if (!(PyArray_ISCONTIGUOUS(rrmLLALocalOrigin)) || !(PyArray_ISCONTIGUOUS(mmmLocal))) {
        PyErr_SetString(PyExc_ValueError, "Input arrays must be a C contiguous.");
        return NULL;
    }
    if (!((PyArray_NDIM(rrmLLALocalOrigin) == PyArray_NDIM(mmmLocal)) && (PyArray_SIZE(rrmLLALocalOrigin) == PyArray_SIZE(mmmLocal)) || ((PyArray_Size(rrmLLALocalOrigin) == NCOORDSINPOINT) && (PyArray_SIZE(rrmLLALocalOrigin) < PyArray_SIZE(mmmLocal))))) {
        PyErr_SetString(PyExc_ValueError,
            "Input arrays must have matching size and dimensions or "
            "the origin must be of size three.");
        return NULL;
    }
    if ((PyArray_SIZE(rrmLLALocalOrigin) % NCOORDSINPOINT) != 0 || (PyArray_SIZE(mmmLocal) % NCOORDSINPOINT) != 0) {
        PyErr_SetString(PyExc_ValueError, "Input arrays must be a multiple of 3.");
        return NULL;
    }
    if (PyArray_TYPE(rrmLLALocalOrigin) != PyArray_TYPE(mmmLocal)) {
        PyErr_SetString(PyExc_ValueError, "Input arrays must have the same type.");
        return NULL;
    }

    PyObject* result_array = PyArray_SimpleNew(
        PyArray_NDIM(mmmLocal), PyArray_SHAPE(mmmLocal), PyArray_TYPE(mmmLocal));
    if (result_array == NULL)
        return NULL;
    size_t nPoints = PyArray_SIZE(mmmLocal) / NCOORDSINPOINT;
    int isOriginSizeOfTargets = (PyArray_Size(rrmLLALocalOrigin) == PyArray_Size(mmmLocal));
    if (PyArray_TYPE(rrmLLALocalOrigin) == NPY_DOUBLE) {
        double* data1 = (double*)PyArray_DATA(rrmLLALocalOrigin);
        double* data2 = (double*)PyArray_DATA(mmmLocal);
        double* result_data = (double*)PyArray_DATA((PyArrayObject*)result_array);
        ENU2ECEFDouble(
            data1, data2, nPoints, isOriginSizeOfTargets, a, b, result_data);
    } else if (PyArray_TYPE(rrmLLALocalOrigin) == NPY_FLOAT) {
        float* data1 = (float*)PyArray_DATA(rrmLLALocalOrigin);
        float* data2 = (float*)PyArray_DATA(mmmLocal);
        float* result_data = (float*)PyArray_DATA((PyArrayObject*)result_array);
        ENU2ECEFFloat(
            data1, data2, nPoints, isOriginSizeOfTargets, a, b, result_data);
    } else {
        PyErr_SetString(PyExc_ValueError,
            "Only 32 and 64 bit float types accepted.");
        return NULL;
    }
    return result_array;
}

static PyObject*
ENU2AERWrapper(PyObject* self, PyObject* args)
{
    PyArrayObject* mmmENU;

    // checks
    if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &mmmENU))
        return NULL;
    if (!(PyArray_ISCONTIGUOUS(mmmENU))) {
        PyErr_SetString(PyExc_ValueError, "Input arrays must be a C contiguous.");
        return NULL;
    }
    if ((PyArray_SIZE(mmmENU) % NCOORDSINPOINT) != 0) {
        PyErr_SetString(PyExc_ValueError, "Input arrays must be a multiple of 3.");
        return NULL;
    }

    PyObject* result_array = PyArray_SimpleNew(
        PyArray_NDIM(mmmENU), PyArray_SHAPE(mmmENU), PyArray_TYPE(mmmENU));
    if (result_array == NULL)
        return NULL;
    size_t nPoints = PyArray_SIZE(mmmENU) / NCOORDSINPOINT;
    if (PyArray_TYPE(mmmENU) == NPY_DOUBLE) {
        double* data1 = (double*)PyArray_DATA(mmmENU);
        double* result_data = (double*)PyArray_DATA((PyArrayObject*)result_array);
        ENU2AERDouble(data1, nPoints, result_data);
    } else if (PyArray_TYPE(mmmENU) == NPY_FLOAT) {
        float* data1 = (float*)PyArray_DATA(mmmENU);
        float* result_data = (float*)PyArray_DATA((PyArrayObject*)result_array);
        ENU2AERFloat(data1, nPoints, result_data);
    } else {
        PyErr_SetString(PyExc_ValueError,
            "Only 32 and 64 bit float types accepted.");
        return NULL;
    }
    return result_array;
}

static PyObject*
AER2ENUWrapper(PyObject* self, PyObject* args)
{
    PyArrayObject* rrmAER;

    // checks
    if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &rrmAER))
        return NULL;
    if (!(PyArray_ISCONTIGUOUS(rrmAER))) {
        PyErr_SetString(PyExc_ValueError, "Input arrays must be a C contiguous.");
        return NULL;
    }
    if ((PyArray_SIZE(rrmAER) % NCOORDSINPOINT) != 0) {
        PyErr_SetString(PyExc_ValueError, "Input arrays must be a multiple of 3.");
        return NULL;
    }

    PyObject* result_array = PyArray_SimpleNew(
        PyArray_NDIM(rrmAER), PyArray_SHAPE(rrmAER), PyArray_TYPE(rrmAER));
    if (result_array == NULL)
        return NULL;
    size_t nPoints = PyArray_SIZE(rrmAER) / NCOORDSINPOINT;
    if (PyArray_TYPE(rrmAER) == NPY_DOUBLE) {
        double* data1 = (double*)PyArray_DATA(rrmAER);
        double* result_data = (double*)PyArray_DATA((PyArrayObject*)result_array);
        AER2ENUDouble(data1, nPoints, result_data);
    } else if (PyArray_TYPE(rrmAER) == NPY_FLOAT) {
        float* data1 = (float*)PyArray_DATA(rrmAER);
        float* result_data = (float*)PyArray_DATA((PyArrayObject*)result_array);
        AER2ENUFloat(data1, nPoints, result_data);
    } else {
        PyErr_SetString(PyExc_ValueError,
            "Only 32 and 64 bit float types accepted.");
        return NULL;
    }
    return result_array;
}

// Method definition object for this extension, these argumens mean:
// ml_name: The name of the method
// ml_meth: Function pointer to the method implementation
// ml_flags: Flags indicating special features of this method, such as
//           accepting arguments, accepting keyword arguments, being a class
//           method, or being a static method of a class.
// ml_doc:  The docstring for the method
static PyMethodDef MyMethods[] = {
    { "geodetic2ECEF",
        geodetic2ECEFWrapper,
        METH_VARARGS,
        "Convert geodetic coordinate system to ECEF." },
    { "ECEF2geodetic",
        ECEF2geodeticWrapper,
        METH_VARARGS,
        "Convert ECEF to geodetic coordinate system." },
    { "ECEF2ENU", ECEF2ENUWrapper, METH_VARARGS, "Convert ECEF to ENU." },
    { "ENU2ECEF", ENU2ECEFWrapper, METH_VARARGS, "Convert ENU to ECEF." },
    { "ENU2AER", ENU2AERWrapper, METH_VARARGS, "Convert ENU to AER." },
    { "AER2ENU", AER2ENUWrapper, METH_VARARGS, "Convert AER to ENU." },
    { NULL, NULL, 0, NULL }
};

// Module definition
static struct PyModuleDef transforms = {
    PyModuleDef_HEAD_INIT,
    "transforms",
    "Module that contains transform functions.",
    -1,
    MyMethods
};

// Module initialization function
PyMODINIT_FUNC
PyInit_transforms(void)
{
    import_array(); // Initialize the NumPy C API
    return PyModule_Create(&transforms);
}
