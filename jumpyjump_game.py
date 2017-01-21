
import gs
import camera
import helper_2d

plus = gs.GetPlus()

font = gs.RasterFont("@core/fonts/default.ttf", 16)

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
node_sphere = plus.AddSphere(scn, gs.Matrix4.Identity, 0.1, 2, 4)
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


def create_wave(height, depth, color, depth_max=3.0, complexity=3):
	nb_lines = 10
	spacer = complexity
	nb_points_top_line = 5
	lines = np.zeros((nb_lines*3*spacer+1*nb_points_top_line, 2))
	for i in range(nb_lines):
		for j in range(1, spacer):
			lines[i] = [i+j-nb_lines*0.5 + math.sin(plus.GetClock().to_sec()), math.cos(i*j) + math.sin(plus.GetClock().to_sec()+height)]
			lines[i+nb_lines] = [i-nb_lines*0.5+j, math.cos(i+j)+height]
			lines[i+nb_lines*2] = [i-nb_lines*0.5 + math.cos(plus.GetClock().to_sec()+j) + math.sin(i), math.cos(i+j)+height + math.sin(plus.GetClock().to_sec())]

	for i in range(nb_points_top_line):
		lines[-i-1] = [i-2, height+6]

	# draw lines
	# alpha = 1.0#(4* math.pow((1.0 - depth/(depth_max)),2) - 3 *math.pow((1.0 - depth/(depth_max)),50))/3.39
	alpha = 1.0-math.pow((1.0 - depth/(depth_max)) * 2.0 - 1.0, 10)
	color = gs.Color(color.r, color.g, color.b, alpha)
	color_line = gs.Color(0, 0.1, 0.8, alpha)
	multipolygons = voronoi_cut(lines)

	down_transition = (1.0-math.pow(depth/(depth_max), 10))*1

	for polygon in multipolygons:
		x, y = polygon.exterior.coords.xy
		for i in range(len(x)-1):
			# if y[i] < height+6 and y[i+1] < height+6:
			helper_2d.draw_line(scene_simple_graphic, gs.Vector3(x[i], y[i]-down_transition, depth), gs.Vector3(x[i+1], y[i+1]-down_transition, depth), color_line)

		if len(x) > 2:# and y[-1] < height+6 and y[0] < height+6:
			helper_2d.draw_line(scene_simple_graphic, gs.Vector3(x[0], y[0]-down_transition, depth), gs.Vector3(x[-1], y[-1]-down_transition, depth), color_line)

		for i in range(len(x)-2):
			# if y[i] < height+6 and y[i+1] < height+6:
			helper_2d.draw_triangle(scene_simple_graphic, gs.Vector3(x[0], y[0]-down_transition, depth), gs.Vector3(x[i+1], y[i+1]-down_transition, depth), gs.Vector3(x[i+2], y[i+2]-down_transition, depth), color)


temp_height = -3.5
max_depth = 3.0
nb_waves_max = 4
spawn_wave_every = 1.0
last_spawn_time = 0
waves = [
	{"height":-3.5 * random.random(), "depth": 1.0, "color": gs.Color(0, random.random()*0.1, random.random())}
]
score = 0
failed = False

score_tex = plus.GetRendererAsync().LoadTexture("assets/score.png")
character_tex_jump = plus.GetRendererAsync().LoadTexture("assets/jump.png")
character_tex_no_jump = plus.GetRendererAsync().LoadTexture("assets/no_jump.png")


def score_ui():
	pos = gs.Vector3(-1, 4.0, -0.9)
	width = gs.Vector3(0.2, 0, 0)
	height = gs.Vector3(0, 0.2, 0)
	helper_2d.draw_quad(scene_simple_graphic,
	                    pos - width -height,
	                    pos - width + height,
	                    pos + width + height,
	                    pos + width - height,
	                    gs.Color.White,
	                    score_tex)

	scene_simple_graphic.Text(-1.05, 4.05, -1, "{}".format(score), gs.Color(), font, 0.01)


def update_character_anim():
	character_width = gs.Vector3(1, 0, 0)
	character_height = gs.Vector3(0, 1, 0)
	if plus.KeyDown(gs.InputDevice.KeySpace):
		pos = gs.Vector3(0.5, 3.0, 0)
		character_tex = character_tex_jump
	else:
		pos = gs.Vector3(0.5, 1.5, 0)
		character_tex = character_tex_no_jump
	helper_2d.draw_quad(scene_simple_graphic,
	                    pos - character_width - character_height,
	                    pos - character_width + character_height,
	                    pos + character_width + character_height,
	                    pos + character_width - character_height,
	                    gs.Color.White,
	                    character_tex)


def show_failed():
	pos = gs.Vector3(-1, 4.0, -0.9)
	width = gs.Vector3(4, 0, 0)
	height = gs.Vector3(0, 4, 0)
	helper_2d.draw_quad(scene_simple_graphic,
	                    pos - width -height,
	                    pos - width + height,
	                    pos + width + height,
	                    pos + width - height,
	                    gs.Color.White,
	                    score_tex)


def update():
	global last_spawn_time, waves, failed

	dt_sec = plus.UpdateClock()

	camera.update_camera_move(dt_sec, camera_handler, None, cam, None)

	# check if spawn waves
	last_spawn_time -= dt_sec.to_sec()
	if last_spawn_time < 0:
		waves.append({"height":-3.5 * random.random(), "depth": max_depth, "color": gs.Color(0, random.random()*0.1, random.random())})
		last_spawn_time = spawn_wave_every

	# draw waves
	waves_to_keep = []
	for wave in reversed(waves):
		wave["depth"] -= (math.pow(1.0-wave["depth"]/max_depth, 2) + 1.0) * (max_depth/(spawn_wave_every * nb_waves_max)) * dt_sec.to_sec()

		if wave["depth"] > 0:
			create_wave(wave["height"], wave["depth"], wave["color"], depth_max=3.0, complexity=2)
			waves_to_keep = [wave] + waves_to_keep

		# if wave["depth"] <0.05 and not plus.KeyDown(gs.InputDevice.KeySpace):
		# 	failed = True

	waves = waves_to_keep
	# print(len(waves))

	if not failed:
		update_character_anim()
		score_ui()
	else:
		show_failed()

	plus.UpdateScene(scn, dt_sec)
