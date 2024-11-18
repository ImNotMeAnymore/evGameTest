class EngineError(Exception): pass
if __name__ == "__main__": raise EngineError("Run Your own script. Not the engine!!!")
class Done(Exception): pass


#cengine.py, a small pygame-ce wrapper
#Copyright (C) 2024  notmeanymore
#
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.
#
#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#Lesser General Public License for more details.
#
#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, see
#<https://www.gnu.org/licenses/>.


import pygame
from pygame.locals import QUIT, KEYDOWN
import random
from pygame import Window
from pygame._sdl2.video import Renderer as _rndr, Texture

pygame.init()
SIZE = pygame.Vector2(16*44, 16*44)

WINDOW = Window(title="Loading...", size=SIZE)
RENDERER = screen = _rndr(WINDOW)

MIDDLE = pygame.Vector2(SIZE.x/2, SIZE.y/2)
PERCENT = pygame.Vector2(SIZE.x/100, SIZE.y/100)
VISIBLE = pygame.Rect(0,0,*SIZE)

def resize(x,y) -> None:
	SIZE.xy = x,y
	MIDDLE.xy = x/2,y/2
	PERCENT.xy = x/100,y/100
	VISIBLE.size = x,y
	WINDOW.size = x,y

_C0NTEXTS = {}

CLOCK = pygame.time.Clock()

Non = pygame.Vector2(0,0)


def loadTexture(path:str):
	return Texture.from_surface(screen,pygame.image.load(path))

def nothing(*a,**k): pass
def col(min=100, max=255,mode="rgba"): return [random.randint(min,max) for i in mode]
def addScene(key, **kw):
	"""
	TODO replace decorator for Scene.__init_subclass__()
	# Arguments:

	- name [str]
	- constantUpdate [bool] (default: False)
	- expectedKeys [list] (default: [])
	- framerate [int] (default: 60)
	- windowName [str] (default: "")
	- windowSize [tuple(int,int)] (default: 704, 704)


	To add a scene:
	----

	@addScene("nameOfScene")

	class CustomSceneName(Scene): pass

	To run a scene:
	----

	- Game("nameOfScene").run() {from outside a scene}
	- self.__game__.changeSceneTo("nameOfScene") {from inside one}
	"""
	def s(f):
		_C0NTEXTS[key] = f(key, **kw)
		return f
	return s



@addScene("_default", constantUpdate=True)
class Scene:
	"""
	# To add a scene:

	@addScene("nameOfScene")

	class CustomSceneName(Scene): pass

	# To run a scene:

	- Game("nameOfScene").run() {from outside a scene}
	- self.__game__.changeSceneTo("nameOfScene") {from inside one}
	"""
	__ID__:list = [-1]
	__byID__:dict = {}
	__globals__:dict = {}

	def play(self): return self.__game__(self.name).run()
	@classmethod
	def nameOf(cls, id:int): return cls.__byID__[id].name
	@classmethod
	def idOf(cls, name:str): return _C0NTEXTS[name].ID

	RENDERER:_rndr = RENDERER
	WINDOW:Window = WINDOW

	def __init__(	self,
					name:str,
					constantUpdate:bool=False,
					expectedKeys:list=[],
					framerate:int=60,
					windowName:str="",
					windowSize:tuple=WINDOW.size,
					windowIcon:pygame.Surface=None
				) -> None:
		self.metadata = {}
		self.name = name
		self.ID = self.__ID__[0]
		self.__byID__[self.ID] = self
		self.__ID__[0] += 1
		self.TICKS_ALL = constantUpdate
		self.keys = expectedKeys
		self.framerate = framerate
		self.windowtitle = windowName
		self.windowSize = windowSize
		self.windowicon = windowIcon
		self.__started__ = False

		self.framerate:int
		self.keys:dict
		self.metadata:dict
		self.name:str
		self.ID:int
		self.TICKS_ALL:bool

		#if (windowSize != WINDOW.size):
		#	x,y = windowSize
		#	if int(WINDOW.size[0]) == x and int(WINDOW.size[1]) == y: pass
		#	else: resize(x,y)


	def changeScene(self, to:str, metadata:dict={}) -> None:
		assert self.__game__
		assert to != self.name
		return self.__game__.changeSceneTo(to, metadata)

	def firstStart(self) -> None: pass
	def close(self) -> None:
		"### It's `Scene.close()`"
		self.__started__ = False
		return self.__game__.changeSceneTo("Close")
	quit = exit = end = done = close #I'm tired of forgetting it's name

	def __globalOnStart__(self, prev:int, meta:dict={}) -> None:
		self.__globalReset__()
		self.onStartPreMeta(prev)
		self.withMetadata(meta)
		self.onReset()
		WINDOW.title = self.windowtitle
		if self.windowicon: WINDOW.set_icon(self.windowicon)
		if (self.windowSize != WINDOW.size):
			x,y = self.windowSize
			if int(WINDOW.size[0]) == x and int(WINDOW.size[1]) == y: pass
			else: resize(x,y)
		if self.__started__: return
		self.__started__ = True
		self.firstStart()

	def onStart(self, prev:int) -> None: pass
	def onStartPreMeta(self, prev:int) -> None: pass #PREVIOUS TO RESET AND AFTER WITHMETA
	def __globalOnEnd__(self, next:int) -> None: pass
	def onEnd(self, next:int) -> None: pass
	def __globalTick__(self) -> None: pass #UNUSED, CALLED EVERY FRAME, NOT ONLY REGISTERED TICKS
	def draw(self,) -> None:
		"""
		Might need to be between:
		---
		
		screen.clear()

		screen.present()
		"""
		self.RENDERER.draw_color = col(mode="RGBA")
		self.RENDERER.clear()
		self.RENDERER.present()
	def run(self,) -> None: pass
		#ONLY TICKS IF (EVENT REGISTERED), (self.TICKS_ALL == True) OR (VALID KEY HELD)
		#NOTE SHOULD NOT CALL .DRAW()
	def __globalEventHandler__(self, e:pygame.event.Event) -> None:
		if e.type == QUIT: return self.close()
	def eventHandler(self, e:pygame.event.Event) -> bool: #RETURN TRUE IF REGISTERED EVENT
		return False #e = individual event
	def __globalKeyHandler__(self, ks:list) -> bool:
		if self.TICKS_ALL: return True
		for i in self.keys:
			if ks[i]: return True
		#if no keys use value of TICK_EVERY, else False
		return False
	def keyHandler(self, ks:list) -> bool: return False
						#IF THIS RETURNS TRUE IT WILL TICK THE SCENE, OTHERWISE
						#IT READS THE VALUE OF __globalKeyHandler__
						#SHOULD ONLY RETURN IF THERE IS AN UNEXPECTED KEY THAT REQUIRES TICKING
						#OR IF SOME KEY SHOULD HAEV LOGIC TO DECIDE IF IT SHOULD TICK OR NOT
						#MAINLY TO "REACT" TO KEYS NOT TO SIGNAL DRAWS
	def __globalReset__(self) -> None:
		self.metadata.clear()
		#self.eat("bugs")
	def onReset(self) -> None: pass
	def withMetadata(self, meta:dict): #data needed at the moment, deleted on __globalReset__()
		if meta: self.metadata.update(meta)	#EXAMPLE: Text to draw on generic dialog bubble
		return self
	def __repr__(self) -> str:
		return f"<Scene '{self.name}'({type(self).__name__}) : ID({self.ID})>"
class MacroScene(Scene):
	_EXIT_ON = 1
	def onReset(self) -> None:
		self.exitCounter = self._EXIT_ON
		self.drawCounter = 1
	def run(self) -> bool:
		if self.exitCounter <= 0:
			return self.close()

	def onKey(self, k:int) -> bool:		pass
	def onMouseUp(self, k:int, pos):	pass
	def onMouseDown(self, k:int, pos):	pass

	def eventHandler(self, e: pygame.event.Event) -> bool:
		if e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE:
			self.exitCounter = self._EXIT_ON

		elif e.type == pygame.KEYDOWN:			return self.onKey(e.key)
		elif e.type == pygame.MOUSEBUTTONUP:	return self.onMouseUp(e.button, e.pos)
		elif e.type == pygame.MOUSEBUTTONDOWN:	return self.onMouseDown(e.button, e.pos)

	def keyHandler(self, ks: list) -> bool:
		if ks[pygame.K_ESCAPE]: self.exitCounter -= 1
@addScene("Close")
class Close(Scene):
	def __init__(self, name:str):
		self.name = name
		self.ID = self.__ID__[0]
		self.__byID__[self.ID] = self
		self.__ID__[0] += 1

	def __globalOnStart__(self, prev:int, meta:dict={}) -> None:
		WINDOW.title = "Bye..."
		raise Done(f"{self.__byID__[prev]} Closed the Game")

class Game:
	def __init__(self, start:str="_default") -> None:
		for v in _C0NTEXTS.values(): v.__game__ = self
		self.should_tick = True
		self.changeSceneTo(start)
		self.scene:Scene
		self.cur:str
		self.should_tick:bool
		self.__started__ = False
		self.currentTick = 0

	def changeSceneTo(self, to:str, metadata:dict={}):
		new:Scene = _C0NTEXTS[to]
		self.cur = to

		if hasattr(self, "scene"):
			self.scene.__globalOnEnd__(new.ID)
			self.scene.onEnd(new.ID)

			new.__globalOnStart__(self.scene.ID, meta=metadata)
			new.onStart(self.scene.ID)
		else:
			new.__globalOnStart__(-1)
			new.onStart(-1)
		self.scene = new
		return new

	def run(self):
		try:
			self.onTick()
			while True:
				CLOCK.tick(self.scene.framerate)
				self.should_tick = self.actionHandler()
				self.onTick()
				#NOTE sigals, etc
		except Done as e:
			print(e,"!")
			return True
		except (Exception, KeyboardInterrupt) as e: raise e from e
		finally: pygame.quit()

	def actionHandler(self): #RETURNS BOOL WETHER IT SHOULD TICK
		events = pygame.event.get()

		ret = False
		for e in events:
			if not (e.__dict__.get("window") in (WINDOW,None)): return
				# handling multiple windows will make core functionality to stop
				# working.  For example resizing will need to be on a per-window
				# basis instead of a global value and therefore so will be
				# getting SIZE, MIDDLE, VISIBLE and other useful variables
				# It's not imposible to implement but it'll break a lot of stuff
				#
				# pop-ups, alerts, floating-guis and other "restrictive" windows
				# on the other hand, are quite possible, their events need to be
				# handled here then perhaps have one dedicated scene-like object
				# for reacting to events, drawing on them and other fancy stuff,
				# for now tho, all of that is on the TODO list.
			self.scene.__globalEventHandler__(e)
			if self.scene.eventHandler(e): ret = True
		keys = pygame.key.get_pressed()
		gk = self.scene.__globalKeyHandler__(keys)
		lk = self.scene.keyHandler(keys)
		return ret or gk or lk

	def onTick(self): #per scene
		self.currentTick += 1
		self.scene.__globalTick__()
		if (self.scene.TICKS_ALL or self.should_tick):
			self.scene.run()
			self.scene.draw()

Scene.__game__:Game

def play(scene:str):
	return Game(scene).run()


#TEMPLATE GAME
"""
from cengine import addScene, MacroScene, screen
import cengine as en
import pygame

@addScene("TemplateGame", constantUpdate=True, windowSize=(160*8,160*5), windowName="Template",framerate=60)
class TemplateGameScene(MacroScene):
	def firstStart(self):
		pass

en.Game("TemplateGame").run()
"""