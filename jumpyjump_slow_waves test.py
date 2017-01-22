
import gs
import camera
import helper_2d

plus = gs.GetPlus()

camera_handler = camera.Camera()
scn = plus.NewScene()

sky_script = gs.LogicScript("@core/lua/sky_lighting.lua")
sky_script.Set("time_of_day", 15.0)
sky_script.Set("attenuation", 0.75)
sky_script.Set("shadow_range", 1000.0) # 1km shadow range
sky_script.Set("shadow_split", gs.Vector4(0.1, 0.2, 0.3, 0.4))
scn.AddComponent(sky_script)

plus.UpdateScene(scn, gs.time(0))
lights = scn.GetNodesWithAspect("Light")
for l in lights:
	scn.RemoveNode(l)

# add simple graphic, to draw 3D line
scene_simple_graphic = gs.SimpleGraphicSceneOverlay(False)
scn.AddComponent(scene_simple_graphic)

cam = plus.AddCamera(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(0, 1, -10)))
camera_handler.reset(gs.Matrix4.TransformationMatrix((3.3167, 1.8287, -6.5168), (0.3149, -0.0965, 0)), 10, cam)
node_sphere = plus.AddSphere(scn, gs.Matrix4.Identity, 0.1, 2, 4)
render_sphere = node_sphere.GetObject().GetGeometry()
scn.RemoveNode(node_sphere)

import numpy as np
from numpy import linalg as LA
from scipy.spatial import Voronoi, Delaunay

scale = 2.0

dx = dy = dz = 0.05
nx = ny = nz = 8

zyx = np.mgrid[0:nx * dx:dx, 0:ny * dy:dy, 0:nz * dz:dz].T
zyx = np.reshape(zyx, (nx * ny * nz, 3))

vec_runaway = np.random.rand(zyx.shape[0], zyx.shape[1]) * 0.1

distance_stay_safe = 0.1
apply_force_counter = 0.0


def update():
	global zyx, vec_runaway, apply_force_counter
	dt_sec = plus.UpdateClock()

	apply_force_counter -= dt_sec.to_sec()

	# i[:, 0] = math.cos(plus.GetClock().to_sec())
	# i = signal.convolve(i, k, mode='same')

	for i in range(zyx.shape[0]):
		diff_xyz = zyx - zyx[i]
		dist_diff_xyz = diff_xyz[:, 0] ** 2 + diff_xyz[:, 1] ** 2 + diff_xyz[:, 2] ** 2

		where_dist_small = np.where((dist_diff_xyz != 0) & (dist_diff_xyz < distance_stay_safe ** 2))[0]
		if where_dist_small.size > 0 and dist_diff_xyz[where_dist_small].max() != 0:
			nearest_neighbourgh = diff_xyz[where_dist_small, :]

			# dist_val = dist_diff_xyz[where_dist_small] / dist_diff_xyz[where_dist_small].max()
			# dist_up_0_5 = np.where(dist_val >= 0.5)
			# dist_under_0_5 = np.where(dist_val < 0.5)
			# dist_val[dist_up_0_5] = 1.0-((dist_val[dist_up_0_5] - 0.5) * 2.0)
			# dist_val[dist_under_0_5] = 1.0
			# # repulsion
			# vec_runaway[i] += (np.sum(dist_val[:, None] * (nearest_neighbourgh / LA.norm(nearest_neighbourgh)), axis=0) / nearest_neighbourgh.shape[0]) * -1.0
			# sum_neighbourgh = (np.sum(dist_val[:, None] * nearest_neighbourgh, axis=0) / nearest_neighbourgh.shape[0])
			# sum_neighbourgh = (np.sum((nearest_neighbourgh / LA.norm(nearest_neighbourgh, axis=1)[:, None]), axis=0) / nearest_neighbourgh.shape[0])
			sum_neighbourgh = (np.sum(nearest_neighbourgh, axis=0) / nearest_neighbourgh.shape[0])
			# sum_neighbourgh += (np.random.rand(nearest_neighbourgh.shape[1]) -0.5) * 0.1

			vec_runaway[i] += sum_neighbourgh * -2.0
			# norm = LA.norm(sum_neighbourgh)
			# if norm != 0:
			# 	vec_runaway[i] += (sum_neighbourgh / norm) * -1.0

	# bounce on the wave
	ground_height = np.cos(zyx[:, 0] * 2 + plus.GetClock().to_sec()) * np.sin(zyx[:, 2] * 2 + plus.GetClock().to_sec()) * 0.1
	below_0 = np.where(zyx[:, 1] <= ground_height)[0]
	vec_runaway[below_0, 1] += (ground_height[below_0] - zyx[below_0, 1]) * 0.1
	zyx[below_0, 1] = ground_height[below_0]

	# above wave, but futur position may be under the wave
	# under_0 = np.where(yx[above_0, 1] + vec_runaway[above_0, 1] < ground_height[above_0])[0]
	# over_0 = np.where(yx[above_0, 1] + vec_runaway[above_0, 1] >= ground_height[above_0])[0]
	#
	# percent_on_top = np.abs(vec_runaway[under_0, 1] / (yx[under_0, 1] - ground_height[under_0]))
	#
	# yx[under_0, :] += vec_runaway[under_0, :] * dt_sec.to_sec() * percent_on_top[:, None]
	# vec_runaway[under_0, 1] *= -1.0
	# yx[under_0, :] += vec_runaway[under_0, :] * dt_sec.to_sec() * (1.0 - percent_on_top)[:, None]

	# gravity
	vec_runaway[:, 1] += -0.9

	# lose forces
	vec_runaway *= 0.9

	#max force
	# vec_runaway = np.clip(vec_runaway, -1, 1)

	if plus.KeyDown(gs.InputDevice.KeyW) or apply_force_counter < 0:
		vec_runaway[np.where(zyx[:, 0] <= 2)[0], 0] += 0.6
		vec_runaway[np.where(zyx[:, 0] <= 2)[0], 1] += 0.01

		if apply_force_counter < -0.2:
			apply_force_counter = 2.0

	#wall
	bouncing_wall = 2
	vec_runaway[np.where(zyx[:, 0] < -bouncing_wall)[0], 0] *= -1.0
	vec_runaway[np.where(zyx[:, 0] > bouncing_wall)[0], 0] *= -1.0
	vec_runaway[np.where(zyx[:, 2] < -bouncing_wall)[0], 2] *= -1.0
	vec_runaway[np.where(zyx[:, 2] > bouncing_wall)[0], 2] *= -1.0
	zyx[np.where(zyx[:, 0] < -bouncing_wall)[0], 0] = -bouncing_wall
	zyx[np.where(zyx[:, 0] > bouncing_wall)[0], 0] = bouncing_wall
	zyx[np.where(zyx[:, 2] < -bouncing_wall)[0], 2] = -bouncing_wall
	zyx[np.where(zyx[:, 2] > bouncing_wall)[0], 2] = bouncing_wall

	# for not bouncing on the floor
	# yx[over_0, :] += vec_runaway[over_0, :] * dt_sec.to_sec()
	zyx += vec_runaway * dt_sec.to_sec() * 1.0


	# draw lines
	# vor = Voronoi(zyx)
	#
	# for region in vor.regions:
	# 	polygon = vor.vertices[region]
	# 	if len(polygon) > 0:
	# 		for i in range(len(polygon)-1):
	# 			if region[i] != -1 and region[i+1] != -1:
	# 				helper_2d.draw_line(scene_simple_graphic, gs.Vector3(polygon[i][0], polygon[i][1], polygon[i][2]), gs.Vector3(polygon[i+1][0], polygon[i+1][1], polygon[i+1][2]))

			# if len(polygon) > 2 and region[0] != -1 and region[-1] != -1:
			# 	helper_2d.draw_line(scene_simple_graphic, gs.Vector3(polygon[0][0], polygon[0][1], polygon[i][2]), gs.Vector3(polygon[-1][0], polygon[-1][1], polygon[-1][2]))
	#
	# tri = Delaunay(zyx)
	# lines = zyx[tri.simplices]
	#
	# for i in range(lines.shape[0]):
	# 	def draw_line(a, b):
	# 		helper_2d.draw_line(scene_simple_graphic, gs.Vector3(a[0], a[1], a[2]), gs.Vector3(b[0], b[1], b[2]))
	# 	draw_line(lines[i][0], lines[i][1])
	# 	draw_line(lines[i][1], lines[i][2])
	# 	draw_line(lines[i][2], lines[i][3])
	# 	draw_line(lines[i][3], lines[i][0])

	for i in range(zyx.shape[0]):
		scn.GetRenderableSystem().DrawGeometry(render_sphere, gs.Matrix4.TranslationMatrix((zyx[i][0] * scale, zyx[i][1] * scale, zyx[i][2] * scale)))
		# helper_2d.draw_cross(scene_simple_graphic, gs.Vector3(zyx[i][0]*scale, zyx[i][1]*scale, zyx[i][2]*scale), gs.Color.White, 0.1)

	# camera.update_camera_move(dt_sec, camera_handler, None, cam, None)
	plus.UpdateScene(scn, dt_sec)

