from cengine import addScene, MacroScene, screen
import cengine as en

import pygame as pg

from pygame import Rect as _Rect, Vector2
from pygame._sdl2.video import Texture

import os, json, random
from math import sin, cos, tan
import functools


ROOT = os.path.realpath(__file__).rsplit("/",1)[0]+"/"

class Vector(Vector2):
	@property
	def xi(self): return int(self.x)
	@property
	def yi(self): return int(self.y)
	@property
	def xyi(self): return int(self.x),int(self.y)


@functools.cache
def cachedJson(path:str):
	with open(path, "r") as f: t = json.load(f)
	return t


Rect = _Rect

TX = {}
SR = {}
@functools.cache
def _loadIMG(path:str):
	if path in SR: return SR[path]
	ret = pg.image.load(path)
	SR[path] = ret
	return ret
@functools.cache
def loadTexture(path:str) -> Texture:
	if path in TX: return TX[path]
	ret = Texture.from_surface(en.RENDERER, _loadIMG(path))
	TX[path] = ret
	ret.blend_mode = 1
	return ret

UNITS = {
	"u":Vector(0, 1), #"s"
	"d":Vector(0,-1), #"w"
	"l":Vector(-1,0), #"a"
	"r":Vector( 1,0), #"d"
}


def setCol(r=None,g=None,b=None):
	R,G,B,_ = screen.draw_color
	screen.draw_color = r if r!=None else R,g if g!=None else G,b if b!=None else B, _


class Thing:
	def allTicks(self):
		self.onTick(self)
	def onTick(self):
		pass
	def draw(self):
		pass




def nastyCheckRect(vec:Vector,obstacle:Rect,rect:Rect):
		#wow this took a while
		O,R = obstacle,rect
		if not vec: return vec
		_x,_y = vec
		nx = ny = 0
		if _x > 0: nx = 1
		elif _x < 0: nx = -1
		if _y > 0: ny = 1
		elif _y < 0: ny = -1
		fx = fy = False
		if ny ==-1 and R.bottom > O.top:
			(X,Y),L = O.bottomleft,O.width
			(x,y),l = R.topleft,R.width
			if x+l > X and x < X+L and y+_y < Y:
				_y = Y-y
				fx = True
		elif ny == 1 and R.top < O.bottom:
			(X,Y),L = O.topleft,O.width
			(x,y),l = R.bottomleft,R.width
			if x+l > X and x < X+L and y+_y > Y:
				_y = Y-y
				fx = True
		if nx ==-1 and R.right > O.left:
			(X,Y),L = O.topright,O.height
			(x,y),l = R.topleft,R.height
			if y+l > Y and y < Y+L and x+_x < X and not fx:
				_x = X-x
				fy = True
		elif nx == 1 and R.left < O.right:
			(X,Y),L = O.topleft,O.height
			(x,y),l = R.topright,R.height
			if y+l > Y and y < Y+L and x+_x > X and not fx:
				_x = X-x
				fy = True
		if fx and fy: raise Exception("Moved wrongly")
		#R.x += _x
		#R.y += _y
		#vec.x = vec.y = 0
		return Vector(_x, _y)



class Obstacle(Thing):
	def __init__(self,x:int,y:int,w:int,h:int,hitbox:list=[],
			bg:str|None=None,fg:str|None=None ):
		self.rect = Rect(x,y,w,h) #This is for drawing and similar
		self.hitboxes = [Rect(i).move(x,y) for i in hitbox] #These are solids
		self.bg = loadTexture(bg) if isinstance(bg, str) else None
		self.fg = loadTexture(fg) if isinstance(fg, str) else None

	def scaleBy(self, scale:int, hitSize:tuple[bool]|None=None):
		c = Vector(self.rect.topleft)*scale
		self.rect.scale_by_ip(scale,scale)
		self.rect.topleft = c
		h = hitSize
		if h == None: h0 = h1 = h2 = h3 = scale
		elif isinstance(h, int): h0 = h1 = h2 = h3 = h
		else: h0, h1, h2, h3 = h
		for n,r in enumerate(self.hitboxes):
			self.hitboxes[n] = Rect(r.left*h0,r.top*h1,r.width*h2,r.height*h3)
		return self
	def draw(self):
		if self.bg == None: return
		self.bg.draw(dstrect=self.rect)
		#setCol(255,0,0)
		#screen.draw_rect(self.rect)
		#setCol(0,0,255)
		#for i in self.hitboxes: screen.fill_rect(i)
	def drawDetail(self):
		if self.fg == None: return
		self.fg.draw(dstrect=self.rect)
	def rectHits(self, target:Rect, move:Vector) -> Vector:
		if not self.hitboxes: return move
		if len(self.hitboxes) == 1:
			r = self.hitboxes[0]
			return nastyCheckRect(move, r, target)
		else:
			raise NotImplementedError("Multiple hitbox checks are not possible yet")
			for r in self.hitboxes:
				"if no contanct pass, if contact save distance"
			"shortest distance to contact is the one allowed"
			"then add distance from that to second shortest (slide)"
			"""	|
			🭻🭻🬷
			  ∧
			  |
			  | 🬕🭶🭶🭶🭶
			 /	|
			"""


class SavedObstacle(Obstacle):
	def __init__(self, name:str, x:int,y:int,w:int=None,h:int=None):
		self.path = p = ROOT+f"data/Obstacles/{name}/"
		self.JS = JS = cachedJson(p+"meta.json")
		TO = {
			"hitbox":JS.get("hitbox",[]),
			"bg":None, "fg":None,
			"w":w or JS.get("w"),
			"h":h or JS.get("h"),
		}
		if "textures-choice" in JS:
			k = JS["textures-choice"]
			bg,fg = random.choice(k)
			TO["bg"],TO["fg"] = self.path+bg,self.path+fg
		super().__init__(x,y,**TO)
		if "scale" in JS: self.scaleBy(**JS["scale"])


#Tree = Obstacle(16*14,16*10,16*10,16*19,[Rect(16*4,16*17,32,1)])
#Tree = Obstacle(14,10,10,19,[Rect(4,17,2,1)]).scaleBy(16,(16,16,16,1))
#Tree = SavedObstacle("Tree", 17,10, )




class Player(Thing):
	rect = Rect(0,0,32,64)
	def __init__(self):
		self.rect.center = en.MIDDLE
		self.movect = Vector(0)
		self._age = 0
		self.texture = loadTexture(ROOT+"data/Player/texture.png")
	def onTick(self):
		self._age += 1
	def draw(self):
		a = self._age/55
		setCol((sin(a)+1)*64, (sin(a+2)+1)*64, (sin(a+4)+1)*64)
		screen.fill_rect(self.rect)
		self.texture.draw(dstrect=self.rect)
	def touchesBorder(self):
		r = ""
		if self.rect.bottom > en.VISIBLE.bottom: r += "u"
		if self.rect.top < en.VISIBLE.top: r += "d"
		if self.rect.left < en.VISIBLE.left: r += "l"
		if self.rect.right > en.VISIBLE.right: r += "r"
		return r


WORLDS = {}


class WorldTile:
	def __init__(self, *k, **kw):
		self._THINGS = []
		self.onInit(*k, **kw)
	def onInit(self): pass
	def draw(self): pass
	def detail(self):
		for i in self._THINGS: i.drawDetail()
	def drawThings(self):
		for i in self._THINGS: i.draw()

class ColTile(WorldTile):
	def onInit(self, r,g,b):
		self.rgb = int(r),int(g),int(b)
	def draw(self):
		setCol(*self.rgb)
		screen.clear()

class VoidObject(WorldTile):
	t = 0
	def draw(self):
		self.t += 0.1
		t = self.t
		c = int(sin(t)*32)+223
		setCol(c,c,c)
		screen.clear()

Void = VoidObject()


@functools.cache
def _genericTicker(age:int):
	return not age%12



class AnimatedTexture:
	def __init__(self, root:str, *path:list[str], _tf=_genericTicker):
		self.textures:list[Texture] = [loadTexture(os.path.join(root,i)) for i in path]
		self.sel = 0
		self._age = 0
		self._tf = _tf
	def tick(self):
		self.sel += 1
		self.sel %= len(self.textures)
	@property
	def cur(self): return self.textures[self.sel]
	@property
	def color(self) -> pg.Color: return self.cur.color
	@color.setter
	def color(self, value) -> None:
		for i in self.textures: i.color = value
	def get_rect(self, **kwargs) -> Rect: return self.cur.get_rect(**kwargs)
	def draw(
		self,
		srcrect:Rect = None,
		dstrect:Rect = None,
		angle:float = 0.0,
		origin:Vector = None,
		flip_x:bool = False,
		flip_y:bool = False,
	) -> None:
		self._age += 1
		self._age %= 2310 #2*3*5*7*11
		if self._tf(self._age): self.tick()
		self.cur.draw(srcrect, dstrect, angle, origin, flip_x, flip_y)
	def draw_triangle(
		self,
		p1_xy:Vector,
		p2_xy:Vector,
		p3_xy:Vector,
		p1_uv:Vector = (0.0, 0.0),
		p2_uv:Vector = (1.0, 1.0),
		p3_uv:Vector = (0.0, 1.0),
		p1_mod:list = (255, 255, 255, 255),
		p2_mod:list = (255, 255, 255, 255),
		p3_mod:list = (255, 255, 255, 255),
	) -> None: self.cur.draw_triangle(
		p1_xy,p2_xy,p3_xy,p1_uv,p2_uv,p3_uv,p1_mod,p2_mod,p3_mod)
	def draw_quad(
		self,
		p1_xy:Vector,
		p2_xy:Vector,
		p3_xy:Vector,
		p4_xy:Vector,
		p1_uv:Vector = (0.0, 0.0),
		p2_uv:Vector = (1.0, 0.0),
		p3_uv:Vector = (1.0, 1.0),
		p4_uv:Vector = (0.0, 1.0),
		p1_mod:list = (255, 255, 255, 255),
		p2_mod:list = (255, 255, 255, 255),
		p3_mod:list = (255, 255, 255, 255),
		p4_mod:list = (255, 255, 255, 255),
	) -> None: self.cur.draw_quad(
		p1_xy,p2_xy,p3_xy,p4_xy,p1_uv,p2_uv,p3_uv,p4_uv,p1_mod,p2_mod,p3_mod,p4_mod)






class SavedTile(WorldTile):
	def onInit(self, name):
		p = ROOT+f"data/Worlds/{name}/"
		k = cachedJson(p+"meta.json")

		def _xtemp(dat:str|list|None):
			if dat == None: return
			if isinstance(dat, str): 
				try: return loadTexture(p+dat)
				except FileNotFoundError:
					return print(f"File {p}{dat} not found, ignoring")
			if isinstance(dat, list): return AnimatedTexture(p,*dat)
		
		self.bg = _xtemp(k.get("bg"))

		print(self.bg)

		self.fg = _xtemp(k.get("fg"))

		for o in k.get("tiles",""):
			WORLDS[tuple(o)] = self
			for t in k.get("obstacles", ""):
				self._THINGS.append(SavedObstacle(*t))


	def draw(self):
		if self.bg: self.bg.draw()
	def detail(self):
		if self.fg: self.fg.draw()
		super().detail()




def loadWorlds(name:str):
	TIL = SavedTile(name)
	


for i in os.listdir(ROOT+"data/Worlds"): loadWorlds(i)
#loadWorlds("Debug")



#WORLDS[0,0]._THINGS.append(Tree)
#WORLDS[0,0]._THINGS.append(Tree)


@addScene("EvGame", constantUpdate=True, windowSize=(32*32,32*20), windowName="Template",framerate=60)
class EvGameScene(MacroScene):
	def firstStart(self):
		self.me = Player()
		self.curWorldC = c = [0,0]
		self.curWorld = WORLDS.get(tuple(c), Void)
		en.WINDOW.position = (pg.WINDOWPOS_CENTERED)
	def run(self):
		super().run()
		self.me.onTick()
		for i in self.me.touchesBorder(): self.moveWorld(UNITS[i])
		v = self.me.movect
		if not v: return
		for i in self.curWorld._THINGS: v = i.rectHits(self.me.rect, v)
		self.me.rect.center += v
		self.me.movect.x = self.me.movect.y = 0


	def moveWorld(self, by):
		x,y = by.xyi
		self.curWorldC[0] += x
		self.curWorldC[1] += y
		if x == 1: self.me.rect.left = 0
		elif x == -1: self.me.rect.right = en.SIZE.x
		if y == 1: self.me.rect.top = 0
		elif y == -1: self.me.rect.bottom = en.SIZE.y
		self.curWorld = WORLDS.get(tuple(self.curWorldC), Void)
	def draw(self):
		#setCol(0,0,0)
		#screen.clear()
		self.curWorld.draw()
		self.curWorld.drawThings()
		self.me.draw()
		self.curWorld.detail()
		screen.present()

	def keyHandler(self, ks: list) -> bool:
		super().keyHandler(ks)
		sp = 4
		if isPressed(ks,"Walk up"):		self.me.movect -= UNITS["u"]*sp
		if isPressed(ks,"Walk down"):	self.me.movect -= UNITS["d"]*sp
		if isPressed(ks,"Walk left"):	self.me.movect += UNITS["l"]*sp
		if isPressed(ks,"Walk right"):	self.me.movect += UNITS["r"]*sp
		#K_DOWN, K_UP, K_LEFT, K_RIGHT


KEYBINDS = {
	"Walk up":(pg.K_UP,pg.K_w),
	"Walk down":(pg.K_DOWN,pg.K_s),
	"Walk left":(pg.K_LEFT,pg.K_a),
	"Walk right":(pg.K_RIGHT,pg.K_d),
	"Action":(pg.K_SPACE,None),
	"Test":(pg.K_F9,None),
}
def isPressed(ks:list, target:str):
	if target not in KEYBINDS: return False
	p,s = KEYBINDS[target]
	return (ks[p] if p else False) or (ks[s] if s else False)




@addScene("RectTest", constantUpdate=True, windowSize=(32*32,32*20), windowName="Template",framerate=60)
class RectTest(MacroScene):
	def firstStart(self):
		self.R = Rect(0,0,50,50)
		self.R.center = en.MIDDLE

		self.O = Rect(100,100,150,215)

		self.movect = Vector(0,0)

	def keyHandler(self, ks: list) -> bool:
		super().keyHandler(ks)
		sp = random.randint(3,6)
		if isPressed(ks,"Walk up"): self.movect -= UNITS["u"]*sp
		if isPressed(ks,"Walk down"): self.movect -= UNITS["d"]*sp
		if isPressed(ks,"Walk left"): self.movect += UNITS["l"]*sp
		if isPressed(ks,"Walk right"): self.movect += UNITS["r"]*sp


	def draw(self):
		setCol(0,0,0)
		screen.clear()
		setCol(0,255,0)
		O,R = self.O,self.R

		screen.draw_rect(O)
		setCol(255,0,0)
		screen.draw_rect(R)
		setCol(255,255,0)

		if not self.movect: return screen.present()
		_x,_y = self.movect
		nx = ny = 0
		if _x > 0: nx = 1
		elif _x < 0: nx = -1
		if _y > 0: ny = 1
		elif _y < 0: ny = -1
		fx = fy = False
		#wow this took a while
		if ny ==-1 and R.bottom > O.top:
			(X,Y),L = O.bottomleft,O.width
			(x,y),l = R.topleft,R.width
			if x+l > X and x < X+L and y+_y < Y:
				_y = Y-y
				fx = True
		elif ny == 1 and R.top < O.bottom:
			(X,Y),L = O.topleft,O.width
			(x,y),l = R.bottomleft,R.width
			if x+l > X and x < X+L and y+_y > Y:
				_y = Y-y
				fx = True
		if nx ==-1 and R.right > O.left:
			(X,Y),L = O.topright,O.height
			(x,y),l = R.topleft,R.height
			if y+l > Y and y < Y+L and x+_x < X and not fx:
				_x = X-x
				fy = True
		elif nx == 1 and R.left < O.right:
			(X,Y),L = O.topleft,O.height
			(x,y),l = R.topright,R.height
			if y+l > Y and y < Y+L and x+_x > X and not fx:
				_x = X-x
				fy = True
		if (fx and fy): raise Exception("Moved wrongly")
		R.x += _x
		R.y += _y
		self.movect *= 0
		screen.present()




#en.play("RectTest")
en.play("EvGame")
