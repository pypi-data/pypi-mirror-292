/* Implementation of python-bind-helper.
   Copyright (C) 2019-2020 MINES ParisTech
   This file is part of the python-bind-helper library.

   The solar_geometry library is free software; you can redistribute it and/or
   modify it under the terms of the GNU Lesser General Public
   License as published by the Free Software Foundation; either
   version 3.0 of the License, or (at your option) any later version.

   The solar_geometry library is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   Lesser General Public License for more details.

   You should have received a copy of the GNU Lesser General Public
   License along with the solar_geometry library; if not, see
   <http://www.gnu.org/licenses/>.

   Authors:
     Benoit Gschwind <benoit.gschwind@mines-paristech.fr>

*/

#ifndef __PYTHON_BIND_HELPER_HXX__

#include <tuple>

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>
#include <numpy/npy_common.h>
#include <numpy/ufuncobject.h>

#include <iostream>
#include <string>

namespace python_bind_helper {

template<typename T>
struct _ufunc_extract_signature;

template<typename R, typename A0, typename A1, typename A2, typename A3>
struct _ufunc_extract_signature<R(*)(A0,A1,A2,A3)> {
	using ARG0 = A0;
	using ARG1 = A1;
	using ARG2 = A2;
	using ARG3 = A3;
};

using _ufunc_types = _ufunc_extract_signature<PyUFuncGenericFunction>;

template<typename ... ARGS>
void fold(ARGS && ... args) { }


template <std::size_t ...>
struct index_sequence { };

template <std::size_t N, std::size_t ... TAIL>
struct _index_sequence : public _index_sequence<N-1, N-1, TAIL...> { };

template <std::size_t ... TAIL>
struct _index_sequence<0U, TAIL ... > {
	using type = index_sequence<TAIL ... >;
};

template <std::size_t N>
using make_index_sequence = typename _index_sequence<N>::type;


// convenient function for debuging.
inline std::string _python_repr(PyObject *obj)
{
    PyObject* repr = PyObject_Repr(obj);
    PyObject* str = PyUnicode_AsEncodedString(repr, "utf-8", "strict");
    auto ret = std::string{PyBytes_AS_STRING(str)};
    Py_XDECREF(repr);
    Py_XDECREF(str);
    return ret;
}

// convenient function for debuging.
inline std::string _python_str(PyObject *obj)
{
    PyObject* repr = PyObject_Str(obj);
    PyObject* str = PyUnicode_AsEncodedString(repr, "utf-8", "strict");
    auto ret = std::string{PyBytes_AS_STRING(str)};
    Py_XDECREF(repr);
    Py_XDECREF(str);
    return ret;
}

template<typename>
struct _python_bind_type_info;

template<>
struct _python_bind_type_info<double> {
	enum : int { npy_type = NPY_DOUBLE };

	static PyObject * format() {
		return Py_BuildValue("s", "f8");
	}

};

template<>
struct _python_bind_type_info<float> {
	enum : int { npy_type = NPY_FLOAT };
	static PyObject * format() {
		return Py_BuildValue("s", "f8");
	}
};

template<>
struct _python_bind_type_info<int64_t> {
	enum : int { npy_type = NPY_INT64 };
	static PyObject * format() {
		return Py_BuildValue("s", "i8");
	}
};

template<>
struct _python_bind_type_info<int32_t> {
	enum : int { npy_type = NPY_INT32 };
	static PyObject * format() {
		return Py_BuildValue("s", "i4");
	}
};

template<>
struct _python_bind_type_info<int16_t> {
	enum : int { npy_type = NPY_INT16 };
	static PyObject * format() {
		return Py_BuildValue("s", "i2");
	}
};

template<>
struct _python_bind_type_info<char> {
	enum : int { npy_type = NPY_INT8 };
	static PyObject * format() {
		return Py_BuildValue("s", "i1");
	}
};

template<>
struct _python_bind_type_info<uint64_t> {
	enum : int { npy_type = NPY_UINT64 };
	static PyObject * format() {
		return Py_BuildValue("s", "u8");
	}
};

template<>
struct _python_bind_type_info<uint32_t> {
	enum : int { npy_type = NPY_UINT32 };
	static PyObject * format() {
		return Py_BuildValue("s", "u4");
	}
};

template<>
struct _python_bind_type_info<uint16_t> {
	enum : int { npy_type = NPY_UINT16 };
	static PyObject * format() {
		return Py_BuildValue("s", "u2");
	}
};

template<>
struct _python_bind_type_info<uint8_t> {
	enum : int { npy_type = NPY_UINT8 };
	static PyObject * format() {
		return Py_BuildValue("s", "u1");
	}
};

template<typename F, F &FUNC>
struct build_ufunc;

// If return type is a tuple
template<typename O_ARGS, typename ... I_ARGS, O_ARGS(&FUNC)(I_ARGS...)>
class build_ufunc<O_ARGS(I_ARGS...), FUNC>
{
	char types[sizeof...(I_ARGS) + 1]; // handle function signature
	PyUFuncGenericFunction func[1]; // handle vectorized function
	void * data[1]; // handle extra data (not used by us currently

	std::string name;
	std::string doc;

	enum : int { ISIZE = sizeof...(I_ARGS) };

	using ISEQ_TYPE = make_index_sequence<ISIZE>;

	template<typename T>
	static inline T & _assign(T & dst, T && src) { return dst = src; }

	template<typename>
	struct _update_types;

	template<std::size_t ... ISEQ>
	struct _update_types<index_sequence<ISEQ...>>
	{
		static void update(char * types)
		{
			fold(_assign<char>(types[ISEQ], _python_bind_type_info<I_ARGS>::npy_type)...);
			fold(_assign<char>(types[ISIZE], _python_bind_type_info<O_ARGS>::npy_type));
		}
	};

	template<typename T>
	struct data_handler {
		char * const   _base;
		npy_intp const _step;

		data_handler(char * base, npy_intp step) : _base{base}, _step{step} { }

		T & operator[](int i)
		{
			return *reinterpret_cast<T*>(_base+_step*i);
		};
	};

	template<typename>
	struct _final;

	template<std::size_t ... ISEQ>
	struct _final<index_sequence<ISEQ...>>
	{
		static void call(_ufunc_types::ARG0 args, _ufunc_types::ARG1 dimensions, _ufunc_types::ARG2 steps, _ufunc_types::ARG3 extra)
		{
		    auto inputs  = std::make_tuple(data_handler<I_ARGS>{args[ISEQ], steps[ISEQ]}...);
		    auto outputs = data_handler<O_ARGS>{args[ISIZE], steps[ISIZE]};
		    npy_intp const n = dimensions[0];
		    for (int i = 0; i < n; i++) {
				outputs[i] = FUNC(std::get<ISEQ>(inputs)[i]...);
		     }
		}
	};

	static void ufunc(_ufunc_types::ARG0 args, _ufunc_types::ARG1 dimensions, _ufunc_types::ARG2 steps, _ufunc_types::ARG3 extra)
	{
		_final<ISEQ_TYPE>::call(args, dimensions, steps, extra);
	}

	PyObject * create_ufunc()
	{
		return PyUFunc_FromFuncAndData(func, data, types, 1, ISIZE, 1, PyUFunc_None, name.c_str(), doc.c_str(), 0);
	}

public:
	build_ufunc(std::string const & name, std::string const & doc = "") :
		func{&ufunc}, data{nullptr}, name{name}, doc{doc}
	{
		_update_types<ISEQ_TYPE>::update(types);
	}

	void register_to(PyObject * module)
	{
	    auto ufunc = create_ufunc();
	    auto d = PyModule_GetDict(module);
	    PyDict_SetItemString(d, name.c_str(), ufunc);
	    Py_DECREF(ufunc);
	}

};

// If return type is a tuple
template<typename ... O_ARGS, typename ... I_ARGS, std::tuple<O_ARGS...>(&FUNC)(I_ARGS...)>
class build_ufunc<std::tuple<O_ARGS...>(I_ARGS...), FUNC>
{
	char types[sizeof...(I_ARGS) + sizeof...(O_ARGS)]; // handle function signature
	PyUFuncGenericFunction func[1]; // handle vectorized function
	void * data[1]; // handle extra data (not used by us currently

	std::string name;
	std::string doc;

	enum : int { ISIZE = sizeof...(I_ARGS) };
	enum : int { OSIZE = sizeof...(O_ARGS) };

	using ISEQ_TYPE = make_index_sequence<ISIZE>;
	using OSEQ_TYPE = make_index_sequence<OSIZE>;

	template<typename T>
	static inline T & _assign(T & dst, T && src) { return dst = src; }

	template<typename, typename>
	struct _update_types;

	template<std::size_t ... ISEQ, std::size_t ... OSEQ>
	struct _update_types<index_sequence<ISEQ...>, index_sequence<OSEQ...>>
	{
		static void update(char * types)
		{
			fold(_assign<char>(types[ISEQ], _python_bind_type_info<I_ARGS>::npy_type)...);
			fold(_assign<char>(types[ISIZE+OSEQ], _python_bind_type_info<O_ARGS>::npy_type)...);
		}
	};


	template<typename T>
	struct data_handler {
		char * const   _base;
		npy_intp const _step;

		data_handler(char * base, npy_intp step) : _base{base}, _step{step} { }

		T & operator[](int i)
		{
			return *reinterpret_cast<T*>(_base+_step*i);
		};
	};

	template<typename, typename>
	struct _final;

	template<std::size_t ... ISEQ, std::size_t ... OSEQ>
	struct _final<index_sequence<ISEQ...>, index_sequence<OSEQ...>>
	{
		static void call(_ufunc_types::ARG0 args, _ufunc_types::ARG1 dimensions, _ufunc_types::ARG2 steps, _ufunc_types::ARG3 extra)
		{
		    auto inputs  = std::make_tuple(data_handler<I_ARGS>{args[ISEQ], steps[ISEQ]}...);
		    auto outputs = std::make_tuple(data_handler<O_ARGS>{args[ISIZE+OSEQ], steps[ISIZE+OSEQ]}...);
		    npy_intp const n = dimensions[0];
		    for (int i = 0; i < n; i++) {
				std::tie(std::get<OSEQ>(outputs)[i]...) = FUNC(std::get<ISEQ>(inputs)[i]...);
		     }
		}
	};

	static void ufunc(_ufunc_types::ARG0 args, _ufunc_types::ARG1 dimensions, _ufunc_types::ARG2 steps, _ufunc_types::ARG3 extra)
	{
		_final<ISEQ_TYPE, OSEQ_TYPE>::call(args, dimensions, steps, extra);
	}

	PyObject * create_ufunc()
	{
		return PyUFunc_FromFuncAndData(func, data, types, 1, ISIZE, OSIZE, PyUFunc_None, name.c_str(), doc.c_str(), 0);
	}

public:
	build_ufunc(std::string const & name, std::string const & doc = "") :
		func{&ufunc}, data{nullptr}, name{name}, doc{doc}
	{
		_update_types<ISEQ_TYPE, OSEQ_TYPE>::update(types);
	}


	void register_to(PyObject * module)
	{
	    auto ufunc = create_ufunc();
	    auto d = PyModule_GetDict(module);
	    PyDict_SetItemString(d, name.c_str(), ufunc);
	    Py_DECREF(ufunc);
	}

};

} // python_bind_helper

#endif // __PYTHON_BIND_HELPER_HXX__



