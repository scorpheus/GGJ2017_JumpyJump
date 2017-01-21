
import gs

# mount the system file driver
gs.MountFileDriver(gs.StdFileDriver())
gs.LoadPlugins()

# gs.SetDefaultLogOutputIsDetailed(True)
# gs.SetDefaultLogOutputLevelMask(gs.LogLevelAll)

plus = gs.GetPlus()
plus.CreateWorkers()
plus.AudioInit()

plus.RenderInit(1024, 768, 8, gs.Window.Windowed, False)

gui = gs.GetDearImGui()
gui.EnableMouseCursor(True)

plus.GetRendererAsync().SetVSync(False)

plus.SetBlend2D(gs.BlendAlpha)
plus.SetBlend3D(gs.BlendAlpha)

import jumpyjump_game
import jumpyjump_slow_waves

# play_menu = True
# playgame = False
play_menu = False
playgame = True

while not plus.IsAppEnded(plus.EndOnDefaultWindowClosed):

	dt_sec = plus.UpdateClock()

	if play_menu:
		if gui.Begin("GUI"):
			if gui.Button("Play !!"):
				play_menu = False
				playgame = True
		gui.End()
		jumpyjump_slow_waves.update()
	elif playgame:
		jumpyjump_game.update()

	plus.Flip()

plus.RenderUninit()
