# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Numerics for fp8."""

from aqt.jax.v2 import utils
from aqt.jax.v2.numerics import numerics
import jax
import jax.numpy as jnp


float_repr = jax.Array


@utils.flax_slots_kw_only_dataclass
class FpNumericsConfig:
  nexp: int
  minexp: int
  nmant: int
  has_subnormals: bool
  has_two_nan: bool
  has_naninf: bool

e3m0 = FpNumericsConfig(
    nexp=3,
    minexp=0,
    nmant=0,
    has_subnormals=False,
    has_two_nan=False,
    has_naninf=False,
)

e3m0_ocp = FpNumericsConfig(
    nexp=3,
    minexp=0,
    nmant=0,
    has_subnormals=True,
    has_two_nan=False,
    has_naninf=False,
)

e2m1 = FpNumericsConfig(
    nexp=2,
    minexp=0,
    nmant=1,
    has_subnormals=False,
    has_two_nan=False,
    has_naninf=False,
)

e2m1_ocp = FpNumericsConfig(
    nexp=2,
    minexp=0,
    nmant=1,
    has_subnormals=True,
    has_two_nan=False,
    has_naninf=False,
)

e1m0 = FpNumericsConfig(
    nexp=1,
    minexp=0,
    nmant=0,
    has_subnormals=False,
    has_two_nan=False,
    has_naninf=False,
)

float8_e4m3fn = FpNumericsConfig(
    nexp=4,
    minexp=-6,
    nmant=3,
    has_subnormals=True,
    has_two_nan=True,
    has_naninf=False,
)

float8_e5m2 = FpNumericsConfig(
    nexp=5,
    minexp=-14,
    nmant=2,
    has_subnormals=True,
    has_two_nan=False,
    has_naninf=True,
)

float16 = FpNumericsConfig(
    nexp=5,
    minexp=-14,
    nmant=10,
    has_subnormals=True,
    has_two_nan=False,
    has_naninf=True,
)


# TODO(lew): Add minexp.
def fp_round(
    x,
    *,
    cfg: FpNumericsConfig,
    key: jax.Array,
    stochastic_rounding: bool,
    test_noise_axis=None,
):
  """FP stochastic rounding for a given mantissa and exponent. Returns bf16."""
  nexp = cfg.nexp
  nmant = cfg.nmant
  assert cfg.minexp == 0, 'minexp not implemented'
  assert not cfg.has_two_nan, 'two_nan not implemented'
  assert not cfg.has_naninf, 'naninf not implemented'

  orig_x = x
  input_dtype = x.dtype
  total_bits = jnp.finfo(input_dtype).bits
  # (sign, exp, mantissa) = (1,8,x)
  msg = f'Unsupported dtype for sthochastic rounding: {input_dtype}.'
  assert input_dtype == jnp.bfloat16 or input_dtype == jnp.float32, msg
  # bf16 bit pattern: seeeeeeeemmmmmmm
  #                   7654321076543210
  container_man = jnp.finfo(input_dtype).nmant
  bits_dtype = jnp.uint16 if total_bits == 16 else jnp.uint32
  assert nmant <= container_man, 'bf16 man bits'
  man_trunc_bits = container_man - nmant  # e2m1 in bf16: 7-1
  # example e2m1 in bf16: man_trunc_mask = 0b0000000000111111  (7-1 1s)
  man_trunc_mask = bits_dtype((1 << man_trunc_bits) - 1)  # 0b00000000_00111111

  # TODO(lew): We can use smaller dtype
  x = jax.lax.bitcast_convert_type(x, bits_dtype)  # adds noise to man
  if stochastic_rounding:
    if test_noise_axis is not None:
      noise_axis_size = x.shape[test_noise_axis]
      sh = list((1,) * len(x.shape))
      sh[test_noise_axis] = noise_axis_size
      rnd_bits = jnp.arange(noise_axis_size, dtype=bits_dtype).reshape(sh)
    else:
      rnd_bits = jax.random.bits(key, x.shape, bits_dtype)
    noise = jax.lax.convert_element_type(rnd_bits, bits_dtype) & man_trunc_mask
  else:
    # example e2m1 in bf16: noise = 0b0000000000100000  (shift = 7-1 - 1)
    noise = 1 << (man_trunc_bits - 1)  #  represents 0.5 in the container
    noise = jax.lax.convert_element_type(noise, bits_dtype)
  # This noise add might overflow up to sign bit if x(bf16) has max exp.
  # In bf16 this happens if x=nan or x=inf.
  x = x + noise  # uint addition, potential carry into exponent, this is correct
  x = jax.lax.bitwise_and(x, ~man_trunc_mask)  # zero-out lowest "6" bits in man

  if nexp is not None:
    # We use 1 as a minimal representable value. TODO(lew): use cfg.minexp.
    # We will clip to [1, 2^(2**nexp - 1) * (2-1 ^ nmant)] interval.
    assert input_dtype == jnp.bfloat16
    # min_exp = jnp.uint16(0b0_10000000_0000000)
    # max_exp = jnp.uint16(0b0_10000111_0000000)
    # bf16_exp_bias = jnp.uint16(0b0_01111111)
    min_exp = jnp.uint16(0b0_01111111) - (1 if cfg.has_subnormals else 0)
    max_exp = min_exp + 2**nexp - 1

    min_repr = min_exp << container_man
    # min_repr_float is used to select which SR to use.
    min_repr_float = jax.lax.bitcast_convert_type(min_repr, input_dtype)
    # container_mant_mask is 0b0000_0000_0111_1111
    container_mant_mask = bits_dtype((1 << container_man) - 1)
    # max_mant for e2m1 in bf16: 0b0000_0000_0100_0000
    max_mant = jnp.uint16(container_mant_mask & ~man_trunc_mask)
    max_repr = (max_exp << container_man) + max_mant

    sign_mask = jnp.uint16(0b1_00000000_0000000)
    sign = jax.lax.bitwise_and(x, sign_mask)
    abs_x = jax.lax.bitwise_and(x, ~sign_mask)
    # TODO(lew): we can do faster clipping with bit twiddling
    # Clipping of positive values in int domain is the same as in float.
    clip_x = jnp.clip(abs_x, min_repr, max_repr)  # sign bit is 0
    x = jax.lax.bitwise_or(sign, clip_x)
    x = jax.lax.bitcast_convert_type(x, input_dtype)
    if cfg.has_subnormals:
      # In simulated numerics, what We would like to represent as a subnormal is
      #    sign * 2^min_exp * (0.mantissa_s) = sign * (0.mantissa_s)
      # However, in container format, the same number is represented by
      #    sign * 2^(min_exp-1) * (1.mantissa) = sign * 0.5 * (1.mantissa_c)
      # Note that they are different in bit repr and mantissa_s != mantissa_c.
      # So we cannot directly truncate mantissa_c to get mantissa_s.
      # Also note that the container subnormal is never hit when simulating
      # the low-precision numerics.
      # Alternatively, we can simply do integer rounding inside the subnormal
      # regime since it is linear.
      orig_x_bit_repr = jax.lax.bitcast_convert_type(orig_x, bits_dtype)
      orig_abs_x = jax.lax.bitwise_and(orig_x_bit_repr, ~sign_mask)
      orig_clip_x = jnp.clip(orig_abs_x, min_repr, max_repr)
      exp = jax.lax.bitwise_and(orig_clip_x, ~container_mant_mask)
      if stochastic_rounding:
        if test_noise_axis is not None:
          noise_axis_size = x.shape[test_noise_axis]
          sh = list((1,) * len(x.shape))
          sh[test_noise_axis] = noise_axis_size
          rnd_bits = jnp.arange(noise_axis_size, dtype=bits_dtype).reshape(sh)
          rnd_bits = rnd_bits << 8
          rnd_bits = (jnp.uint32(rnd_bits) << 7) | jnp.float32(1).view(
              jnp.uint32
          )
          noise = (
              jax.lax.bitcast_convert_type(rnd_bits, jnp.float32)
              - 1.5
              + 1.0 / 512  # to make noise symmetric to zero
          )
        else:
          noise = jax.random.uniform(key, orig_x.shape, dtype=jnp.float32) - 0.5
      else:
        noise = 0.0
      # SR within subnormal is adding random noise [-0.5, 0.5) then round.
      subnormal = (jnp.round(orig_x * 2**nmant + noise) / 2**nmant).astype(
          input_dtype
      )
      x = jnp.where(exp == (min_exp << container_man), subnormal, x)
    else:
      # Rounding of values in [-1, 1] interval follows different logic.
      if stochastic_rounding:
        assert bits_dtype == jnp.uint16
        if test_noise_axis is not None:
          noise_axis_size = x.shape[test_noise_axis]
          sh = list((1,) * len(x.shape))
          sh[test_noise_axis] = noise_axis_size
          rnd_bits = jnp.arange(noise_axis_size, dtype=bits_dtype).reshape(sh)
          rnd_bits = rnd_bits << 8
        else:
          rnd_bits = jax.random.bits(key, x.shape, bits_dtype)
        rnd_bits = (jnp.uint32(rnd_bits) << 7) | jnp.float32(2).view(jnp.uint32)
        # rnd_bits here is 32 bits, with exponent 10000000, first 8 mantissa
        # being the generated "noise" and the rest of mantissa being 0.
        # Sign bit is 0.
        rnd_floats = jax.lax.bitcast_convert_type(rnd_bits, jnp.float32) - (
            3.0 - 2 ** (-16)
        )
        # rx is 1 or -1 - SR of orig_x
        rx = (orig_x > rnd_floats) * 2 - 1.0
        x = jnp.where(jnp.abs(orig_x) < min_repr_float, rx, x)
  else:
    x = jax.lax.bitcast_convert_type(x, input_dtype)

  return x


def fp_round_new(
    x,
    *,
    cfg: FpNumericsConfig,
    key: jax.Array,
    stochastic_rounding: bool,
    test_noise_axis=None,
):
  """FP stochastic rounding for a given mantissa and exponent. Returns bf16."""
  # This function is identical to fp_round but with improved readability.
  # Information about the numerics to be simulated
  nexp = cfg.nexp
  nmant = cfg.nmant
  assert cfg.minexp == 0, 'minexp not implemented'
  assert not cfg.has_two_nan, 'two_nan not implemented'
  assert not cfg.has_naninf, 'naninf not implemented'

  # Information about the container
  # BF16 bit pattern: (sign, exp, mantissa) = (1,8,x)
  # Notation: ctner = container
  input_dtype = x.dtype
  msg = f'Unsupported dtype for sthochastic rounding: {input_dtype}.'
  assert input_dtype == jnp.bfloat16, msg
  ctner_total_bits = jnp.finfo(input_dtype).bits
  ctner_nmant = jnp.finfo(input_dtype).nmant
  assert nmant <= ctner_nmant, 'bf16 man bits'
  bits_dtype = jnp.uint16

  # Masks
  ctner_mant_mask = bits_dtype((1 << ctner_nmant) - 1)  # 0_00000000_1111111
  mant_trunc_bits = ctner_nmant - nmant
  # Mantissa truncation mask:
  #     exp    nmant
  # 0_00000000_0..0011
  mant_trunc_mask = bits_dtype((1 << mant_trunc_bits) - 1)
  sign_mask = bits_dtype(0b1 << (ctner_total_bits - 1))

  min_normal = jax.lax.convert_element_type(2**cfg.minexp, input_dtype)
  min_normal_repr = jax.lax.bitcast_convert_type(min_normal, bits_dtype)
  bias = 1 if cfg.has_subnormals else 0
  ctner_bias = 127
  min_ctner_exp = bits_dtype(ctner_bias - bias)
  max_ctner_exp = bits_dtype(min_ctner_exp + 2**nexp - 1)
  max_ctner_mant = bits_dtype(ctner_mant_mask & ~mant_trunc_mask)
  max_normal_repr = (max_ctner_exp << ctner_nmant) + max_ctner_mant
  max_normal = jax.lax.bitcast_convert_type(max_normal_repr, input_dtype)

  def trunc_and_clip_normal(x_in: float_repr) -> float_repr:
    sign = jnp.sign(x_in)
    x_in = jnp.abs(x_in)
    x_in = jax.lax.bitcast_convert_type(x_in, bits_dtype)
    if stochastic_rounding:
      if test_noise_axis is not None:
        noise_axis_size = x_in.shape[test_noise_axis]
        sh = list((1,) * len(x_in.shape))
        sh[test_noise_axis] = noise_axis_size
        rnd_bits = jnp.arange(noise_axis_size, dtype=bits_dtype).reshape(sh)
      else:
        rnd_bits = jax.random.bits(key, x_in.shape, bits_dtype)
      noise = jax.lax.bitwise_and(rnd_bits, mant_trunc_mask)
      x_in = x_in + noise
    else:
      carry_bit = bits_dtype(1 << (mant_trunc_bits - 1))
      x_in = x_in + carry_bit
    x_in = jax.lax.bitwise_and(x_in, ~mant_trunc_mask)
    x_in = jax.lax.bitcast_convert_type(x_in, input_dtype)
    if nexp is not None:
      x_in = jnp.clip(x_in, min_normal, max_normal)
    return x_in * sign

  def round_subnormal(x_in: float_repr) -> float_repr:
    if cfg.has_subnormals:
      if stochastic_rounding:
        if test_noise_axis is not None:
          noise_axis_size = x_in.shape[test_noise_axis]
          sh = list((1,) * len(x_in.shape))
          sh[test_noise_axis] = noise_axis_size
          rnd_bits = jnp.arange(noise_axis_size, dtype=bits_dtype).reshape(sh)
          rnd_bits = rnd_bits << 8
          rnd_bits = (jnp.uint32(rnd_bits) << 7) | jnp.float32(1).view(
              jnp.uint32
          )
          noise = (
              jax.lax.bitcast_convert_type(rnd_bits, jnp.float32)
              - 1.5
              + 0.001953125  # to make noise symmetric to zero
          )
        else:
          noise = jax.random.uniform(key, x_in.shape, dtype=jnp.float32) - 0.5
      else:
        noise = 0.0
      x_in = (jnp.round(x_in * 2**nmant + noise) / 2**nmant).astype(input_dtype)
    else:
      if stochastic_rounding:
        if test_noise_axis is not None:
          noise_axis_size = x_in.shape[test_noise_axis]
          sh = list((1,) * len(x_in.shape))
          sh[test_noise_axis] = noise_axis_size
          rnd_bits = jnp.arange(noise_axis_size, dtype=bits_dtype).reshape(sh)
          rnd_bits = rnd_bits << 8
        else:
          rnd_bits = jax.random.bits(key, x_in.shape, bits_dtype)
        rnd_bits = (jnp.uint32(rnd_bits) << 7) | jnp.float32(2).view(jnp.uint32)
        rnd_floats = jax.lax.bitcast_convert_type(rnd_bits, jnp.float32) - (
            3.0 - 2 ** (-16)
        )
        x_in = (x_in > rnd_floats) * 2 - 1.0
      else:
        sign = jax.lax.bitwise_and(
            jax.lax.bitcast_convert_type(x_in, bits_dtype), sign_mask
        )
        x_in = jax.lax.bitwise_or(sign, min_normal_repr)
        x_in = jax.lax.bitcast_convert_type(x_in, input_dtype)
    return x_in

  normal = trunc_and_clip_normal(x)
  subnormal = round_subnormal(x)
  out = jnp.where(jnp.abs(x) < min_normal, subnormal, normal)
  return out


def fp_largest_representable(cfg: FpNumericsConfig):
  nexp = cfg.nexp
  nmant = cfg.nmant
  assert cfg.minexp == 0, 'minexp not implemented'
  assert not cfg.has_naninf, 'naninf not implemented'
  max_exp = 2**nexp - 1 + cfg.minexp - (1 if cfg.has_subnormals else 0)
  max_mant = 2**nmant - 1 - (1 if cfg.has_two_nan else 0)
  return 2**max_exp * (1 + (max_mant / 2**nmant))


@utils.flax_slots_kw_only_dataclass
class FpNumerics(numerics.AqtNumerics):
  """Numerics for fp8."""

  # Requested rounding precision.
  cfg: FpNumericsConfig = utils.static_field()
  stochastic_rounding: bool = utils.static_field(default=False)
  clip_gradient: bool = utils.static_field(default=False)

  def abs_val_mapped_to(self):
    return fp_largest_representable(cfg=self.cfg)

  def get_dtype(self):
    return jnp.bfloat16

  def vjp_fwd(self, x, context):
    x = fp_round(
        x.astype(jnp.bfloat16),
        cfg=self.cfg,
        key=context.key,
        stochastic_rounding=self.stochastic_rounding,
    )
    res = (x,)
    return x, res

  def vjp_bwd(self, res, grad):
    ret = grad
    if self.clip_gradient:
      (x,) = res
      clip_bound = self.abs_val_mapped_to()
      ret *= (-clip_bound <= x) * (x <= clip_bound)
    return (ret, None)
