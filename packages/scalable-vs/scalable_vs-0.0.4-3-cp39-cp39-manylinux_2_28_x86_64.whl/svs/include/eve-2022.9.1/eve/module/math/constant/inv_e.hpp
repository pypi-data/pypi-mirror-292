//==================================================================================================
/*
  EVE - Expressive Vector Engine
  Copyright : EVE Project Contributors
  SPDX-License-Identifier: BSL-1.0
*/
//==================================================================================================
#pragma once

#include <eve/module/core.hpp>

namespace eve
{
//================================================================================================
//! @addtogroup math_constants
//! @{
//!   @var inv_e
//!   @brief Callable object computing the constant \f$e^{-1}\f$.
//!
//!   **Defined in Header**
//!
//!   @code
//!   #include <eve/module/math.hpp>
//!   @endcode
//!
//!   @groupheader{Callable Signatures}
//!
//!   @code
//!   namespace eve
//!   {
//!      template< eve::value T >
//!      T inv_e(as<T> x) noexcept;
//!   }
//!   @endcode
//!
//!   **Parameters**
//!
//!     * `x` :  [Type wrapper](@ref eve::as) instance embedding the type of the constant.
//!
//!    **Return value**
//!
//!      The call `eve::inv_e(as<T>())` returns athe inverse of the basis of the natural logarithms.
//!
//!  @groupheader{Example}
//!
//!  @godbolt{doc/math/inv_e.cpp}
//! @}
//================================================================================================
EVE_MAKE_CALLABLE(inv_e_, inv_e);

namespace detail
{
  template<floating_real_value T>
  EVE_FORCEINLINE auto inv_e_(EVE_SUPPORTS(cpu_), eve::as<T> const&) noexcept
  {
    using t_t = element_type_t<T>;
    if constexpr( std::is_same_v<t_t, float> ) return T(0x1.78b564p-2);
    else if constexpr( std::is_same_v<t_t, double> ) return T(0x1.78b56362cef38p-2);
  }

  template<floating_real_value T, typename D>
  EVE_FORCEINLINE constexpr auto inv_e_(EVE_SUPPORTS(cpu_), D const&, as<T> const&) noexcept
      requires(is_one_of<D>(types<upward_type, downward_type> {}))
  {
    using t_t = element_type_t<T>;
    if constexpr( std::is_same_v<D, upward_type> )
    {
      if constexpr( std::is_same_v<t_t, float> ) return T(0x1.78b564p-2);
      else if constexpr( std::is_same_v<t_t, double> ) return T(0x1.78b56362cef38p-2);
    }
    else if constexpr( std::is_same_v<D, downward_type> )
    {
      if constexpr( std::is_same_v<t_t, float> ) return T(0x1.78b562p-2);
      else if constexpr( std::is_same_v<t_t, double> ) return T(0x1.78b56362cef37p-2);
    }
  }
}
}
