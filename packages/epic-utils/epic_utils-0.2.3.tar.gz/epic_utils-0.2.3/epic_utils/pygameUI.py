from .core import Vector2, Color
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg

class UIObject:
    def __init__(self, parent, position : Vector2, size : Vector2, backgroundColor : Color = Color.White, anchorPoint : Vector2 = Vector2.zero):
        self.position = position
        self.size = size
        self.anchorPoint : Vector2 = anchorPoint
        self.backgroundColor : Color = backgroundColor
        self.children = []
        self.parent = parent
        self.parent.addChild(self)
    def get_Rect(self):
        return pg.Rect(self.position.x, self.position.y, self.size.x, self.size.y)
    def draw(self, screen : pg.Surface):
        screen.fill(self.backgroundColor.toTuple(), self.get_Rect())
    def addChild(self, child):
        self.children.append(child)
    def removeChild(self, child):
        self.children.remove(child)
        
    def delete(self):
        self.parent.removeChild(self)
        del self


class TextLabel(UIObject):
    def __init__(self, parent, position : Vector2, size : Vector2, text : str, font : pg.font.Font, textColor : Color, backgroundColor : Color = Color.White, anchorPoint : Vector2 = Vector2(0, 0)):
        super().__init__(parent, position, size, backgroundColor=backgroundColor, anchorPoint=anchorPoint)
        self.text : str = text
        self.font = font
        self.textColor : Color = textColor
        self.renderedText = self.font.render(self.text, True, self.textColor.toTuple())
    def changeText(self, text : str):
        self.text = text
        self.renderedText = self.font.render(self.text, True, self.textColor.toTuple())
    def draw(self, screen : pg.Surface):
        super().draw(screen)
        screen.blit(self.renderedText, (self.position.x, self.position.y))

class Application:
    def __init__(self, size : Vector2, title : str, updateFunction = None):
        self.size : Vector2 = size
        self.title : str = title
        self.running = True
        self.clock = pg.time.Clock()
        self.fps = 60
        self.display = pg.display.set_mode(self.size.toTuple())
        self.updateFunction = updateFunction
        self.children = []
        pg.display.set_caption(self.title)
        
        
        #Init Pygame
        pg.font.init()
        
    def setFPS(self, fps : int):
        self.fps = fps
    def addChild(self, child : UIObject):
        self.children.append(child)
    def drawChildren(self, obj : UIObject):
        for child in obj.children:
            child.draw(self.display)
            if (len(child.children) > 0):
                self.drawChildren(child)
    def draw(self):
        self.drawChildren(self)
    def run(self):
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
            self.draw()
            pg.display.update()
            if self.updateFunction != None:
                self.updateFunction(pg.event.get())
            self.clock.tick(self.fps)
        
        
if __name__ == "__main__":
    app = Application(Vector2(800, 600), "Test")
    
    l = TextLabel(app, Vector2(0, 0), Vector2(100, 100), "Hello World", pg.font.SysFont("Calibri", 36), Color(0, 0, 0))
    
    app.run()