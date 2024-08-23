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
//!   @var pio_6
//!   @brief Callable object computing the constant \f$\pi/6\f$.
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
//!      T pio_6(as<T> x) noexcept;
//!   }
//!   @endcode
//!
//!   **Parameters**
//!
//!     * `x` :  [Type wrapper](@ref eve::as) instance embedding the type of the constant.
//!
//!    **Return value**
//!
//!      The call `eve::pio_6(as<T>())` returns  \f$\pi/6\f$.
//!
//!  @groupheader{Example}
//!
//!  @godbolt{doc/math/pio_6.cpp}
//! @}
//================================================================================================
EVE_MAKE_CALLABLE(pio_6_, pio_6);

namespace detail
{
  template<floating_real_value T>
  EVE_FORCEINLINE auto pio_6_(EVE_SUPPORTS(cpu_), eve::as<T> const&) noexcept
  {
    using t_t = element_type_t<T>;
    if constexpr( std::is_same_v<t_t, float> ) return T(0x1.0c1524p-1);
    else if constexpr( std::is_same_v<t_t, double> ) return T(0x1.0c152382d7366p-1);
  }

  template<floating_real_value T, typename D>
  EVE_FORCEINLINE constexpr auto pio_6_(EVE_SUPPORTS(cpu_), D const&, as<T> const&) noexcept
      requires(is_one_of<D>(types<upward_type, downward_type> {}))
  {
    using t_t = element_type_t<T>;
    if constexpr( std::is_same_v<D, upward_type> )
    {
      if constexpr( std::is_same_v<t_t, float> ) return T(0x1.0c1524p-1);
      else if constexpr( std::is_same_v<t_t, double> ) return T(0x1.0c152382d7366p-1);
    }
    else if constexpr( std::is_same_v<D, downward_type> )
    {
      if constexpr( std::is_same_v<t_t, float> ) return T(0x1.0c1522p-1);
      else if constexpr( std::is_same_v<t_t, double> ) return T(0x1.0c152382d7365p-1);
    }
  }
}
}
