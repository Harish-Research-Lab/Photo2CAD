class node:
    t = 0 #Translation has happened or not
    ro = 0 #Rotation has happened or not
    #Translation values
    tx=0
    ty=0
    tz=0
    #Rotation values
    rx=0
    ry=0
    rz=0
    def __init__(self, shape = 'set', operation = 'None',\
    l = 0, b = 0, h = 0,\
    fn = 12, fa = 12, fs = 2, r = 0, r1 = 0,\
    center = "true"):
        self.left = 'None'
        self.right = 'None'
        self.string = ''
        self.operation = operation
        self.shape = shape
        self.l = l
        self.b = b
        self.h = h
        self.fn = fn
        self.fa = fa
        self.fs = fs
        self.r = r  #Radius
        self.r1 = r1
        self.center = center

    def translate(self, x = 0, y = 0, z = 0):
        self.tx = x
        self.ty = y
        self.tz = z
        self.t = 1
    def rotate(self, x = 0, y = 0, z = 0):
        self.rx = x
        self.ry = y
        self.rz = z
        self.ro = 1

    def name(self):
        if(self.t == 1):
            self.string = 'translate([' + str(self.tx) + ',' + str(self.ty) + ',' + str(self.tz) + ']){\n\t'
        if(self.ro == 1):
            if(self.t == 1):
                self.string = self.string + 'rotate(['+ str(self.rx) + ',' + str(self.ry) + ',' + str(self.rz) + ']){\n\t\t'
            else:
                self.string = self.string + 'rotate(['+ str(self.rx) + ',' + str(self.ry) + ',' + str(self.rz) + ']){\n\t'
        if(self.shape == "cube"):
            self.string = self.string + 'cube(['+ str(self.l) + ',' + str(self.b) + ',' + str(self.h) + '], center = ' + self.center + ');\n'
        if(self.shape == "cylinder"):
            self.string = self.string + 'cylinder($fn = ' + str(self.fn) + ', h = ' + str(self.h) + ', r1 = ' + str(self.r) + \
            ', r2 = ' + str(self.r1) + ', center = ' + self.center + ');\n'
        if(self.shape == "sphere"):
            self.string = self.string + 'sphere($fn = ' + str(self.fn) + ', $fa = ' + str(self.fa) + ', $fs = '+ str(self.fs) + \
            'r = ' + str(self.r) + ');\n'
        if(self.ro == 1 and self.t == 1):
            self.string = self.string + "\t}\n"
        if(self.ro == 1 or self.t == 1):
            self.string = self.string + "}\n"

    def setr(self,r):
        self.r = r
    def setl(self,l):
        self.l = l
    def setb(self,b):
        self.b = b
    def seth(self,h):
        self.h = h
    def setr1(self,r):
        self.r1 = r
    def setoperation(self,operation):
        self.operation = operation
