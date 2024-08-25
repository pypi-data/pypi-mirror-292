"""
Copyright (c) Meta Platforms, Inc. and affiliates.
All rights reserved.

This file is modified from
https://github.com/RobertTLange/gymnax/

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""

from typing import Tuple, Union
from collections import OrderedDict
import chex
import jax
import jax.numpy as jnp


class Discrete(object):
	"""
	Minimal jittable class for discrete gymnax spaces.
	TODO: For now this is a 1d space. Make composable for multi-discrete.
	"""

	def __init__(self, num_categories: int, shape: Tuple[int] = (), dtype=jnp.int32):
		assert num_categories >= 0
		self.n = num_categories
		self.shape = shape
		self.dtype = dtype

	def sample(self, rng: chex.PRNGKey) -> chex.Array:
		"""Sample random action uniformly from set of categorical choices."""
		return jax.random.randint(
			rng, shape=self.shape, minval=0, maxval=self.n
		).astype(self.dtype)

	def contains(self, x: jnp.int_) -> bool:
		"""Check whether specific object is within space."""
		# type_cond = isinstance(x, self.dtype)
		# shape_cond = (x.shape == self.shape)
		range_cond = jnp.logical_and(x >= 0, x < self.n)
		return range_cond


class Box(object):
	"""
	Minimal jittable class for array-shaped gymnax spaces.
	TODO: Add unboundedness - sampling from other distributions, etc.
	"""
	def __init__(
		self,
		low: float,
		high: float,
		shape: Tuple[int],
		dtype: jnp.dtype = jnp.float32,
	):
		self.low = low
		self.high = high
		self.shape = shape
		self.dtype = dtype

	def sample(self, rng: chex.PRNGKey) -> chex.Array:
		"""Sample random action uniformly from 1D continuous range."""
		return jax.random.uniform(
			rng, shape=self.shape, minval=self.low, maxval=self.high
		).astype(self.dtype)

	def contains(self, x: jnp.int_) -> bool:
		"""Check whether specific object is within space."""
		# type_cond = isinstance(x, self.dtype)
		# shape_cond = (x.shape == self.shape)
		range_cond = jnp.logical_and(
			jnp.all(x >= self.low), jnp.all(x <= self.high)
		)
		return range_cond


class Dict(object):
	"""Minimal jittable class for dictionary of simpler jittable spaces."""
	def __init__(self, spaces: dict):
		self.spaces = spaces
		self.num_spaces = len(spaces)

	def sample(self, rng: chex.PRNGKey) -> dict:
		"""Sample random action from all subspaces."""
		key_split = jax.random.split(rng, self.num_spaces)
		return OrderedDict(
			[
				(k, self.spaces[k].sample(key_split[i]))
				for i, k in enumerate(self.spaces)
			]
		)

	def contains(self, x: jnp.int_) -> bool:
		"""Check whether dimensions of object are within subspace."""
		# type_cond = isinstance(x, dict)
		# num_space_cond = len(x) != len(self.spaces)
		# Check for each space individually
		out_of_space = 0
		for k, space in self.spaces.items():
			out_of_space += 1 - space.contains(getattr(x, k))
		return out_of_space == 0


class Tuple(object):
	"""Minimal jittable class for tuple (product) of jittable spaces."""
	def __init__(self, spaces: Union[tuple, list]):
		self.spaces = spaces
		self.num_spaces = len(spaces)

	def sample(self, rng: chex.PRNGKey) -> Tuple[chex.Array]:
		"""Sample random action from all subspaces."""
		key_split = jax.random.split(rng, self.num_spaces)
		return tuple(
			[
				space.sample(key_split[i])
				for i, space in enumerate(self.spaces)
			]
		)

	def contains(self, x: jnp.int_) -> bool:
		"""Check whether dimensions of object are within subspace."""
		# type_cond = isinstance(x, tuple)
		# num_space_cond = len(x) != len(self.spaces)
		# Check for each space individually
		out_of_space = 0
		for space in self.spaces:
			out_of_space += 1 - space.contains(x)
		return out_of_space == 0


class Dummy(object):
	def __init__(self, default_value=None):
		self._default_value = default_value
		self.dtype = jnp.uint32
		if self._default_value is None:
			self.n = 0
		else:
			self.n = 1

	def sample(self, rng: chex.PRNGKey):
		if self._default_value is None:
			return None
		else:
			return jnp.array(0, dtype=self.dtype)

	def contains(self, x: jnp.int_) -> bool:
		return False
