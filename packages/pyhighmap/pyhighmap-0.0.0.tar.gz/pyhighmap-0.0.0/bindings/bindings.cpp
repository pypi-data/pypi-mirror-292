/* Copyright (c) 2024 Otto Link. Distributed under the terms of the GNU General
 * Public License. The full license is in the file LICENSE, distributed with
 * this software. */
#define PYBIND11_DETAILED_ERROR_MESSAGES
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "highmap.hpp"

#include "helpers.hpp"

namespace py = pybind11;

PYBIND11_MODULE(pyhighmap, m)
{
  // py::class_<hmap::Vec2<int>>(m, "Vec2Int")
  //     .def(py::init<>())
  //     .def(py::init<int, int>())
  //     .def_readwrite("x", &hmap::Vec2<int>::x)
  //     .def_readwrite("y", &hmap::Vec2<int>::y);

  // py::class_<hmap::Vec2<float>>(m, "Vec2Float")
  //     .def(py::init<>())
  //     .def(py::init<float, float>())
  //     .def_readwrite("x", &hmap::Vec2<float>::x)
  //     .def_readwrite("y", &hmap::Vec2<float>::y);

  // py::class_<hmap::Vec4<float>>(m, "Vec4Float")
  //     .def(py::init<>())
  //     .def(py::init<float, float, float, float>())
  //     .def_readwrite("a", &hmap::Vec4<float>::a)
  //     .def_readwrite("b", &hmap::Vec4<float>::b)
  //     .def_readwrite("c", &hmap::Vec4<float>::c)
  //     .def_readwrite("d", &hmap::Vec4<float>::d);

  py::class_<hmap::Array>(m, "Array")
      .def(py::init<>())
      .def_readwrite("vector", &hmap::Array::vector)
      .def("to_npy",
           [](const hmap::Array &obj)
           {
             std::vector<size_t> size = {static_cast<size_t>(obj.shape.x),
                                         static_cast<size_t>(obj.shape.y)};
             return vector_to_numpy(obj.vector, size);
           });

  py::enum_<hmap::NoiseType>(m, "NoiseType")
      .value("PARBERRY", hmap::NoiseType::PARBERRY)
      .value("PERLIN", hmap::NoiseType::PERLIN)
      .value("PERLIN_BILLOW", hmap::NoiseType::PERLIN_BILLOW)
      .value("PERLIN_HALF", hmap::NoiseType::PERLIN_HALF)
      .value("SIMPLEX2", hmap::NoiseType::SIMPLEX2)
      .value("SIMPLEX2S", hmap::NoiseType::SIMPLEX2S)
      .value("VALUE", hmap::NoiseType::VALUE)
      .value("VALUE_CUBIC", hmap::NoiseType::VALUE_CUBIC)
      // .value("VALUE_DELAUNAY", hmap::NoiseType::VALUE_DELAUNAY)
      // .value("VALUE_LINEAR", hmap::NoiseType::VALUE_LINEAR)
      .value("WORLEY", hmap::NoiseType::WORLEY)
      .value("WORLEY_DOUBLE", hmap::NoiseType::WORLEY_DOUBLE)
      .value("WORLEY_VALUE", hmap::NoiseType::WORLEY_VALUE)
      .export_values();

  m.def("noise",
        [](hmap::NoiseType noise_type,
           py::object      shape_obj,
           py::object      kw_obj,
           uint            seed)
        {
          hmap::Array array = hmap::noise(noise_type,
                                          pyobj_to_vec2<int>(shape_obj),
                                          pyobj_to_vec2<float>(kw_obj),
                                          seed);
          return array_to_numpy(array);
        });

  m.def(
      "noise_fbm",
      [](hmap::NoiseType noise_type,
         py::object      shape_obj,
         py::object      kw_obj,
         uint            seed,
         int             octaves,
         float           weight,
         float           persistence,
         float           lacunarity)
      {
        hmap::Array array = hmap::noise_fbm(noise_type,
                                            pyobj_to_vec2<int>(shape_obj),
                                            pyobj_to_vec2<float>(kw_obj),
                                            seed,
                                            octaves,
                                            weight,
                                            persistence,
                                            lacunarity);
        return array_to_numpy(array);
      },
      py::arg("noise_type"),
      py::arg("shape_obj"),
      py::arg("kw_obj"),
      py::arg("seed"),
      py::arg("octaves") = 8,
      py::arg("weight") = 0.7f,
      py::arg("persistence") = 0.5f,
      py::arg("lacunarity") = 2.f);
}
