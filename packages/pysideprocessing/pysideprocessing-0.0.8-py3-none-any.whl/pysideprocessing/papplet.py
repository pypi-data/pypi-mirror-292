"""Used for sketch mode"""
__version__ = "0.0.4" # 2024.08
__author__ = "S. Gebert <nomisge @ live . de>"
# __all__ = ['sketch_setup', 'sketch_draw', 'sketch',
#            'width', 'height', 'set_size', 'set_zoom',
#            'load_pixels', 'update_pixels', 'get',
#            'push_image', 'undo', 'redo',
#            'clear', 'rect_mode', 'ellipse_mode', 'image_mode',
#            'ellipse', 'line', 'point', 'quad', 'rectangle', 'square', 'triangle',
#            'text', 'text_font', 'text_size',
#            'stroke', 'no_stroke', 'stroke_weight', 'fill', 'no_fill', 'background',
#            'create_image', 'load_image', 'save', 'image', 'delay']

import sys, threading, time

from PySide6 import QtWidgets

from pysideprocessing.pwidget import PWidget, PSurface, PSignals
from pysideprocessing.pimage import PImage
from pysideprocessing.pgraphics import Graphics
from pysideprocessing.color import color

from makefun import wraps
from decopatch import function_decorator, DECORATED
from typing import Optional, Callable

PImage.PIXELS_DIMENSION = 2
 
sketch: PWidget = None # type:ignore[assignment]
signals: PSignals = None # type:ignore[assignment]
"""The sketch

Syntax
------
sketch.pixels

"""
window: PSurface = None # type:ignore[assignment]

def _run_sketch(ready_to_execute: threading.Event):
    global sketch, window, signals
    app = QtWidgets.QApplication(sys.argv)
    sketch = PWidget()
    signals = PSignals(sketch)
    
    ready_to_execute.wait() #Wait for execution event
    
    window = PSurface(sketch)  
    window.show()

    app.exec()
    ready_to_execute.clear()

_exec_event = threading.Event()
_gui_thread = threading.Thread(target=_run_sketch, args=(_exec_event,))
_gui_thread.start()

def setup():
    pass
def _run_setup(ready_to_execute: threading.Event):
    ready_to_execute.wait() #Wait for execution event
    setup()
    ready_to_execute.clear()

_setup_event = threading.Event()
_setup_wait_thread = threading.Thread(target=_run_setup, args=(_setup_event,))
_setup_wait_thread.start()

@function_decorator
def sketch_setup(run: bool = True, func:Callable[[PWidget],None]=DECORATED):
    """Decorator to make a function the setup function

    Use this only once. If used multiple times, the last call will take precendence
    """
    global setup

    if run: _exec_event.set()# run the sketch
    while sketch is None: # wait for gui_thread to load sketch
        pass
    while signals is None:
        pass
    setup = func
    _setup_event.set() 
    return func

class RepeatTimer(threading.Timer):
    def run(self):
        self.function(*self.args, **self.kwargs)
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

def draw():
    pass
def _run_draw(ready_to_execute: threading.Event):
    
    ready_to_execute.wait() #Wait for execution event
    #TODO: end Timer and all Threads when program is closed
    #TODO: write better custom timer class, without sleep? and skipping tasks options.
    #TODO: provide method to adjust timer frequence to reduce flickering
    timer = RepeatTimer(1/60,draw)
    timer.start()
    ready_to_execute.clear()

_draw_event = threading.Event()
_draw_wait_thread = threading.Thread(target=_run_draw, args=(_draw_event,))
_draw_wait_thread.start()

@function_decorator
def sketch_draw(run: bool = False, func:Callable[[PWidget],None]=DECORATED):
    """Decorator to make a function the draw loop

    Use this only once. If used multiple times, the last call will take precendence
    """
    global draw

    if run: _exec_event.set() # run the sketch
    while sketch is None: # wait for gui_thread to load sketch
        pass
    while signals is None:
        pass
    @wraps(func)
    def _impl(*_args, **_kwargs):
        signals.painter_begin.emit()
        func()
        signals.painter_end.emit()
    draw = _impl
    _draw_event.set() 
    return func
    
def width() -> int:
    return sketch.get_pixmap().width()

def height() -> int:
    return sketch.get_pixmap().height()
   
def set_size(width: int, height: int): # pylint: disable=redefined-outer-name
    sketch.set_size(width, height)

def load_pixels():
    """Läd die Pixel Daten des momentan angezeigten Bilds in die pixels[] Liste.
    """
    sketch.load_pixels()
    
def update_pixels():
    """Setzt das Bild neu auf Basis des Pixel-Arrays.

    Die Groesse des Bildes wird nicht automatisch an das Array angepasst.
    """
    sketch.update_pixels()
    
def push_image():
    """Speichert das aktuell angezeigte Bild in der history
    """
    sketch.push_image()

# def update_image():
#     sketch.update_image()

def undo():
    """Ruft das letzte abgespeicherte Bild aus der History wieder auf.
    """
    sketch.undo()
    
def redo():
    sketch.redo()
# 
# def get_image(self):     
#     return sketch.get_image()

def set_zoom(factor: float):
    sketch.set_zoom(factor)

# -- Functions to work on picture --
# --- Zeichnenfunktionen ---
# @wraps(Graphics.clear,remove_args="self")
def clear():
    signals.clear.emit()

# @wraps(Graphics.rect_mode,remove_args="self")
def rect_mode(mode: int):
    sketch.rect_mode(mode)

# @wraps(Graphics.ellipse_mode,remove_args="self")
def ellipse_mode(mode: int):
    sketch.ellipse_mode(mode)
#TODO def arc
#TODO def circle
#TODO make sure wraps works in autocomplete
# @wraps(PGraphics.ellipse.__doc__, func_name="ellipse")
@wraps(Graphics.ellipse,remove_args='self')
def ellipse(a: int, b: int, c: int, d: int):
    signals.ellipse.emit(a,b,c,d)
# ellipse.__doc__ = PGraphics.ellipse.__doc__

@wraps(Graphics.line,remove_args="self")
def line(x1:int, y1:int,x2:int,y2:int):
    signals.line.emit(x1,y1,x2,y2)

@wraps(Graphics.point,remove_args="self")
def point(x:int, y:int):
    signals.point.emit(x,y)
    
@wraps(Graphics.quad,remove_args="self")
def quad(x1:int, y1:int,x2:int,y2:int, x3:int, y3:int, x4:int, y4:int):
    signals.quad.emit(x1,y1,x2,y2,x3,y3,x4,y4)
    
# @wraps(Graphics.rectangle,remove_args="self")
def rectangle(a: int, b: int, c: int, d: int):
    signals.rectangle.emit(a,b,c,d)
#     sketch.rectangle(a,b,c,d)

@wraps(Graphics.square,remove_args="self")
def square(x:int, y:int, extend:int):
    signals.square.emit(x,y,extend)
    
@wraps(Graphics.triangle,remove_args="self")
def triangle(x1:int, y1:int,x2:int,y2:int, x3:int, y3:int):
    signals.triangle.emit(x1,y1,x2,y2,x3,y3)
   
# @wraps(Graphics.text,remove_args="self")
def text(s:str, x:int, y:int):
    signals.text.emit(s,x,y)

# --- Farbfestlegungen ---
def get(x: int, y: int) -> color:
    """Der Farbwert an der Position x,y de"""
    raise NotImplementedError()

# @wraps(Graphics.stroke,remove_args="self")
def stroke(pencolor: color):
    signals.stroke.emit(pencolor)

# @wraps(Graphics.no_stroke,remove_args="self")
def no_stroke():
    signals.no_stroke.emit()
    
@wraps(Graphics.stroke_weight,remove_args="self")
def stroke_weight(weight: int):
    signals.stroke_weight.emit(weight)

@wraps(Graphics.fill,remove_args="self")
def fill(fillcolor: color):
    signals.fill.emit(fillcolor)
    
@wraps(Graphics.no_fill,remove_args="self")
def no_fill():
    """Legt fest, dass die Formen nicht gefüllt werden sollen.
    """
    signals.no_fill.emit()
    
@wraps(Graphics.background,remove_args="self")
def background(backgroundcolor: color):
    signals.background.emit(backgroundcolor)

@wraps(Graphics.text_font,remove_args="self")
def text_font(font): #TODO font type?
    signals.text_font.emit(font)

@wraps(Graphics.text_size,remove_args="self")
def text_size(size: int):
    signals.text_size.emit(size)

# --- Dateioperationen ---
def image_mode():
    raise NotImplementedError

def create_image():
    raise NotImplementedError

# @wraps(PWidget.load_image)
def load_image(filename: str) -> PImage:
    return sketch.load_image(filename)

# @wraps(PWidget.image)
def image(image:PImage, x:int,y:int, width: int = -1, height: int = -1): # pylint: disable=redefined-outer-name
    sketch.image(image,x,y,width,height)

# @wraps(PWidget.save)
def save(filename: str, format: Optional[str]=None, quality:int=-1):
    sketch.save(filename, format, quality)
    
# --- Sonstiges ---

def delay(millis: int):
    """Hilfsfunktion zum Verzoegern der Ausgabe

    Parameters
    ----------
    millis : int
        Wartezeit in Millisekunden
    """
#     global count_time
#     init_time = time.perf_counter()
#     time_not_passed = True
#     while time_not_passed: # Init loop
#         if init_time + millis/1000 <= time.perf_counter():
#             time_not_passed = False
    time.sleep(millis/1000)