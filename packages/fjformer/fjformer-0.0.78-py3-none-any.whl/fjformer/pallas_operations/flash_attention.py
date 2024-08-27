import os as _os

import flax.linen

_os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"
_os.environ["XLA_PYTHON_CLIENT_MEM_FRACTION"] = "0.10"
_os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import math
from typing import Optional, Tuple

import chex
import jax
from flax.linen.attention import dot_product_attention
from jax import lax, random
from jax import numpy as jnp

from fjformer.sharding import auto_shard_array


def get_qkv(b, s, h, d):
	return [
		random.normal(random.key(0), (b, s, h, d)),
		random.normal(random.key(1), (b, s, h, d)),
		random.normal(random.key(2), (b, s, h, d)),
	]


def flash_attention(
	q: chex.Array,
	k: chex.Array,
	v: chex.Array,
	mask: Optional[chex.Array] = None,
	bias: Optional[chex.Array] = None,
	*,
	dropout: float = 0.0,
	inference: bool,
	key: Optional[random.PRNGKeyArray] = None,
	block_size: Optional[int] = None,
	dtype: Optional[jnp.dtype] = None,
	precision: lax.PrecisionLike = None,
):
	if not inference and dropout > 0 and key is None:
		raise ValueError("key must be provided for training")

	if dropout < 0 or dropout > 1:
		raise ValueError(f"invalid dropout {dropout}")
	if dtype is not None:
		q = q.astype(dtype)
		k = k.astype(dtype)

	if block_size is None:
		block_size = 1024
	q_seq_len = q.shape[2]
	kv_seq_len = k.shape[2]
	q /= math.sqrt(float(k.shape[-1]))

	return _flash_attention(
		(q, k, v),
		q_seq_len,
		kv_seq_len,
		k.shape[-1],
		mask,
		bias,
		dropout,
		inference=inference,
		key=key,
		block_size=block_size,
		precision=precision,
	)


@jax.custom_vjp
def _flash_attention(
	qkv: Tuple[chex.Array, chex.Array, chex.Array],
	q_seq: int,
	k_seq: int,
	dim: int,
	mask: Optional[chex.Array] = None,
	bias: Optional[chex.Array] = None,
	dropout: float = 0.0,
	*,
	inference: bool,
	key: Optional[random.PRNGKeyArray] = None,
	block_size: int,
	precision: lax.PrecisionLike,
):
	return _flash_attention_forward(
		None,
		qkv,
		q_seq,
		k_seq,
		dim,
		mask,
		bias,
		dropout,
		inference=inference,
		key=key,
		block_size=block_size,
		precision=precision,
	)[0]


@jax.named_scope("_flash_attention_forward")
def _flash_attention_forward(
	ignore,
	qkv: Tuple[chex.Array, chex.Array, chex.Array],
	q_seq: int,
	k_seq: int,
	dim: int,
	mask: Optional[chex.Array],
	bias: Optional[chex.Array],
	dropout: float,
	*,
	inference: bool,
	key: Optional[random.PRNGKeyArray],
	block_size: int,
	precision: lax.PrecisionLike,
):
	del ignore
	q, k, v = qkv
	if q_seq % block_size != 0:
		raise ValueError(f"q axis size {q_seq} is not a multiple of {block_size}")
	if k_seq % block_size != 0:
		raise ValueError(f"k axis size {k_seq} is not a multiple of {block_size}")

	# number of blocks for Q and K
	Tr = q_seq // block_size
	Tc = k_seq // block_size
	q_batch_axes = q.shape[0:2]
	o_shape = jax.eval_shape(flax.linen.attention.dot_product_attention, q, k, v)
	o = auto_shard_array(
		jnp.zeros(o_shape, q.dtype),
		names=[p for p in getattr(q.sharding, "spec", [])],
	)
	ell = auto_shard_array(jnp.zeros((*q_batch_axes, q_seq)))

	@jax.named_scope("_flash_attention_forward_do_o_block")
	def do_o_block(state):
		i, o, ell = state
		chunk = i * block_size
		q_i = q[:, :, chunk : chunk + block_size, :]  # batch, head, pos, dim
		o_i = o[:, :, chunk : chunk + block_size, :]  # batch, head, pos, dim
		sumexp_i = jnp.zeros(q_batch_axes + (block_size,), q.dtype)
		max_i = jnp.full(q_batch_axes + (block_size,), -jnp.inf, q.dtype)

		@jax.named_scope("_flash_attention_forward_do_o_block_do_qk_block")
		def do_qk_block(state):
			i, j, o_i, q_i, sumexp_i, old_max_i = state
			k_chunk = j * block_size
			k_j = k[:, :, chunk : chunk + block_size, :]  # batch, head, pos, dim
			v_j = v[:, :, chunk : chunk + block_size, :]  # batch, head, pos, dim
			attn_ij = q_i @ k_j.transpose(0, 1, 3, 2)


def main():
	q, k, v = get_qkv(1, 64, 8, 128)
	res = dot_product_attention(q, k, v)
	print(res.sum().mean())


if __name__ == "__main__":
	main()
