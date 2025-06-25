from ctypes import windll, Structure, c_long, c_int, byref

class POINT(Structure):
    _fields_ = [("x", c_int),
                ("y", c_int)]

class RECT(Structure):
    _fields_ = [("upperleft", POINT),
                ("lowerright", POINT)]
    def x0(self):
        return self.upperleft.x 
    def y0(self):
        return self.upperleft.y
    def x1(self):
        return self.lowerright.x 
    def y1(self):
        return self.lowerright.y
    def w(self):
        return self.x1() - self.x0()
    def h(self):
        return self.y1() - self.y0()
    
def h_res_check(h_res): 
    if h_res >= 0:
        return 0
    else:
        print("HRESULT failed: %d" % h_res)
        return h_res
    

def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return pt

def wait_for_mouseposition():
    pt = POINT()
    state_left = windll.user32.GetKeyState(hex(0x01))
    while not (state_left == -127 or state_left == -128):
        pt = windll.user32.user32.GetCursorPos()

    return pt