#include <Python.h>
#include <stdlib.h>
#include <linux/i2c-dev.h>
#include <fcntl.h>
#include <unistd.h>

#ifdef __arm__
#include <arm-linux-gnueabihf/sys/ioctl.h>
#else
#include <sys/ioctl.h>
#endif




// returns fd of i2c object
static PyObject* i2c_open(PyObject *self, PyObject *args)
{
	char i2c_filename[20];
	int count = 0, i2c_handle = -1;
	while (i2c_handle == -1 && (++count < 4))
	{
		sprintf(i2c_filename, "/dev/i2c-%d", count);
		i2c_handle = open(i2c_filename, O_RDWR);
	}

	// check that i2c device is valid
	if (i2c_handle == -1)
	{
		PyErr_SetString(PyExc_IOError, "Failed to open i2c interface");
	}

	return Py_BuildValue("i", i2c_handle);
}

// shuts down given i2c interface and frees the i2cBuffer
static PyObject* i2c_close(PyObject *self, PyObject *args)
{
	int i2c_handle;
	if (!PyArg_ParseTuple(args, "i", &i2c_handle))
		return NULL;

	if (close(i2c_handle) < 0)
		PyErr_SetFromErrno(PyExc_IOError);

	Py_RETURN_NONE;
}

/*
i2c_send(i2cHandle, address, bytes)
this function expects a ByteArray type
*/
static PyObject* i2c_send(PyObject *self, PyObject *args)
{
	int i2c_handle = 0;
	int address = 0;
	PyObject *array_of_bytes;
	
	// read arguments
	if (!PyArg_ParseTuple(args, "iiO", &i2c_handle, &address, &array_of_bytes))
		return NULL;

	// check that array_of_bytes is actually an array
	if (!PyByteArray_Check(array_of_bytes))
	{
		PyErr_SetString(PyExc_TypeError, "argument given was not a ByteArray");
		return NULL;
	}

	// get the pointer of the bytes to send
	int count = PyByteArray_Size(array_of_bytes);
	char *bytes = PyByteArray_AS_STRING(array_of_bytes);
	// set slave address
	if (ioctl(i2c_handle, I2C_SLAVE, address) < 0)
	{
		PyErr_SetFromErrno(PyExc_IOError);
		return NULL;
	}

	// write data to i2c bus
	if (write(i2c_handle, bytes, count) != count)
	{
		PyErr_SetFromErrno(PyExc_IOError);
		return NULL;
	}

	Py_RETURN_NONE;
}

/*
 *	performs a read on the given i2c interface and returns the bytes read
 *	arguments are:
 *		integer: i2c device handle
 *		integer: i2c slave address to read from
 *		integer: the number of bytes to read
 */
static PyObject* i2c_read(PyObject *self, PyObject *args)
{
	int i2c_handle = 0;
	int address = 0;
	int count = 0;

	if (!PyArg_ParseTuple(args, "iii", &i2c_handle, &address, &count))
		return NULL;

	if (count < 1)
	{
		PyErr_SetString(PyExc_TypeError, "cannot read less than one byte from i2c slave");
		return NULL;
	}

	// set slave address
	if (ioctl(i2c_handle, I2C_SLAVE, address) < 0)
	{
		PyErr_SetString(PyExc_TypeError, "failed to set i2c slave address");
		return NULL;
	}

	char* buffer = malloc(sizeof(char) * count);
	if (read(i2c_handle, buffer, count) != count)
	{
		PyErr_SetString(PyExc_TypeError, "failed to read the specified number of bytes from i2c device");
		return NULL;
	}

	PyObject* result = PyByteArray_FromStringAndSize(buffer, count);
	if (result == NULL)
	{
		if (buffer != NULL)
			free(buffer);

		PyErr_SetString(PyExc_TypeError, "failed to create return string after i2c read");
		return NULL;
	}

	if (buffer != NULL)
		free(buffer);
	return result;
}

static PyMethodDef PythonI2cMethods[] =
{
	{"i2c_open", i2c_open, METH_VARARGS, "Opens the first available i2c interface and return its file descriptor number"},
	{"i2c_close", i2c_close, METH_VARARGS, "Closes an already open i2c interface"},
	{"i2c_send", i2c_send, METH_VARARGS, "Sends bytearray down specified i2c interface to given address"},
	{"i2c_read", i2c_read, METH_VARARGS, "Reads count bytes from i2c slave"},
	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef python_i2c_module = {
	PyModuleDef_HEAD_INIT,
	"python_i2c",
	NULL,
	-1,
	PythonI2cMethods
};

PyMODINIT_FUNC PyInit_python_i2c(void)
{
	//(void) Py_InitModule("python_i2c", PythonI2cMethods);
	return PyModule_Create(&python_i2c_module);
}
