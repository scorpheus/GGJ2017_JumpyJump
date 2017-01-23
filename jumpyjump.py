
import gs

# mount the system file driver
gs.MountFileDriver(gs.StdFileDriver())
gs.LoadPlugins()

# gs.SetDefaultLogOutputIsDetailed(True)
# gs.SetDefaultLogOutputLevelMask(gs.LogLevelAll)

plus = gs.GetPlus()
# plus.CreateWorkers()
plus.AudioInit()

plus.RenderInit(1920, 1080, 8, gs.Window.Windowed, False)

gui = gs.GetDearImGui()
gui.EnableMouseCursor(True)

plus.GetRendererAsync().SetVSync(False)

plus.SetBlend2D(gs.BlendAlpha)
plus.SetBlend3D(gs.BlendAlpha)

import jumpyjump_game2
import jumpyjump_slow_waves
# import jumpyjump_test_voronoi_wave

play_menu = True
playgame = False
# play_menu = False
# playgame = True

while not plus.IsAppEnded(plus.EndOnDefaultWindowClosed):

	dt_sec = plus.UpdateClock()

	if play_menu:
		if gui.Begin("JumpyJump"):
			if gui.Button("Play !!"):
				play_menu = False
				playgame = True
				jumpyjump_game2.failed = False
				jumpyjump_game2.score = 0
				jumpyjump_game2.spawn_wave_every = 0.1
		gui.End()
		jumpyjump_slow_waves.update()
	elif playgame:
		if gui.Begin("exit"):
			if gui.Button("Exit !!"):
				play_menu = True
				playgame = False
		gui.End()
		jumpyjump_game2.update()

	# jumpyjump_test_voronoi_wave.update()
	plus.Flip()

plus.RenderUninit()
