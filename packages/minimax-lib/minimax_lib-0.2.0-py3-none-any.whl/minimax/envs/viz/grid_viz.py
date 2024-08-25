"""
Copyright (c) Meta Platforms, Inc. and affiliates.
All rights reserved.

This file is modified from 
https://github.com/Farama-Foundation/Minigrid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
"""

import math

import numpy as np

from minimax.envs.viz.window import Window
import minimax.envs.viz.grid_rendering as rendering
from minimax.envs.maze.maze import OBJECT_TO_INDEX, COLOR_TO_INDEX, COLORS


INDEX_TO_COLOR = [k for k,v in COLOR_TO_INDEX.items()]
TILE_PIXELS = 32


class GridVisualizer:
	"""
	Manages a window and renders contents of EnvState instances to it.
	"""
	tile_cache = {}

	def __init__(self):
		self.window = None

	def _lazy_init_window(self):
		if self.window is None:
			self.window = Window('minimax')

	def show(self, block=False):
		self._lazy_init_window()
		self.window.show(block=block)

	def screenshot(self, path):
		self._lazy_init_window()
		self.window.save_img(path)

	def render(self, params, state, highlight=True, tile_size=TILE_PIXELS, maze_map=None):
		return self._render_state(params, state, highlight, tile_size, maze_map)

	def render_grid(self, grid, tile_size=TILE_PIXELS, k_rot90=0, agent_dir_idx=None):
		self._lazy_init_window()

		img = GridVisualizer._render_grid(
				grid,
				tile_size,
				highlight_mask=None,
				agent_dir_idx=agent_dir_idx,
			)
		
		if k_rot90 > 0:
			img = np.rot90(img, k=k_rot90)

		self.window.show_img(img)

	def _render_state(self, params, state, highlight=True, tile_size=TILE_PIXELS, maze_map=None):
		"""
		Render the state
		"""
		self._lazy_init_window()

		if hasattr(params, 'agent_view_size'):
			agent_view_size = params.agent_view_size
			padding = agent_view_size-2 # show
			grid = np.asarray(state.maze_map[padding:-padding,padding:-padding,:])
		else:
			assert maze_map is not None, 'Either params contains agent_view_size or explicit maze map is passed in.'
			grid = np.asarray(maze_map)

		grid_offset = np.array([1,1])
		h,w = grid.shape[:2]
		
		# === Compute highlight mask
		if highlight:
			highlight_mask = np.zeros(shape=(h,w), dtype=bool)

			f_vec = state.agent_dir
			r_vec = np.array([-f_vec[1], f_vec[0]])

			fwd_bound1 = state.agent_pos
			fwd_bound2 = state.agent_pos + state.agent_dir*(agent_view_size-1)
			side_bound1 = state.agent_pos - r_vec*(agent_view_size//2) 
			side_bound2 = state.agent_pos + r_vec*(agent_view_size//2)

			min_bound = np.min(np.stack([
						fwd_bound1, 
						fwd_bound2, 
						side_bound1, 
						side_bound2]) + grid_offset, 0)

			min_y = min(max(min_bound[1], 0), highlight_mask.shape[0]-1)
			min_x = min(max(min_bound[0],0), highlight_mask.shape[1]-1)

			max_y = min(max(min_bound[1]+agent_view_size, 0), highlight_mask.shape[0]-1)
			max_x = min(max(min_bound[0]+agent_view_size, 0), highlight_mask.shape[1]-1)

			highlight_mask[min_y:max_y,min_x:max_x] = True

		# Render the whole grid
		img = GridVisualizer._render_grid(
			grid,
			tile_size,
			highlight_mask=highlight_mask if highlight else None,
			agent_dir_idx=state.agent_dir_idx if hasattr(state, 'agent_dir_idx') else 0
		)

		self.window.show_img(img)

	@classmethod
	def _render_obj(
		cls,
		obj,
		img):
		# Render each kind of object
		obj_type = obj[0]
		color = INDEX_TO_COLOR[obj[1]]

		if obj_type == OBJECT_TO_INDEX['wall']:
			rendering.fill_coords(img, rendering.point_in_rect(0, 1, 0, 1), COLORS[color])
		elif obj_type == OBJECT_TO_INDEX['goal']:
			rendering.fill_coords(img, rendering.point_in_rect(0, 1, 0, 1), COLORS[color])
		elif obj_type == OBJECT_TO_INDEX['agent']:
			agent_dir_idx = obj[2]
			tri_fn = rendering.point_in_triangle(
				(0.12, 0.19),
				(0.87, 0.50),
				(0.12, 0.81),
			)
			tri_fn = rendering.rotate_fn(tri_fn, cx=0.5, cy=0.5, theta=0.5*math.pi*agent_dir_idx)
			rendering.fill_coords(img, tri_fn, (255, 0, 0))
			# rendering.fill_coords(img, tri_fn, (60, 182, 234))

		elif obj_type == OBJECT_TO_INDEX['empty']:
			rendering.fill_coords(img, rendering.point_in_rect(0, 1, 0, 1), COLORS[color])
		elif obj_type == OBJECT_TO_INDEX['lava']:
			c = (255, 128, 0)

			# Background color
			rendering.fill_coords(img, rendering.point_in_rect(0, 1, 0, 1), c)

			# Little waves
			for i in range(3):
				ylo = 0.3 + 0.2 * i
				yhi = 0.4 + 0.2 * i
				rendering.fill_coords(img, rendering.point_in_line(0.1, ylo, 0.3, yhi, r=0.03), (0,0,0))
				rendering.fill_coords(img, rendering.point_in_line(0.3, yhi, 0.5, ylo, r=0.03), (0,0,0))
				rendering.fill_coords(img, rendering.point_in_line(0.5, ylo, 0.7, yhi, r=0.03), (0,0,0))
				rendering.fill_coords(img, rendering.point_in_line(0.7, yhi, 0.9, ylo, r=0.03), (0,0,0))
		else:
			raise ValueError(f'Rendering object at index {obj_type} is currently unsupported.')

	@classmethod
	def _render_tile(
		cls,
		obj,
		highlight=False,
		agent_dir_idx=None,
		tile_size=TILE_PIXELS,
		subdivs=3
	):
		"""
		Render a tile and cache the result
		"""
		# Hash map lookup key for the cache
		if obj is not None and \
			obj[0] == OBJECT_TO_INDEX['agent'] and \
			agent_dir_idx is not None:
			obj = np.array(obj)
			obj[-1] = agent_dir_idx

		no_object = obj is None or (
			obj[0] in [OBJECT_TO_INDEX['empty'], OBJECT_TO_INDEX['unseen']] \
			and obj[2] == 0
		)

		if not no_object:
			key = (*obj, highlight, tile_size)
		else:
			key = (obj, highlight, tile_size)

		if key in cls.tile_cache:
			return cls.tile_cache[key]

		img = np.zeros(shape=(tile_size * subdivs, tile_size * subdivs, 3), dtype=np.uint8)

		# Draw the grid lines (top and left edges)
		rendering.fill_coords(img, rendering.point_in_rect(0, 0.031, 0, 1), (100, 100, 100))
		rendering.fill_coords(img, rendering.point_in_rect(0, 1, 0, 0.031), (100, 100, 100))

		if not no_object:
			GridVisualizer._render_obj(obj, img)

		if highlight:
			rendering.highlight_img(img)

		# Downsample the image to perform supersampling/anti-aliasing
		img = rendering.downsample(img, subdivs)

		# Cache the rendered tile
		cls.tile_cache[key] = img

		return img

	@classmethod
	def _render_grid(
		cls,
		grid,
		tile_size=TILE_PIXELS,
		highlight_mask=None,
		agent_dir_idx=None):
		if highlight_mask is None:
			highlight_mask = np.zeros(shape=grid.shape[:2], dtype=np.bool)

		# Compute the total grid size in pixels
		width_px = grid.shape[1]*tile_size
		height_px = grid.shape[0]*tile_size

		img = np.zeros(shape=(height_px, width_px, 3), dtype=np.uint8)

		# Render the grid
		for y in range(grid.shape[0]):
			for x in range(grid.shape[1]):		
				obj = grid[y,x,:]
				if obj[0] in [OBJECT_TO_INDEX['empty'], OBJECT_TO_INDEX['unseen']] \
					and obj[2] == 0:
					obj = None

				tile_img = GridVisualizer._render_tile(
					obj,
					highlight=highlight_mask[y, x],
					tile_size=tile_size,
					agent_dir_idx=agent_dir_idx,
				)

				ymin = y*tile_size
				ymax = (y+1)*tile_size
				xmin = x*tile_size
				xmax = (x+1)*tile_size
				img[ymin:ymax, xmin:xmax, :] = tile_img

		return img

	def close(self):
		self.window.close()