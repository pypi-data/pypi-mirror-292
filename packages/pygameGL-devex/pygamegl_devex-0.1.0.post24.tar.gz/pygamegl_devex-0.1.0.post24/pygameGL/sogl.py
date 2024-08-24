import ctypes
from ctypes import c_void_p, POINTER, c_ubyte, c_int, c_char_p, c_uint32

SOGL_DLL:str = __file__.removesuffix('sogl.py')+"ext\\SoGL\\sogl64.dll"
GLFW_DLL:str = __file__.removesuffix('sogl.py')+"ext\\GL\\glfw3.dll"
GLEW_DLL:str = __file__.removesuffix('sogl.py')+"ext\\GL\\glew32.dll"

""" configure SoGL structures """
class SGclock:
    _fields_ = [
        ("delta", ctypes.c_float),
        ("current", ctypes.c_float),
        ("previous", ctypes.c_float)
    ]


class SGmat4(ctypes.Structure):
    _fields_ = [
        ("m", ctypes.c_float * 16)
    ]

class SGvec2(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float)
    ]

class SGvec3(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float)
    ]

class SGvec4(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("w", ctypes.c_float)
    ]


class SGcontext(ctypes.Structure):
    class Info(ctypes.Structure):
        _fields_ = [
            ("support_stereo_rendering", ctypes.c_uint),
            ("max_draw_buffers", ctypes.c_uint),
            ("max_texture_size", ctypes.c_uint),
            ("max_viewport_dims", ctypes.c_uint),
            ("max_vertex_attribs", ctypes.c_uint),
            ("max_component_passes", ctypes.c_uint),
            ("max_fragment_textures", ctypes.c_uint),
            ("max_vertex_uniforms", ctypes.c_uint),
            ("max_cubemap_texture_size", ctypes.c_uint),
            ("max_vertex_textures", ctypes.c_uint),
            ("max_shader_textures", ctypes.c_uint),
            ("max_fragment_uniforms", ctypes.c_uint),
            ("version", ctypes.c_char * 1024),
            ("renderer", ctypes.POINTER(ctypes.c_ubyte))
        ]

    class state(ctypes.Structure):
        _fields_ = [
            ("running", ctypes.c_ubyte),
        ]

    class resources(ctypes.Structure):
        _fields_ = [
            ("title", ctypes.c_char_p),
            ("winsize", SGvec2),
            ("window", ctypes.c_void_p)
        ]
    
    _fields_ = [ ("info", Info), ("state", state), ("resources", resources), ("init", ctypes.c_ubyte) ]

def load_SoGL():
    lib = None
    if __import__('sys').platform == 'win32':
        lib = ctypes.CDLL(SOGL_DLL)

    # error loading SoGL library!
    if lib == None: return lib
    else:

        # configure SoGL functions
        lib.sgInit.restype=None
        lib.sgInit.argtypes=None

        lib.sgMakeClock.restype=SGclock
        lib.sgMakeClock.argtypes=None

        lib.sgMakeWindow.restype=ctypes.c_void_p
        lib.sgMakeWindow.argtypes=(ctypes.c_uint, ctypes.c_uint, ctypes.c_char_p)

    return lib

