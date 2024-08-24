"""Used for oop mode"""
__version__ = "0.0.2" # 2024.08
__author__ = "S. Gebert <nomisge @ live . de>"
__all__ = ['PWidget', 'PSurface','PWidgetMeta','PSignals']

from pysideprocessing.pimage import PImage, PixelArray
from pysideprocessing.color import color
from pysideprocessing.pgraphics import PGraphics, Graphics, Paintable

from abc import abstractmethod, ABC
from typing import Optional, Callable
from functools import wraps

from PySide6.QtWidgets import QMainWindow, QLabel
from PySide6.QtCore import Property, QRect, Qt, QObject, Slot, Signal
from PySide6.QtGui import QPainter, QPixmap, QImage, QPaintEvent

from collections import deque
from decopatch import function_decorator, DECORATED

# from typing import TypeVar, Generic

# T = TypeVar("T")
# 
# class UndoRedo(Generic[T]):
# 
#     HISTORY_SIZE: int = 2 # Anzahl rückgängig machbarer Schritte
#     _history: deque[T]
# 
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self._history = deque()
#     
#     @property
#     def history(self) -> deque[T]:
#         """the history of the states"""
#         return self._history
#     @history.setter
#     def history(self, history: deque[T]):
#         self._history = history
#       
#     @abstractmethod
#     def undo(self):
#         """for undoing the history of the states"""
#     @abstractmethod
#     def redo(self):
#         """for redoing the history of the states"""

class _ShibokenObjectTypeFence(type(QObject)): # type: ignore[misc]
    """
    This solve for:
        TypeError: Shiboken.ObjectType.__new__(PWidgetMeta) is not safe, use type.__new__()

    Principle is to "please" the check done in Objects/typeobject.c:tp_new_wrapper function by
    making look like the "most derived base that's not a heap type" has the same tp_new function
    than Shiboken.ObjectType.

    Another way could have been to declare PWidgetMeta with type(QWidget) first.
    But if you do that, ABCMeta.__new__ is not called, and its internal states do not get properly
    initialised. (Same for any other metaclass you may want to use actually.)
    I guess because Shiboken.ObjectType is not cooperative and does not call the __new__ of
    super types.

    Inserting such "fence" type at the beginning of the metaclass MRO works because:
    - tp_new_wrapper will be happy, and not throw the "not safe" error.
    - As type(QWidget) is also declared further down the MRO, its final (and unique) position in
      the MRO will be that later one, instead of right after the position of this fence type.
      Meaning we still get to normally call other metaclasses __new__ before reaching
      Shiboken.ObjectType.__new__
      
    source: https://bugreports.qt.io/browse/PYSIDE-1767
    """
    ...

class PWidgetMeta(_ShibokenObjectTypeFence, type(ABC), type(QObject)): # type: ignore[misc]
    """
    This solve for:
        TypeError: metaclass conflict: the metaclass of a derived class
        must be a (non-strict) subclass of the metaclasses of all its bases
        
    source: https://bugreports.qt.io/browse/PYSIDE-1767
    """
    ...

class PaintableGraphicsLabel(QLabel, Graphics, Paintable, metaclass=PWidgetMeta):
    HISTORY_SIZE: int = 2 # Anzahl rückgängig machbarer Schritte
    _history: deque[QPixmap]

    def __new__(cls, *args, **kwargs):
        '''
        This solve for abstraction check not being done by Shiboken.Object.
        Normally, abstraction check is is done by Objects/typeobject.c:object_new.
        NB: cls.__abstractmethods__ is set and populated by ABCMeta.__new__ already.
        
        source: https://bugreports.qt.io/browse/PYSIDE-1767
        '''
        if cls.__abstractmethods__:
            s = 's' if len(cls.__abstractmethods__) > 1 else ''
            raise TypeError(
                f'Can\'t instantiate abstract class {cls.__name__} '
                f'with abstract method{s} {", ".join(cls.__abstractmethods__)}'
            )

        return super().__new__(cls, *args, **kwargs)
    #
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._history = deque()
    
    @property
    def history(self) -> deque[QPixmap]:
        """the history of the states"""
        return self._history
    @history.setter
    def history(self, history: deque[QPixmap]):
        self._history = history
      
    @abstractmethod
    def undo(self):
        """for undoing the history of the states"""
    @abstractmethod
    def redo(self):
        """for redoing the history of the states"""

@function_decorator
def image_modification(method: Callable[...,None]=DECORATED) -> Callable[...,None]:
    @wraps(method)
    def _impl(self,*method_args, **method_kwargs):
        self.push_image()
        method(self,*method_args, **method_kwargs)
        self.update_image()
    return _impl  

class PWidget(PaintableGraphicsLabel, metaclass=PWidgetMeta):
    """Base class for all Sketches that use...
    """
        
    #maybe not use QLabel but other widget that has QPixmap
    _pixmap: QPixmap #das aktuelle Bild
    _image: Optional[PImage]
    _pixels: PixelArray

    _graphics: PGraphics
    _painter: QPainter    
             
    # Zoom Faktor
    zoom_factor: float
    ZOOM_FIT: int = -1 #FIT = -1;
    ZOOM_NORMAL: int  = 1#NORMAL = 1;
  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._image = None
        self.zoom_factor = 1        
        self._pixmap = QPixmap()
        self._painter = QPainter()
        
        self._graphics = PGraphics(self)   
#         self.background(0xffd3d3d3)  #not working, since paint_device not yet ready   
        self.stroke(color("black"))
        self.fill(color("white"))
        self.text_size(12)        

    def setup(self):
        """setup-Methode
        """
        ...
    
    def draw(self):
        """draw-Methode
        """
        ...
    
    @property
    def painter(self):
        return self._painter
    
    @Property(int) # type: ignore[operator]
    def width(self) -> int:
        return self._pixmap.width()
    @Property(int) # type: ignore[operator]
    def height(self) -> int:
        return self._pixmap.height()
       
    @image_modification
    def set_size(self, width: int, height: int):
        #TODO: Raise error if called from elsewhere than setup, or more than once
        self._image = None
        oldpix = self._pixmap.copy(0,0,width,height)
        self._pixmap = QPixmap(width, height)
        self.clear() #don't change background color, only fill background
        self.resize(self._pixmap.size())
        self._painter.begin(self._pixmap)
        self._painter.drawPixmap(0,0,oldpix)
        self._painter.end()
        
    @property
    def pixels(self) -> PixelArray:
        """Bilddaten als ein oder zweidimensionales Pixel-Array.
        
        Returns
        -------
        list[list[QColor]]
            zweidimensionales QColor-Array
        """
        if self._image is None:
            raise Exception("Image not loaded")
        return self._image.pixels
    
    @pixels.setter
    def pixels(self, pixels:PixelArray):
        """
        
        Parameters
        ----------
        pixels : array_like
            ein oder zweidimensionales Array von QColor-Objekten
        """
        if self._image is None:
            raise Exception("Image not loaded")
        self._image.pixels  = pixels
 
    def load_pixels(self):
        """Läd die Pixel Daten des momentan angezeigten Bilds in die pixels[] Liste.
        """
        self._image = PImage(filename= self._pixmap.toImage())
        self._image.load_pixels()
        #TODO set image format
        
    def update_pixels(self):
        """Setzt das Bild neu auf Basis des Pixel-Arrays.

        Die Groesse des Bildes wird nicht automatisch an das Array angepasst.
        """
        if self._image is None:
            raise Exception("pixels not loaded") # TODO meaningful exception
        
        self.push_image()
        self._image.update_pixels()
        self._pixmap = QPixmap.fromImage(self._image.get_image())
        self.update_image()
                                                                                                                                                                                                                                                                                                                   
    def paintEvent(self, e: QPaintEvent):
        super().paintEvent(e)  
        self.setPixmap(self._pixmap)
    
    def painter_begin(self):
        self._painter.begin(self._pixmap)
    
    def painter_end(self):
        self._painter.end()
        self.update()
        
    def push_image(self):
        """Speichert das aktuell angezeigte Bild in der history
        """
        if self.HISTORY_SIZE > 0:
            if len(self.history) == self.HISTORY_SIZE:
                self.history.popleft()
            self.history.append(self._pixmap.copy())

    def update_image(self):
        self.update()

    def undo(self):
        """Ruft das letzte abgespeicherte Bild aus der History wieder auf.
        """
        if len(self.history) > 0:
            self._pixmap = self.history.pop()
            self.update()
            
    def redo(self):
        raise NotImplementedError()
    
    def set_pixmap(self, pixmap: QPixmap, save_old_image: bool = False):
        if save_old_image:
            self.push_image()
        self._pixmap = pixmap
        self.resize(self._pixmap.size())
        self.update_image()
    
    def get_pixmap(self) -> QPixmap:
        return self._pixmap
    
    def get_paint_device(self) -> QPixmap|QImage:
        return self._pixmap
    
    def get_image(self) -> PImage:     
        return PImage(filename=self._pixmap.toImage())
    
    def set_zoom(self, factor: float):
        pass

# -- Methods to work on picture --
# --- Zeichnenfunktionen ---
    @Slot()
    @image_modification
    def clear(self):
        self._graphics.clear()
    
    def rect_mode(self, mode: int):
        self._graphics.rect_mode(mode)
        
    def ellipse_mode(self, mode: int):
        self._graphics.ellipse_mode(mode)
        
    #TODO: arc, circle
#     def arc
#     def circle
    @Slot(int,int,int,int)
    @image_modification
    def ellipse(self,  a: int, b: int, c: int, d: int):
        self._graphics.ellipse(a,b,c,d)
    
    @Slot(int,int,int,int)
    @image_modification
    def line(self, x1:int, y1:int, x2:int, y2:int):
        self._graphics.line(x1,y1,x2,y2)

    @Slot(int,int)
    @image_modification
    def point(self, x:int, y:int):
        self._graphics.point(x,y)
    
    @Slot(int,int,int,int,int,int,int,int)
    @image_modification
    def quad(self, x1:int, y1:int,x2:int,y2:int, x3:int, y3:int, x4:int, y4:int):
        self._graphics.quad(x1,y1,x2,y2,x3,y3,x4,y4)
   
    @Slot(int,int,int,int)
    @image_modification
    def rectangle(self, a: int, b: int, c: int, d: int):
        self._graphics.rectangle(a,b,c,d)
#         self._painter.drawRect(a,b,c,d)

    @Slot(int,int,int)
    @image_modification
    def square(self, x:int, y:int, extend:int):
        self._graphics.square(x,y,extend)

    @Slot(int,int,int,int,int,int)
    @image_modification
    def triangle(self, x1:int, y1:int,x2:int,y2:int, x3:int, y3:int):
        self._graphics.triangle(x1,y1,x2,y2,x3,y3)
        
    @Slot(str,int,int)
    @image_modification
    def text(self, s:str, x:int, y:int):
        self._graphics.text(s,x,y)

# --- Farbfestlegungen ---
    #TODO: Slot
    def get(self, x: int, y: int) -> color:
        """Der Farbwert an der Position x,y de"""
        raise NotImplementedError()
    
    @Slot(color)
    def stroke(self, pencolor: color):
        self._graphics.stroke(pencolor)
    
    @Slot()
    def no_stroke(self):
        self._graphics.no_stroke()
        
    @Slot(int)
    def stroke_weight(self, weight: int):
        self._graphics.stroke_weight(weight)
    
    @Slot(color)
    def fill(self, fillcolor: color):
        self._graphics.fill(fillcolor)
    
    @Slot()
    def no_fill(self):
        """Legt fest, dass die Formen nicht gefüllt werden sollen.
        """
        self._graphics.no_fill()
    
    @Slot(color)
    @image_modification
    def background(self, argb: color):
        #TODO: allow images or numbers etc. instead of argb int    
        self._graphics.background(argb)
        
    @Slot(str)
    def text_font(self, font: str=""):
        self._graphics.text_font(font)
    
    @Slot(int)
    def text_size(self, size: int):
        self._graphics.text_size(size)
        
# --- Dateioperationen ---
    def image_mode(self):
        raise NotImplementedError
    
    def create_image(self):
        raise NotImplementedError

    def load_image(self, filename: str) -> PImage:
        """Lädt ein Bild aus dem Dateisystem

        Lädt ein Bild von einem Datentraeger und setzt Stiftfarbe und Fuellfarbe auf Standardwerte zurück.
        
        Parameters
        ----------
        filename : str
            Dateiname des Bildes
        """
        #TODO: implement some checks if file exisits
        #TODO: reset settings
        return PImage(filename=filename)
        
    def image(self, image:PImage, x:int,y:int, width: int = -1, height: int = -1):
        if width < 0: width = self.width
        if height < 0: height = self.height
        
        self._painter.begin(self._pixmap)
        self._painter.drawPixmap(QRect(x,y,width,height),image.pixmap, QRect(0,0,self.width, self.height))
        self._painter.end()
    
    def save(self, filename: str, format: Optional[str]=None, quality:int=-1):
        """Speichert ein Bild.

        Speichert ein Bild auf einem Datentraeger. Zulaessig sind die Dateiformate PNG und GIF. Die Dateiendung legt den Typ fest.
        Standardmaessig wird die Dateiendung .png ergaenzt, wenn keine angegeben ist.
        
        Parameters
        ----------
        filename : str
            Dateiname des Bildes
        format : str, optional
        quality : int, optional
        """
        self._pixmap.save(filename, format, quality)
        
# --- Sonstiges ---   
    def delay(self, millis: int):
        """Hilfsfunktion zum Verzoegern der Ausgabe

        Parameters
        ----------
        millis : int
            Wartezeit in Millisekunden
        """
        raise Exception("Can only be used in applet mode")

class PSignals(QObject):
    clear = Signal()
    ellipse = Signal(int,int,int,int)
    line = Signal(int,int,int,int)
    point = Signal(int,int)
    quad = Signal(int,int,int,int,int,int,int,int)
    rectangle = Signal(int,int,int,int)
    square = Signal(int,int,int)
    triangle = Signal(int,int,int,int,int,int)
    text = Signal(str,int,int)
    stroke = Signal(color)
    no_stroke = Signal()
    stroke_weight = Signal(int)
    fill = Signal(color)
    no_fill = Signal()
    background = Signal(color)
    text_font = Signal(str)
    text_size = Signal(int)
    painter_begin = Signal()
    painter_end = Signal()

    def __init__(self, sketch: PWidget):
        super().__init__()
        self.sketch = sketch
        self.clear.connect(sketch.clear)
        self.ellipse.connect(sketch.ellipse)
        self.line.connect(sketch.line)
        self.point.connect(sketch.point)
        self.quad.connect(sketch.quad)
        self.rectangle.connect(sketch.rectangle)
        self.square.connect(sketch.square)
        self.triangle.connect(sketch.triangle)
        self.text.connect(sketch.text)
        self.stroke.connect(sketch.stroke)
        self.no_stroke.connect(sketch.no_stroke)
        self.stroke_weight.connect(sketch.stroke_weight)
        self.fill.connect(sketch.fill)
        self.no_fill.connect(sketch.no_fill)
        self.background.connect(sketch.background)
        self.text_font.connect(sketch.text_font)
        self.text_size.connect(sketch.text_size)
        self.painter_begin.connect(sketch.painter_begin)
        self.painter_end.connect(sketch.painter_end)

class PSurface(QMainWindow):
    """Standard Surface

    """
    #TODO: Implement class mode: can be run in class (without papplet.py)
#     class _SetupSingle(QObject):
#         def __init__(self, sketch, *args, **kwargs):
#             super().__init__()
#             self._sk = sketch
#             self.args = args
#             self.kwargs = kwargs
#         
#     class _DrawLoop(QObject):
#         def __init__(self, sketch, *args, **kwargs):
#             super().__init__()
#             self._sk = sketch
#             self.args = args
#             self.kwargs = kwargs
#             
# #         @Slot()
#         def loop(self):
#             self._draw_timer = QTimer()
# #             self._draw_timer.setSingleShot(False)
#             self._draw_timer.setTimerType(Qt.TimerType.PreciseTimer)
#             self._draw_timer.setInterval(int(1000/60))
#             self._draw_timer.timeout.connect(self._sk.draw) # type: ignore[attr-defined]
# 
#             self.thread().finished.connect(self.stop_draw_timer)
#             self._draw_timer.start()
#             for i in range(5000):
#                 time.sleep(0.05)
#                 QApplication.processEvents()
#                 
#         def start_draw_timer(self):
#             print("start")
#             
#         def stop_draw_timer(self):
#             print("stop")
#     class _Setup(QObject):
#         def __init__(self,sketch, *args, **kwargs):
#             signals = PSignals(sketch)
#                         
    
    def __init__(self, canvas: PWidget):
        super().__init__()
        #possibility for transparency in background      
        self.setAttribute(Qt.WA_TranslucentBackground) # type: ignore[attr-defined]
        self.setCentralWidget(canvas)
        self._canvas = canvas
        
#         self.count_time = 1

#         self._draw_thread = QThread()
#         draw_loop = self._DrawLoop(self._canvas)
#         draw_loop.moveToThread(self._draw_thread)
#         
#         self._draw_thread.started.connect(draw_loop.loop)
#         
#         self._draw_thread.start()
#         self._setup_thread = QThread()
#         
# #         self._canvas.setup()
#         
#         self._draw_timer = QTimer()
# #             self._draw_timer.setSingleShot(False)
#         self._draw_timer.setTimerType(Qt.TimerType.PreciseTimer)
#         self._draw_timer.setInterval(int(1000/60))
#         self._draw_timer.timeout.connect(self._canvas.draw) # type: ignore[attr-defined]
# 
#         self._draw_timer.start()
    
#     def stop_loop(self):
#         self._draw_thread.quit()
#                 
#     def delay(self,millis):
#         self._draw_thread.quit()
#         init_time = time.perf_counter()
#         print(f"delay start {self.count_time}")
#         time_not_passed = True
#         while time_not_passed: # Init loop
#             if init_time + millis/1000 <= time.perf_counter():
#                 time_not_passed = False
# #             time.sleep(millis/1000)
#         self.count_time += 1

