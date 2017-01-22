
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

node_sphere = plus.AddSphere(scn, gs.Matrix4.Identity, 0.1, 2, 4, "assets/material_diffuse_color_red.mat")
render_sphere_red = node_sphere.GetObject().GetGeometry()
scn.RemoveNode(node_sphere)
node_sphere = plus.AddSphere(scn, gs.Matrix4.Identity, 0.1, 2, 4, "assets/material_diffuse_color_green.mat")
render_sphere_green = node_sphere.GetObject().GetGeometry()
scn.RemoveNode(node_sphere)

import numpy as np

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

	# move one of the particle
	if plus.KeyDown(gs.InputDevice.KeyZ):
		vec_runaway[0, 2] += 2
	if plus.KeyDown(gs.InputDevice.KeyS):
		vec_runaway[0, 2] -= 2
	if plus.KeyDown(gs.InputDevice.KeyQ):
		vec_runaway[0, 0] -= 2
	if plus.KeyDown(gs.InputDevice.KeyD):
		vec_runaway[0, 0] += 2

	viewport = plus.GetRendererAsync().GetViewport().get()
	success, point_mouse = gs.Unproject(cam.GetTransform().GetWorld(), cam.GetCamera().GetZoomFactor(), plus.GetRendererAsync().GetAspectRatio().get(), gs.Vector3(plus.GetMousePos()[0]/viewport.ex, 1.0-plus.GetMousePos()[1]/viewport.ey, 1))

	d = gs.Vector3(0, 1, 0).Dot(gs.Vector3(0, 0, 0)-cam.GetTransform().GetPosition()) / gs.Vector3(0, 1, 0).Dot(point_mouse - cam.GetTransform().GetPosition())
	ground_pos = cam.GetTransform().GetPosition() + (point_mouse - cam.GetTransform().GetPosition()).Normalized() * d

	scn.GetRenderableSystem().DrawGeometry(render_sphere_green, gs.Matrix4.TranslationMatrix(ground_pos))
	ground_pos /= scale

	for i in range(zyx.shape[0]):
		diff_xyz = zyx - zyx[i]
		dist_diff_xyz = diff_xyz[:, 0] ** 2 + diff_xyz[:, 1] ** 2 + diff_xyz[:, 2] ** 2

		where_dist_small = np.where((dist_diff_xyz != 0) & (dist_diff_xyz < distance_stay_safe ** 2))[0]
		if where_dist_small.size > 0 and dist_diff_xyz[where_dist_small].max() != 0:
			nearest_neighbourgh = diff_xyz[where_dist_small, :]
			sum_neighbourgh = (np.sum(nearest_neighbourgh, axis=0) / nearest_neighbourgh.shape[0])
			vec_runaway[i] += sum_neighbourgh * -2.0

		# repulse more from the particle 0
		if dist_diff_xyz[0] < 0.5:
			vec_runaway[i] += diff_xyz[0] * -1.0

	vec_a = (gs.Vector3(ground_pos.x, zyx[0][1], ground_pos.z) - gs.Vector3(zyx[0][0], zyx[0][1], zyx[0][2])).Normalized()
	vec_runaway[0] += [vec_a.x, vec_a.y, vec_a.z]

	# bounce on the wave
	ground_height = np.cos(zyx[:, 0] *4 + plus.GetClock().to_sec()*1) * np.sin(zyx[:, 2] *4 + plus.GetClock().to_sec()) * 0.1
	below_0 = np.where(zyx[:, 1] <= ground_height)[0]
	vec_runaway[below_0, 1] += (ground_height[below_0] - zyx[below_0, 1]) * 0.1
	zyx[below_0, 1] = ground_height[below_0]

	# gravity
	vec_runaway[:, 1] += -0.9

	# lose forces
	vec_runaway *= 0.9

	if plus.KeyDown(gs.InputDevice.KeyW) or apply_force_counter < 0:
		# vec_runaway[np.where(zyx[1:, 0] <= 2)[0], 0] += 0.6
		# vec_runaway[np.where(zyx[1:, 0] <= 2)[0], 1] += 0.01
		vec_runaway[1:, 0] += 0.6
		vec_runaway[1:, 1] += 0.01

		if apply_force_counter < -0.2:
			apply_force_counter = 2.0

	# wall
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
	zyx += vec_runaway * dt_sec.to_sec() * 1.0

	scn.GetRenderableSystem().DrawGeometry(render_sphere_red, gs.Matrix4.TranslationMatrix((zyx[0][0] * scale, zyx[0][1] * scale, zyx[0][2] * scale)))
	for i in range(1, zyx.shape[0]):
		scn.GetRenderableSystem().DrawGeometry(render_sphere, gs.Matrix4.TranslationMatrix((zyx[i][0] * scale, zyx[i][1] * scale, zyx[i][2] * scale)))

	# camera.update_camera_move(dt_sec, camera_handler, None, cam, None)
	plus.UpdateScene(scn, dt_sec)

