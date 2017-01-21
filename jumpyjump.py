
import gs
import camera
import helper_2d

# mount the system file driver
gs.MountFileDriver(gs.StdFileDriver())
gs.LoadPlugins()

# gs.SetDefaultLogOutputIsDetailed(True)
# gs.SetDefaultLogOutputLevelMask(gs.LogLevelAll)

plus = gs.GetPlus()
plus.CreateWorkers()
plus.AudioInit()

font = gs.RasterFont("@core/fonts/default.ttf", 16)

plus.RenderInit(1024, 768, 8, gs.Window.Windowed, False)

gui = gs.GetDearImGui()
gui.EnableMouseCursor(True)

plus.GetRendererAsync().SetVSync(False)

scn = None
scene_simple_graphic = None
cam = None
camera_handler = camera.Camera()
scn = plus.NewScene()

sky_script = gs.LogicScript("@core/lua/sky_lighting.lua")
sky_script.Set("time_of_day", 15.0)
sky_script.Set("attenuation", 0.75)
sky_script.Set("shadow_range", 1000.0) # 1km shadow range
sky_script.Set("shadow_split", gs.Vector4(0.1, 0.2, 0.3, 0.4))
scn.AddComponent(sky_script)

# add simple graphic, to draw 3D line
scene_simple_graphic = gs.SimpleGraphicSceneOverlay(False)
scn.AddComponent(scene_simple_graphic)

cam = plus.AddCamera(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(0, 1, -10)))
camera_handler.reset(gs.Matrix4.TranslationMatrix(gs.Vector3(0, 1, -10)), 10, cam)
node_sphere = plus.AddSphere(scn, gs.Matrix4.Identity, 0.1, 2, 4)
render_sphere = node_sphere.GetObject().GetGeometry()
scn.RemoveNode(node_sphere)

import numpy as np
from scipy import signal
import math
i = np.zeros((10, 10))
i[:, 0] = 1
k = np.zeros((3, 3))
k[:, 2] = 0.1
k[1, 1] = 0.9

scale = 2.0

dx = dy = dz = 0.1
nx = ny = nz = 10
# x, y = np.meshgrid(np.arange(0, nx*dx, dx), np.arange(0, ny*dy, dy))
# v = np.empty((nx, ny, 2))
# cx, cy = 5, 5
# s = 2
# rx, ry = y - cx, x - cy
# r = np.hypot(rx, ry)
# v2 = s * np.dstack((-ry, rx)) / r[..., None]
# v2[np.isnan(v2)] = 0
#
from scipy.spatial import distance
# we make these [2,] arrays to broadcast over the last output dimension
g = np.array([0, -9.8, 0])
s = np.array([-2, 2])

# this creates a [100, 100, 2] mesh, where the last dimension corresponds
# to (y, x)
yx = np.mgrid[0:nx * dx:dx, 0:ny * dy:dy, 0:nz * dz:dz].T
yx = np.reshape(yx, (nx*ny*nz, 3))

vec_runaway = np.random.rand(yx.shape[0], yx.shape[1])*0.1

distance_stay_safe = 0.2

while not plus.IsAppEnded(plus.EndOnDefaultWindowClosed):

	dt_sec = plus.UpdateClock()

	# i[:, 0] = math.cos(plus.GetClock().to_sec())
	# i = signal.convolve(i, k, mode='same')

	for i in range(yx.shape[0]):
		diff_xy = yx - yx[i]
		dist_diff_xy = diff_xy[:, 0]**2 + diff_xy[:, 1]**2 + diff_xy[:, 2]**2

		where_near = np.where(dist_diff_xy < distance_stay_safe**2)[0]
		nearest_neighbourgh = diff_xy[where_near, :]
		dist_nearest_neighbourgh = dist_diff_xy[where_near]

		# repulsion
		vec_runaway[i] += (np.sum(nearest_neighbourgh, axis=0) / yx.shape[0])*-2000.0

	# bounce on the wave
	ground_height = np.cos(yx[:, 0]*2+plus.GetClock().to_sec())*np.sin(yx[:, 2]*2+plus.GetClock().to_sec()) *0.1
	below_0 = np.where(yx[:, 1] <= ground_height)[0]
	vec_runaway[below_0, 1] += ground_height[below_0] - yx[below_0, 1] * 0.5
	yx[below_0, 1] = ground_height[below_0]

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
	vec_runaway[:, 1] += -0.3

	# lose forces
	vec_runaway *= 0.99

	#max force
	# vec_runaway = np.clip(vec_runaway, -1, 1)

	if plus.KeyDown(gs.InputDevice.KeyW):
		vec_runaway[np.where(yx[:, 0] <= 2)[0], 0] += 0.5
		vec_runaway[np.where(yx[:, 0] <= 2)[0], 2] += 1

	#wall
	yx[np.where(yx[:, 0] < -2)[0], 0] = -2
	yx[np.where(yx[:, 0] > 2)[0], 0] = 2
	yx[np.where(yx[:, 2] < -2)[0], 2] = -2
	yx[np.where(yx[:, 2] > 2)[0], 2] = 2

	# for not bouncing on the floor
	# yx[over_0, :] += vec_runaway[over_0, :] * dt_sec.to_sec()
	yx += vec_runaway * dt_sec.to_sec()

	for i in range(yx.shape[0]):
		scn.GetRenderableSystem().DrawGeometry(render_sphere, gs.Matrix4.TranslationMatrix((yx[i][0]*scale, yx[i][1]*scale, yx[i][2]*scale)))
		# helper_2d.draw_cross(scene_simple_graphic, gs.Vector3(yx[i][0]*scale, yx[i][1]*scale, yx[i][2]*scale), gs.Color.White, 0.1)

	camera.update_camera_move(dt_sec, camera_handler, gui, cam, None)
	plus.UpdateScene(scn, dt_sec)

	plus.Flip()

plus.RenderUninit()
