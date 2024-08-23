//==================================================================================================
/**
  EVE - Expressive Vector Engine
  Copyright : EVE Project Contributors
  SPDX-License-Identifier: BSL-1.0
**/
//==================================================================================================
#pragma once

#include <eve/module/core/regular/abs.hpp>
#include <eve/module/core/regular/absmax.hpp>
#include <eve/module/core/regular/absmin.hpp>
#include <eve/module/core/regular/add.hpp>
#include <eve/module/core/regular/agm.hpp>
#include <eve/module/core/regular/all.hpp>
#include <eve/module/core/regular/any.hpp>
#include <eve/module/core/regular/average.hpp>
#include <eve/module/core/regular/binarize.hpp>
#include <eve/module/core/regular/binarize_not.hpp>
#include <eve/module/core/regular/bit_and.hpp>
#include <eve/module/core/regular/bit_andnot.hpp>
#include <eve/module/core/regular/bit_ceil.hpp>
#include <eve/module/core/regular/bit_floor.hpp>
#include <eve/module/core/regular/bit_mask.hpp>
#include <eve/module/core/regular/bit_not.hpp>
#include <eve/module/core/regular/bit_notand.hpp>
#include <eve/module/core/regular/bit_notor.hpp>
#include <eve/module/core/regular/bit_or.hpp>
#include <eve/module/core/regular/bit_ornot.hpp>
#include <eve/module/core/regular/bit_select.hpp>
#include <eve/module/core/regular/bit_shl.hpp>
#include <eve/module/core/regular/bit_shr.hpp>
#include <eve/module/core/regular/bit_width.hpp>
#include <eve/module/core/regular/bit_xor.hpp>
#include <eve/module/core/regular/bitofsign.hpp>
#include <eve/module/core/regular/broadcast.hpp>
#include <eve/module/core/regular/broadcast_group.hpp>
#include <eve/module/core/regular/ceil.hpp>
#include <eve/module/core/regular/clamp.hpp>
#include <eve/module/core/regular/combine.hpp>
#include <eve/module/core/regular/compress_store.hpp>
#include <eve/module/core/regular/conj.hpp>
#include <eve/module/core/regular/convert.hpp>
#include <eve/module/core/regular/converter.hpp>
#include <eve/module/core/regular/copysign.hpp>
#include <eve/module/core/regular/count_true.hpp>
#include <eve/module/core/regular/countl_one.hpp>
#include <eve/module/core/regular/countl_zero.hpp>
#include <eve/module/core/regular/countr_one.hpp>
#include <eve/module/core/regular/countr_zero.hpp>
#include <eve/module/core/regular/dec.hpp>
#include <eve/module/core/regular/deinterleave_groups.hpp>
#include <eve/module/core/regular/deinterleave_groups_shuffle.hpp>
#include <eve/module/core/regular/diff_of_prod.hpp>
#include <eve/module/core/regular/dist.hpp>
#include <eve/module/core/regular/div.hpp>
#include <eve/module/core/regular/epsilon.hpp>
#include <eve/module/core/regular/exponent.hpp>
#include <eve/module/core/regular/fam.hpp>
#include <eve/module/core/regular/fanm.hpp>
#include <eve/module/core/regular/fdim.hpp>
#include <eve/module/core/regular/first_true.hpp>
#include <eve/module/core/regular/firstbitset.hpp>
#include <eve/module/core/regular/firstbitunset.hpp>
#include <eve/module/core/regular/floor.hpp>
#include <eve/module/core/regular/fma.hpp>
#include <eve/module/core/regular/fmod.hpp>
#include <eve/module/core/regular/fms.hpp>
#include <eve/module/core/regular/fnma.hpp>
#include <eve/module/core/regular/fnms.hpp>
#include <eve/module/core/regular/frac.hpp>
#include <eve/module/core/regular/fracscale.hpp>
#include <eve/module/core/regular/frexp.hpp>
#include <eve/module/core/regular/fsm.hpp>
#include <eve/module/core/regular/fsnm.hpp>
#include <eve/module/core/regular/gather.hpp>
#include <eve/module/core/regular/has_single_bit.hpp>
#include <eve/module/core/regular/hi.hpp>
#include <eve/module/core/regular/if_else.hpp>
#include <eve/module/core/regular/ifnot_else.hpp>
#include <eve/module/core/regular/ifrexp.hpp>
#include <eve/module/core/regular/inc.hpp>
#include <eve/module/core/regular/interleave.hpp>
#include <eve/module/core/regular/interleave_shuffle.hpp>
#include <eve/module/core/regular/is_denormal.hpp>
#include <eve/module/core/regular/is_equal.hpp>
#include <eve/module/core/regular/is_eqz.hpp>
#include <eve/module/core/regular/is_even.hpp>
#include <eve/module/core/regular/is_finite.hpp>
#include <eve/module/core/regular/is_flint.hpp>
#include <eve/module/core/regular/is_gez.hpp>
#include <eve/module/core/regular/is_gtz.hpp>
#include <eve/module/core/regular/is_imag.hpp>
#include <eve/module/core/regular/is_infinite.hpp>
#include <eve/module/core/regular/is_less.hpp>
#include <eve/module/core/regular/is_less_equal.hpp>
#include <eve/module/core/regular/is_lessgreater.hpp>
#include <eve/module/core/regular/is_lez.hpp>
#include <eve/module/core/regular/is_ltz.hpp>
#include <eve/module/core/regular/is_nan.hpp>
#include <eve/module/core/regular/is_negative.hpp>
#include <eve/module/core/regular/is_ngez.hpp>
#include <eve/module/core/regular/is_ngtz.hpp>
#include <eve/module/core/regular/is_nlez.hpp>
#include <eve/module/core/regular/is_nltz.hpp>
#include <eve/module/core/regular/is_normal.hpp>
#include <eve/module/core/regular/is_not_denormal.hpp>
#include <eve/module/core/regular/is_not_equal.hpp>
#include <eve/module/core/regular/is_not_finite.hpp>
#include <eve/module/core/regular/is_not_flint.hpp>
#include <eve/module/core/regular/is_not_greater.hpp>
#include <eve/module/core/regular/is_not_greater_equal.hpp>
#include <eve/module/core/regular/is_not_imag.hpp>
#include <eve/module/core/regular/is_not_infinite.hpp>
#include <eve/module/core/regular/is_not_less.hpp>
#include <eve/module/core/regular/is_not_less_equal.hpp>
#include <eve/module/core/regular/is_not_nan.hpp>
#include <eve/module/core/regular/is_not_real.hpp>
#include <eve/module/core/regular/is_odd.hpp>
#include <eve/module/core/regular/is_ordered.hpp>
#include <eve/module/core/regular/is_positive.hpp>
#include <eve/module/core/regular/is_pow2.hpp>
#include <eve/module/core/regular/is_real.hpp>
#include <eve/module/core/regular/is_unordered.hpp>
#include <eve/module/core/regular/last_true.hpp>
#include <eve/module/core/regular/ldexp.hpp>
#include <eve/module/core/regular/lerp.hpp>
#include <eve/module/core/regular/lo.hpp>
#include <eve/module/core/regular/load.hpp>
#include <eve/module/core/regular/logical_andnot.hpp>
#include <eve/module/core/regular/logical_notand.hpp>
#include <eve/module/core/regular/logical_notor.hpp>
#include <eve/module/core/regular/logical_ornot.hpp>
#include <eve/module/core/regular/logical_xor.hpp>
#include <eve/module/core/regular/lohi.hpp>
#include <eve/module/core/regular/lookup.hpp>
#include <eve/module/core/regular/manhattan.hpp>
#include <eve/module/core/regular/mantissa.hpp>
#include <eve/module/core/regular/max.hpp>
#include <eve/module/core/regular/maxabs.hpp>
#include <eve/module/core/regular/maximum.hpp>
#include <eve/module/core/regular/maxmag.hpp>
#include <eve/module/core/regular/min.hpp>
#include <eve/module/core/regular/minabs.hpp>
#include <eve/module/core/regular/minimum.hpp>
#include <eve/module/core/regular/minmag.hpp>
#include <eve/module/core/regular/minus.hpp>
#include <eve/module/core/regular/modf.hpp>
#include <eve/module/core/regular/mul.hpp>
#include <eve/module/core/regular/nb_values.hpp>
#include <eve/module/core/regular/nearest.hpp>
#include <eve/module/core/regular/negabsmax.hpp>
#include <eve/module/core/regular/negabsmin.hpp>
#include <eve/module/core/regular/negate.hpp>
#include <eve/module/core/regular/negatenz.hpp>
#include <eve/module/core/regular/negmaxabs.hpp>
#include <eve/module/core/regular/negminabs.hpp>
#include <eve/module/core/regular/next.hpp>
#include <eve/module/core/regular/nextafter.hpp>
#include <eve/module/core/regular/none.hpp>
#include <eve/module/core/regular/oneminus.hpp>
#include <eve/module/core/regular/plus.hpp>
#include <eve/module/core/regular/popcount.hpp>
#include <eve/module/core/regular/prev.hpp>
#include <eve/module/core/regular/rat.hpp>
#include <eve/module/core/regular/read.hpp>
#include <eve/module/core/regular/rec.hpp>
#include <eve/module/core/regular/reduce.hpp>
#include <eve/module/core/regular/refine_rec.hpp>
#include <eve/module/core/regular/rem.hpp>
#include <eve/module/core/regular/remainder.hpp>
#include <eve/module/core/regular/remdiv.hpp>
#include <eve/module/core/regular/replace.hpp>
#include <eve/module/core/regular/reverse.hpp>
#include <eve/module/core/regular/rotl.hpp>
#include <eve/module/core/regular/rotr.hpp>
#include <eve/module/core/regular/round.hpp>
#include <eve/module/core/regular/roundscale.hpp>
#include <eve/module/core/regular/rshl.hpp>
#include <eve/module/core/regular/rshr.hpp>
#include <eve/module/core/regular/rsqrt.hpp>
#include <eve/module/core/regular/safe.hpp>
#include <eve/module/core/regular/saturate.hpp>
#include <eve/module/core/regular/scan.hpp>
#include <eve/module/core/regular/shl.hpp>
#include <eve/module/core/regular/shr.hpp>
#include <eve/module/core/regular/sign.hpp>
#include <eve/module/core/regular/sign_alternate.hpp>
#include <eve/module/core/regular/signnz.hpp>
#include <eve/module/core/regular/slide_left.hpp>
#include <eve/module/core/regular/slide_right.hpp>
#include <eve/module/core/regular/sqr.hpp>
#include <eve/module/core/regular/sqr_abs.hpp>
#include <eve/module/core/regular/sqrt.hpp>
#include <eve/module/core/regular/store.hpp>
#include <eve/module/core/regular/sub.hpp>
#include <eve/module/core/regular/sum_of_prod.hpp>
#include <eve/module/core/regular/swap_adjacent_groups.hpp>
#include <eve/module/core/regular/swap_if.hpp>
#include <eve/module/core/regular/three_fma.hpp>
#include <eve/module/core/regular/trunc.hpp>
#include <eve/module/core/regular/two_add.hpp>
#include <eve/module/core/regular/two_prod.hpp>
#include <eve/module/core/regular/two_split.hpp>
#include <eve/module/core/regular/ulpdist.hpp>
#include <eve/module/core/regular/unalign.hpp>
#include <eve/module/core/regular/unsafe.hpp>
#include <eve/module/core/regular/write.hpp>
