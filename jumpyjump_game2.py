
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

plus.AddEnvironment(scn, gs.Color.Black, gs.Color.Black, gs.Color.Black, 0.0, 2)

plus.UpdateScene(scn, gs.time(0))
lights = scn.GetNodesWithAspect("Light")
for l in lights:
	scn.RemoveNode(l)

# add simple graphic, to draw 3D line
scene_simple_graphic = gs.SimpleGraphicSceneOverlay(False)
scene_simple_graphic.SetBlendMode(gs.BlendAlpha)
scn.AddComponent(scene_simple_graphic)

scene_simple_graphic_2d = gs.SimpleGraphicSceneOverlay(True)
scene_simple_graphic_2d.SetBlendMode(gs.BlendAlpha)
scn.AddComponent(scene_simple_graphic_2d)

cam = plus.AddCamera(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(0, 1, -10)))
camera_handler.reset(gs.Matrix4.TranslationMatrix(gs.Vector3(0.75, 2.59, -6.49)), 10, cam)
node_sphere = plus.AddSphere(scn, gs.Matrix4.Identity, 0.1, 2, 4)
render_sphere = node_sphere.GetObject().GetGeometry()
scn.RemoveNode(node_sphere)

import math
from scipy.spatial import Voronoi
# from shapely.ops import polygonize
# from shapely.geometry import LineString, MultiPolygon, MultiPoint, Point
#
#
# def voronoi_cut(points):
# 	vor = Voronoi(points)
#
# 	lines = [
# 	    LineString(vor.vertices[line])
# 	    for line in vor.ridge_vertices if -1 not in line
# 	]
#
# 	# pts = MultiPoint([Point(i) for i in points])
# 	# mask = pts.convex_hull.union(pts.buffer(10, resolution=1, cap_style=3))
# 	# return MultiPolygon([poly.intersection(mask) for poly in polygonize(lines)])
#
# 	convex_hull = MultiPoint([Point(i) for i in points]).convex_hull.buffer(1)
# 	return MultiPolygon([poly.intersection(convex_hull) for poly in polygonize(lines)])


def create_wave(height, depth, color, depth_max=3.0):
	nb_lines = 2
	nb_points_top_line = 20
	# lines = np.zeros((nb_lines*3+1*nb_points_top_line, 2))
	# for i in range(nb_lines):
	# 	lines[i] = [i-nb_lines*0.5 + math.sin(plus.GetClock().to_sec()), math.cos(i) + math.sin(plus.GetClock().to_sec()+height)]
	# 	lines[i+nb_lines] = [i-nb_lines*0.5, math.cos(i)+height]
	# 	lines[i+nb_lines*2] = [i-nb_lines*0.5 + math.cos(plus.GetClock().to_sec()) + math.sin(i), math.cos(i)+height + math.sin(plus.GetClock().to_sec())]
	#
	# for i in range(nb_points_top_line):
	# 	lines[-i-1] = [math.cos(i-2), height+math.sin(height)*6]

	points = []
	for i in range(nb_points_top_line):
		points.append([i - nb_points_top_line//2 + math.sin(i+plus.GetClock().to_sec()+depth), height + math.sin(i)*0.5 + math.cos(depth+plus.GetClock().to_sec()) *0.1])
		points.append([i - nb_points_top_line//2 - math.sin(i+0.5+plus.GetClock().to_sec()+depth), height + math.sin(i)*0.5 - math.cos(depth+plus.GetClock().to_sec()) *0.1])

	for pos in points:
		pos[0] *= 3
		pos[1] *= 3

	# for pos in points:
	# 	helper_2d.draw_cross(scene_simple_graphic, gs.Vector3(pos[0], pos[1], depth), gs.Color.White)
		# scn.GetRenderableSystem().DrawGeometry(render_sphere, gs.Matrix4.TranslationMatrix((pos[0]*3, pos[1], pos[2])))

	# draw lines
	# alpha = 1.0#(4* math.pow((1.0 - depth/(depth_max)),2) - 3 *math.pow((1.0 - depth/(depth_max)),50))/3.39
	# alpha = 1.0-math.pow((1.0 - depth/(depth_max)) * 2.0 - 1.0, 10)
	alpha = 1.0
	color = gs.Color(color.r, color.g, color.b, alpha)
	color_line = gs.Color(0, 0.1, 0.8, alpha)
	# multipolygons = voronoi_cut(points)
	#
	# for polygon in multipolygons:
	# 	x, y = polygon.exterior.coords.xy
	# 	for i in range(len(x)-1):
	# 		# if y[i] < height+6 and y[i+1] < height+6:
	# 		helper_2d.draw_line(scene_simple_graphic, gs.Vector3(x[i], y[i], depth), gs.Vector3(x[i+1], y[i+1], depth), color_line)
	#
	# 	if len(x) > 2:# and y[-1] < height+6 and y[0] < height+6:
	# 		helper_2d.draw_line(scene_simple_graphic, gs.Vector3(x[0], y[0], depth), gs.Vector3(x[-1], y[-1], depth), color_line)

		# for i in range(len(x)-2):
		# 	if y[i] < height+6 and y[i+1] < height+6:
		# 	helper_2d.draw_triangle(scene_simple_graphic, gs.Vector3(x[0], y[0], depth), gs.Vector3(x[i+1], y[i+1], depth), gs.Vector3(x[i+2], y[i+2]-down_transition, depth), color)

	forbidden_height = height*3 + 2
	vor = Voronoi(points)
	for region in vor.regions:
		polygon = vor.vertices[region]
		if len(polygon) > 0:
			polygon_allowed = True
			for i in range(len(polygon)-1):
				if region[i] != -1 and region[i+1] != -1:
					if polygon[i][1] > forbidden_height or polygon[i+1][1] > forbidden_height:
						polygon_allowed = False

			if polygon_allowed:
				for i in range(len(polygon)-1):
					if region[i] != -1 and region[i+1] != -1:
						helper_2d.draw_line(scene_simple_graphic, gs.Vector3(polygon[i][0], polygon[i][1], depth), gs.Vector3(polygon[i+1][0], polygon[i+1][1], depth), color_line)

				if len(polygon) > 2 and region[0] != -1 and region[-1] != -1:
					helper_2d.draw_line(scene_simple_graphic, gs.Vector3(polygon[0][0], polygon[0][1], depth), gs.Vector3(polygon[-1][0], polygon[-1][1], depth), color_line)

				for i in range(len(polygon)-2):
					if region[0] != -1 and region[i+1] != -1 and region[i+2] != -1:
						helper_2d.draw_triangle(scene_simple_graphic, gs.Vector3(polygon[0][0], polygon[0][1], depth), gs.Vector3(polygon[i+1][0], polygon[i+1][1], depth), gs.Vector3(polygon[i+2][0], polygon[i+2][1], depth), color)

current_wave = 0
max_depth = 25.0
nb_waves_max = 4
spawn_wave_every = 0.1
last_spawn_time = 0
timer_jump = 0
waves = []
score = 0
failed = False

failed_tex = plus.GetRendererAsync().LoadTexture("assets/failed.png")
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

	scene_simple_graphic.Text(-0.9, 3.9, -1, "{}".format(score), gs.Color(), font, 0.01)


def update_character_anim():
	global timer_jump
	character_width = gs.Vector3(2, 0, 0)
	character_height = gs.Vector3(0, 2, 0)
	if timer_jump > 0 and plus.KeyDown(gs.InputDevice.KeySpace):
		pos = gs.Vector3(0.5, 3.0, 15)
		character_tex = character_tex_jump
		timer_jump -= plus.GetClockDt().to_sec()
	else:
		if not plus.KeyDown(gs.InputDevice.KeySpace):
			timer_jump = 0.2

		pos = gs.Vector3(0.5, -2, 15)
		character_tex = character_tex_no_jump
	helper_2d.draw_quad(scene_simple_graphic,
	                    pos - character_width - character_height,
	                    pos - character_width + character_height,
	                    pos + character_width + character_height,
	                    pos + character_width - character_height,
	                    gs.Color.White,
	                    character_tex)


def show_failed():
	pos = gs.Vector3(0, 0, 0)
	viewport = plus.GetRendererAsync().GetViewport().get()
	width = gs.Vector3(viewport.ex, 0, 0)
	height = gs.Vector3(0, viewport.ey, 0)
	helper_2d.draw_quad(scene_simple_graphic_2d,
	                    pos,
	                    pos + height,
	                    pos + width + height,
	                    pos + width,
	                    gs.Color.White,
	                    failed_tex)

for i in range(int(max_depth)):
	waves.append({"height": -1.0, "depth": i*3, "color":  gs.Color(0, 0, (i/max_depth)*0.8+0.2)})#gs.Color(0, random.random()*0.1, random.random()*0.5+0.5)})


def update():
	global last_spawn_time, failed, score, current_wave, spawn_wave_every

	dt_sec = plus.UpdateClock()

	# camera.update_camera_move(dt_sec, camera_handler, None, cam, None)

	last_spawn_time -= dt_sec.to_sec()
	if last_spawn_time < 0:

		if not failed and current_wave == 15//3 and plus.KeyDown(gs.InputDevice.KeySpace):
			score += 1

		current_wave -= 1
		if current_wave < 0:
			current_wave = len(waves)-1
			spawn_wave_every *= 0.8
		last_spawn_time = spawn_wave_every

	# draw waves
	# print(current_wave)
	for id, wave in enumerate(waves):
		if current_wave == id:
			create_wave(wave["height"] + 2, wave["depth"], gs.Color(0, 0, 1), max_depth)
		else:
			create_wave(wave["height"], wave["depth"], wave["color"], max_depth)

	if not failed and current_wave == 15//3 and not plus.KeyDown(gs.InputDevice.KeySpace):
		failed = True
		spawn_wave_every = 0.1

	update_character_anim()
	score_ui()

	if failed:
		show_failed()
		if plus.KeyDown(gs.InputDevice.KeySpace):
			failed = False
			score = 0

	plus.UpdateScene(scn, dt_sec)
