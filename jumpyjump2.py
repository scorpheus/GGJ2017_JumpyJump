
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
import math
from numpy import linalg as LA
from scipy.spatial import Voronoi, Delaunay


def voronoi_finite_polygons_2d(vor, radius=None):
	"""
	Reconstruct infinite voronoi regions in a 2D diagram to finite
	regions.

	Parameters
	----------
	vor : Voronoi
		Input diagram
	radius : float, optional
		Distance to 'points at infinity'.

	Returns
	-------
	regions : list of tuples
		Indices of vertices in each revised Voronoi regions.
	vertices : list of tuples
		Coordinates for revised Voronoi vertices. Same as coordinates
		of input vertices, with 'points at infinity' appended to the
		end.

	"""

	if vor.points.shape[1] != 2:
		raise ValueError("Requires 2D input")

	new_regions = []
	new_vertices = vor.vertices.tolist()

	center = vor.points.mean(axis=0)
	if radius is None:
		radius = vor.points.ptp().max()

	# Construct a map containing all ridges for a given point
	all_ridges = {}
	for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
		all_ridges.setdefault(p1, []).append((p2, v1, v2))
		all_ridges.setdefault(p2, []).append((p1, v1, v2))

	# Reconstruct infinite regions
	for p1, region in enumerate(vor.point_region):
		vertices = vor.regions[region]

		if all(v >= 0 for v in vertices):
			# finite region
			new_regions.append(vertices)
			continue

		# reconstruct a non-finite region
		# ridges = all_ridges[p1]
		# new_region = [v for v in vertices if v >= 0]
		#
		# for p2, v1, v2 in ridges:
		# 	if v2 < 0:
		# 		v1, v2 = v2, v1
		# 	if v1 >= 0:
		# 		# finite ridge: already in the region
		# 		continue
		#
		# 	# Compute the missing endpoint of an infinite ridge
		#
		# 	t = vor.points[p2] - vor.points[p1] # tangent
		# 	t /= np.linalg.norm(t)
		# 	n = np.array([-t[1], t[0]])  # normal
		#
		# 	midpoint = vor.points[[p1, p2]].mean(axis=0)
		# 	direction = np.sign(np.dot(midpoint - center, n)) * n
		# 	far_point = vor.vertices[v2] + direction * radius
		#
		# 	new_region.append(len(new_vertices))
		# 	new_vertices.append(far_point.tolist())

		# sort region counterclockwise
		# vs = np.asarray([new_vertices[v] for v in new_region])
		# c = vs.mean(axis=0)
		# angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
		# new_region = np.array(new_region)[np.argsort(angles)]
		#
		# # finish
		# new_regions.append(new_region.tolist())

	return new_regions, np.asarray(new_vertices)

while not plus.IsAppEnded(plus.EndOnDefaultWindowClosed):

	dt_sec = plus.UpdateClock()

	nb_lines = 10
	spacer = 3
	lines = np.zeros((nb_lines*3*spacer, 2))
	for i in range(nb_lines):
		for j in range(1, spacer):
			lines[i] = [i+j-nb_lines*0.5 + math.sin(plus.GetClock().to_sec()), math.cos(i*j) + math.sin(plus.GetClock().to_sec())]
			lines[i+nb_lines] = [i-nb_lines*0.5+j, math.cos(i+j)]
			lines[i+nb_lines*2] = [i-nb_lines*0.5 + math.cos(plus.GetClock().to_sec()+j) + math.sin(i), math.cos(i+j) + math.sin(plus.GetClock().to_sec())]

	# draw lines
	vor = Voronoi(lines)
	regions = voronoi_finite_polygons_2d(vor, 10)

	forbidden_draw_height =6
	for polygon in regions[0]:
		for i in range(len(polygon) - 1):
			if regions[1][polygon[i]][1] < forbidden_draw_height and regions[1][polygon[i+1]][1] < forbidden_draw_height:
				helper_2d.draw_line(scene_simple_graphic, gs.Vector3(regions[1][polygon[i]][0], regions[1][polygon[i]][1], 0), gs.Vector3(regions[1][polygon[i+1]][0], regions[1][polygon[i+1]][1], 0))

		if regions[1][polygon[i]][1] < forbidden_draw_height and regions[1][polygon[i+1]][1] < forbidden_draw_height:
			helper_2d.draw_line(scene_simple_graphic, gs.Vector3(regions[1][polygon[0]][0], regions[1][polygon[0]][1], 0), gs.Vector3(regions[1][polygon[len(polygon) - 1]][0], regions[1][polygon[len(polygon) - 1]][1], 0))

	camera.update_camera_move(dt_sec, camera_handler, gui, cam, None)
	plus.UpdateScene(scn, dt_sec)

	plus.Flip()

plus.RenderUninit()
