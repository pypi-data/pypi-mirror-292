#include "helpers.hpp"

py::array_t<float> vector_to_numpy(const std::vector<float>  &vec,
                                   const std::vector<size_t> &size)
{
  return py::array_t<float>(size, vec.data());
}

py::array_t<float> array_to_numpy(const hmap::Array &array)
{
  std::vector<size_t> size = {static_cast<size_t>(array.shape.x),
                              static_cast<size_t>(array.shape.y)};
  return py::array_t<float>(size, array.vector.data());
}
