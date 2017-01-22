
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
scene_simple_graphic.SetBlendMode(gs.BlendAlpha)
scn.AddComponent(scene_simple_graphic)

cam = plus.AddCamera(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(0, 1, -10)))
camera_handler.reset(gs.Matrix4.TranslationMatrix(gs.Vector3(0.75, 2.59, -6.49)), 10, cam)
node_sphere = plus.AddSphere(scn, gs.Matrix4.Identity, 1.0)
render_sphere = node_sphere.GetObject().GetGeometry()
scn.RemoveNode(node_sphere)

import random
import numpy as np
import math
from shapely.ops import polygonize
from shapely.geometry import LineString, MultiPolygon, MultiPoint, Point
from scipy.spatial import Voronoi


def voronoi_cut(points):
	vor = Voronoi(points)

	lines = [
		LineString(vor.vertices[line])
		for line in vor.ridge_vertices if -1 not in line
	]

	# pts = MultiPoint([Point(i) for i in points])
	# mask = pts.convex_hull.union(pts.buffer(10, resolution=1, cap_style=3))
	# return MultiPolygon([poly.intersection(mask) for poly in polygonize(lines)])

	convex_hull = MultiPoint([Point(i) for i in points]).convex_hull.buffer(2)
	return MultiPolygon([poly.intersection(convex_hull) for poly in polygonize(lines)])

nb_base_particles = 30.
nb_particles = nb_base_particles*nb_base_particles
steepness = np.ones((nb_particles))
steepness[:] = 0.9
amplitude = np.ones((nb_particles))
amplitude[:] = 0.1
phase_const = np.ones((nb_particles))
phase_const[:] = 10
direction = np.zeros((nb_particles, 3.))
direction[:, 0] = 0.5 + random.random()*0.8-0.4
direction[:, 1] = 0.3 + random.random()*0.8-0.4
direction[:, 2] = 0.3 + random.random()*0.8-0.4
w = np.ones((nb_particles))

position = np.mgrid[0.:nb_base_particles:1, 0.:1.:1, 0.:nb_base_particles:1].T
position = np.reshape(position, (nb_particles, 3))

# a = np.arange(float(math.sqrt(nb_particles)))
# x, y = np.meshgrid(a, a)
# position = np.dstack((y, x))
# position = np.reshape(position, (nb_particles, 2))




def create_wave(height, depth, color, depth_max=3.0, complexity=3):
	global steepness, amplitude, direction, w, position, phase_const
	points = []

	# add point in the corner
	# points.append([-5, -5])
	# points.append([-5, 5])
	# points.append([5, 5])
	# points.append([5, -5])
	#
	# # add middle move
	# for x in range(-4, 4):
	# 	for z in range(-4, 4):
	# 		points.append([x+z + math.sin(plus.GetClock().to_sec()), math.cos(x*z) + math.sin(plus.GetClock().to_sec())])
	# 		points.append([x+z, math.cos(x+z)])
	# 		points.append([x + math.cos(plus.GetClock().to_sec()+z) + math.sin(x), math.cos(x+z)+height + math.sin(plus.GetClock().to_sec())])

	# yPos += (float) ((steepness[i] * amplitude[i]) * direction[i].y * Math.cos(w[i] * (direction[i].dot(position[i])) + phase_const[i] * time))

	for i in range(position.shape[0]):
		position[i, 0] += (steepness[i] * amplitude[i]) * direction[i, 0] * np.cos(w[i] * (np.dot(direction[i], position[i])) + phase_const[i] * plus.GetClock().to_sec())
		position[i, 1] += (steepness[i] * amplitude[i]) * direction[i, 1] * np.cos(w[i] * (np.dot(direction[i], position[i])) + phase_const[i] * plus.GetClock().to_sec())
		position[i, 2] += (steepness[i] * amplitude[i]) * direction[i, 2] * np.cos(w[i] * (np.dot(direction[i], position[i])) + phase_const[i] * plus.GetClock().to_sec())

	for pos in position:
		# helper_2d.draw_cross(scene_simple_graphic, gs.Vector3(pos[0], pos[1], pos[2]), gs.Color.White)
		scn.GetRenderableSystem().DrawGeometry(render_sphere, gs.Matrix4.TranslationMatrix((pos[0], pos[1], pos[2])))


	# draw lines
	# alpha = 1.0#(4* math.pow((1.0 - depth/(depth_max)),2) - 3 *math.pow((1.0 - depth/(depth_max)),50))/3.39
	# alpha = 1.0-math.pow((1.0 - depth/(depth_max)) * 2.0 - 1.0, 10)
	# alpha = 1
	# color = gs.Color(color.r, color.g, color.b, alpha)
	# color_line = gs.Color(0, 0.1, 0.8, alpha)
	# multipolygons = voronoi_cut(position)
	#
	# down_transition = (1.0-math.pow(depth/(depth_max), 10))*1
	#
	# for polygon in multipolygons:
	# 	x, y = polygon.exterior.coords.xy
	# 	for i in range(len(x)-1):
	# 		# if y[i] < height+6 and y[i+1] < height+6:
	# 		helper_2d.draw_line(scene_simple_graphic, gs.Vector3(x[i], 0, y[i]-down_transition), gs.Vector3(x[i+1], 0, y[i+1]-down_transition), color_line)
	#
	# 	if len(x) > 2:# and y[-1] < height+6 and y[0] < height+6:
	# 		helper_2d.draw_line(scene_simple_graphic, gs.Vector3(x[0], 0, y[0]-down_transition), gs.Vector3(x[-1], 0, y[-1]-down_transition), color_line)
	#
	# 	for i in range(len(x)-2):
	# 		# if y[i] < height+6 and y[i+1] < height+6:
	# 		helper_2d.draw_triangle(scene_simple_graphic, gs.Vector3(x[0], 0, y[0]-down_transition), gs.Vector3(x[i+1], 0, y[i+1]-down_transition), gs.Vector3(x[i+2], 0, y[i+2]-down_transition), color)
	#

def update():

	dt_sec = plus.UpdateClock()

	camera.update_camera_move(dt_sec, camera_handler, None, cam, None)

	create_wave(3, 1.5, gs.Color(0.05, 0.847, 0.745), depth_max=3.0, complexity=2)


	plus.UpdateScene(scn, dt_sec)
