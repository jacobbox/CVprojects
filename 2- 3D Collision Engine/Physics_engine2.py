import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from math import sin,cos,pi,atan,tan
from random import randint,random,choice
from os import listdir
from os.path import dirname
from time import time
print("dependancy: OpenGL , pygame\n python pip -m install @\n @:PyOpenGL , pygame")
class Player:

    display = (1920,1080)
    fps = 50
    fov = 78
    sensitivity = 1
    inverty = 0 # boolean ONLY
    gravity = 1
    jump_power_const = 0.03
    collision_distance = 2 # min size = height of charicter

    
    jump_power = jump_power_const * pow(100/fps,0.5)
    g_strength = (1/30)/fps

    _vfov = (360/pi)*atan(tan(pi*fov/360)*(display[1]/display[0]))
    _frame_value = (1/fps)*1000

    x = 0
    y = 0
    z = 0
    xo = 0
    yo = 0
    zo = 0
    speed = 0.04
    speed = speed * (100/fps)
    vy = 0
    
    on_ground = False
    ry = 0
    rx = 0

    cc = []
    cco = []
    
    def calc_cc():
        """calculate (update) collision coords"""
        h = 0.25 # distance from position of edge
        n = -1.7 # negitive distance
        p = 0.2 # pos distance
        x = player.x
        y = player.y
        z = player.z
        Player.cc = [(x-h,y+p,z-h),(x+h,y+p,z-h),(x-h,y+p,z+h),(x+h,y+p,z+h),(x-h,y+n,z-h),(x+h,y+n,z-h),(x-h,y+n,z+h),(x+h,y+n,z+h)]

    def calc_cco():
        """calculate (update) OLD collision coords"""
        h = 0.25 # distance from position of edge
        n = -1.7 # negitive distance
        p = 0.2 # pos distance
        x = player.xo
        y = player.yo
        z = player.zo
        Player.cco = [(x-h,y+p,z-h),(x+h,y+p,z-h),(x-h,y+p,z+h),(x+h,y+p,z+h),(x-h,y-p,z-h),(x+h,y-p,z-h),(x-h,y-p,z+h),(x+h,y-p,z+h)]

class texture:
    '''Texture class \n file should be either apsolote or, from current, form\n e.g. file=image/test_image.png'''
    _textures = {}

    def __init__(self,name,file):
        textureSurface = pygame.image.load(file)
        textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
        width = textureSurface.get_width()
        height = textureSurface.get_height()

        
        texid = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, texid)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        #glDisable(GL_TEXTURE_2D)
        texture._textures[name] = texid

    def load_to_draw(name):
        '''usage:  (while inside glBegin-->glEnd)\n|    glEnd()\n|--> texture.load_to_draw("normal")\n|    glBegin(GL_QUADS)'''
        glBindTexture(GL_TEXTURE_2D,texture._textures[name])



class solid_object:
    """This will be sub-classed"""
    
    obs = []

    def natral_init(self):
        solid_object.obs.append(self)

    def collision(self):
        pass#placeholder to prevent crashing



named = {}
_images = {}
def load_image_loction():
    """Get all images in the images sub-folder"""
    global named,_images
    for i in listdir(dirname(__file__)+"/images"):
        _images["images/"+str(i)] = str(i)
    _images.update(named)#allows image renaming

load_image_loction()
    
def reload_tex():
    """Creates the textures from known images"""
    global _images
    for img in list(_images.keys())[:]:
        texture(_images[img],img)

def pos(x):
    '''returns: |x|'''
    if x < 0:
        return -x
    return x
    


class collidable_object():

    dither_value = Player.g_strength
    objects = []
    point_variance = 0.0001
    obyref = {}

    def __init__(self,ref,x,y,z,coly,colxz_wid,collision_distance,faces=None,vol=(0,0,0),acc=(0,-Player.g_strength,0),coord_mylt=1,auto_scaling=None,coords=None,point=False,lines=True,friction=0.95):
        collidable_object.objects.append(self)
        collidable_object.obyref[ref] = self
        self.ref = ref
        self.collision_distance = collision_distance
        self.x = x
        self.y = y
        self.z = z
        self.xo = x
        self.yo = y
        self.zo = z
        self.vx = vol[0]
        self.vy = vol[1]
        self.vz = vol[2]
        self.acc = acc
        self.friction = friction
        self.lines = lines
        self._coly = coly
        self._colxz_wid = colxz_wid
        self.on_ground = False
        self.cc = []#concider imminet running to prevent errors
        self.cco = []
        self.point = point#point is an image
        self.faces = faces
        if not (self.faces == None or len(self.faces) == 6):
            for f in ["top","bottom","left","right","back","front"]:
                try:
                    temp = self.faces[f] # the face exists
                except:
                    self.faces[f] = None # the face is set to None

                    
        if auto_scaling != None:#there is auto_scaling
            dx = self.x2-self.x1
            dy = self.y2-self.y1
            dz = self.z2-self.z1
            fbys = float(dy / min(dy,dx)) * auto_scaling["fb"]
            fbxs = float(dx / min(dy,dx)) * auto_scaling["fb"]
            lrys = float(dy / min(dy,dz)) * auto_scaling["lr"]
            lrzs = float(dz / min(dy,dz)) * auto_scaling["lr"]
            tbzs = float(dz / min(dz,dx)) * auto_scaling["tb"]
            tbxs = float(dx / min(dz,dx)) * auto_scaling["tb"]

            self.coords = {"front":((fbxs,0.0),(fbxs,fbys),(0.0,fbys),(0.0,0.0)),"back":((fbxs,0.0),(fbxs,fbys),(0.0,fbys),(0.0,0.0)),"left":((lrzs,0.0),(lrzs,lrys),(0.0,lrys),(0.0,0.0)),"right":((lrzs,0.0),(lrzs,lrys),(0.0,lrys),(0.0,0.0)),"top":((tbxs,0.0),(tbxs,tbzs),(0.0,tbzs),(0.0,0.0)),"bottom":((tbxs,0.0),(tbxs,tbzs),(0.0,tbzs),(0.0,0.0))}

            
        else: # there is no auto_scaling
            self.coords = {"front":((1.0,0.0),(1.0,1.0),(0.0,1.0),(0.0,0.0)),"back":((1.0,0.0),(1.0,1.0),(0.0,1.0),(0.0,0.0)),"left":((1.0,0.0),(1.0,1.0),(0.0,1.0),(0.0,0.0)),"right":((1.0,0.0),(1.0,1.0),(0.0,1.0),(0.0,0.0)),"top":((1.0,0.0),(1.0,1.0),(0.0,1.0),(0.0,0.0)),"bottom":((1.0,0.0),(1.0,1.0),(0.0,1.0),(0.0,0.0))}
        if coords != None: # there are unique coord requirments for the image's location
            self.coords.update(coords)
        if coord_mylt != 1:
            new = {}
            for face in list(self.coords.keys())[:]:
                new[face] = []
                for coord in self.coords[face]:
                    new[face].append((coord[0]*coord_mylt,coord[1]*coord_mylt))
                new[face] = tuple(new[face])
            self.coords = new

    def calc_cc(self):
        """calculate (update) collision coords"""
        w = self._colxz_wid
        h = self._coly
        x = self.x
        y = self.y
        z = self.z
        self.cc = [(x-w,y+h,z-w),(x+w,y+h,z-w),(x-w,y+h,z+w),(x+w,y+h,z+w),(x-w,y,z-w),(x+w,y,z-w),(x-w,y,z+w),(x+w,y,z+w)]

    def calc_cco(self):
        """calculate (update) OLD collision coords"""
        w = self._colxz_wid
        h = self._coly
        x = self.xo
        y = self.yo
        z = self.zo
        self.cco = [(x-w,y+h,z-w),(x+w,y+h,z-w),(x-w,y+h,z+w),(x+w,y+h,z+w),(x-w,y,z-w),(x+w,y,z-w),(x-w,y,z+w),(x+w,y,z+w)]

    def render(self):

        x1 = (self.x-self._colxz_wid) - player.x
        y1 = self.y - player.y
        z1 = (self.z-self._colxz_wid) - player.z
        x2 = (self.x+self._colxz_wid) - player.x
        y2 = (self.y+self._coly) - player.y
        z2 = (self.z+self._colxz_wid) - player.z

        vert = ((x1,y1,z1),(x1,y2,z1),(x2,y2,z1),(x2,y1,z1),   (x1,y1,z2),(x1,y2,z2),(x2,y2,z2),(x2,y1,z2))
        if self.point == False:
            if self.faces != None:#there are some faces
                x = -1
                for face in cuboid.surfaces:
                    x = -1
                    if self.faces[cuboid.faceord[x]] != None: # there is a face for this side
                        dat = self.faces[cuboid.faceord[x]] # dat = the face data
                        if type(dat) == tuple or type(dat) == list:#coloured face
                            glBegin(GL_QUADS)
                            for point in face:
                                glColor3fv(dat)
                                glVertex3fv(vert[point])
                            glEnd()
                        else:#type == string    ###image face
                            glEnable(GL_TEXTURE_2D)
                            texture.load_to_draw(dat)
                            coords = self.coords[cuboid.faceord[x]]#my coords relivent for this face
                            glBegin(GL_QUADS)
                            tc = 0
                            for point in face:
                                glTexCoord2f(*coords[tc])
                                glVertex3fv(vert[point])
                                tc += 1
                            glEnd()
                            glDisable(GL_TEXTURE_2D)
        else:

            ipoints = ((x1,(self._coly/2)+self.y-player.y,z1),(x1,(self._coly/2)+self.y-player.y,z2),(x2,(self._coly/2)+self.y-player.y,z2),(x2,(self._coly/2)+self.y-player.y,z1),    (self.x- player.x,y1,z1),(self.x- player.x,y2,z1),(self.x- player.x,y2,z2),(self.x- player.x,y1,z2),    (x1,y1,self.z- player.z),(x2,y1,self.z- player.z),(x2,y2,self.z- player.z),(x1,y2,self.z- player.z))
            face_definition = (
                (0,1,2,3),
                (3,2,1,0),
                (4,5,6,7),
                (7,6,5,4),
                (8,9,10,11),
                (11,10,9,8)
                )
            ##face_definition = (
            ##    (0,1,2,3),
            ##    (4,5,6,7),
            ##    )
            
            faceord = ("top","bottom","right","left","front","back")
            x = -1
            for face in face_definition:
                x += 1
                if type(self.point) == tuple or type(self.point) == list:
                    glBegin(GL_QUADS)
                    for point in face:
                        glColor3fv((0.2,0.2,0.9))
                        glVertex3fv(ipoints[point])
                    glEnd()
                else:
                    
                    glEnable(GL_BLEND)
                    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                    glEnable(GL_TEXTURE_2D)
                    texture.load_to_draw(self.point)
                    coords = self.coords[faceord[x]]#my coords relivent for this face
                    glBegin(GL_QUADS)
                    tc = 0
                    for point in face:
                        glTexCoord2f(*coords[tc])
                        glVertex3fv(ipoints[point])
                        tc += 1
                    glEnd()
                    glDisable(GL_TEXTURE_2D)
                    glDisable(GL_BLEND)
                    
        if self.lines:
            glBegin(GL_LINES)
            glColor3fv((0,0.65,0.87))
            for edge in cuboid.edges:
                for point in edge:
                    glVertex3fv(vert[point])
            glEnd()

    def destroy(self):
        collidable_object.objects.remove(self)
        del collidable_object.obyref[self.ref]

    def __del__(self):
        #print(self.ref+" died!")
        pass
        

class cuboid(solid_object):

    edges = (
    (0,1),
    (1,2),
    (2,3),
    (3,0),
    (0,4),
    (1,5),
    (2,6),
    (3,7),
    (4,5),
    (5,6),
    (6,7),
    (7,4)
    )

    surfaces = (
    (0,1,2,3),#back
    (7,6,5,4),#frount
    (4,5,1,0),#left
    (3,2,6,7),#right
    (6,2,1,5),#top
    (3,7,4,0),#bottom
    )
    faceord = ("back","front","left","right","top","bottom")

    def __init__(self,x1,y1,z1,x2,y2,z2,faces=None,coords=None,auto_scaling=None,coord_mylt=1,lines=True):
        '''faces takes form: {"side":|(r,g,b)|or|"tex name"|}\n autoscaling is a scaling factor for repeating textured face sides'''
        self.natral_init()
        self.x1 = min(x1,x2)
        self.y1 = min(y1,y2)
        self.z1 = min(z1,z2)
        self.x2 = max(x1,x2)
        self.y2 = max(y1,y2)
        self.z2 = max(z1,z2)
        self.lines = lines
        self.faces = faces
        if type(self.faces) == dict:
            if not (self.faces == None or len(self.faces) == 6):
                for f in ["top","bottom","left","right","back","front"]:
                    try:
                        temp = self.faces[f] # the face exists
                    except:
                        self.faces[f] = None # the face is set to None
        elif type(self.faces) == str:
            new_faces = {}
            for f in ["top","bottom","left","right","back","front"]:
                 new_faces[f] = self.faces # the face exists
            self.faces = new_faces
        else:
            raise TypeError("faces must be a string or a dictionary")
            

                    
        if auto_scaling != None:#there is auto_scaling
            dx = self.x2-self.x1
            dy = self.y2-self.y1
            dz = self.z2-self.z1
            fbys = float(dy / min(dy,dx)) * auto_scaling["fb"]
            fbxs = float(dx / min(dy,dx)) * auto_scaling["fb"]
            lrys = float(dy / min(dy,dz)) * auto_scaling["lr"]
            lrzs = float(dz / min(dy,dz)) * auto_scaling["lr"]
            tbzs = float(dz / min(dz,dx)) * auto_scaling["tb"]
            tbxs = float(dx / min(dz,dx)) * auto_scaling["tb"]

            self.coords = {"front":((fbxs,0.0),(fbxs,fbys),(0.0,fbys),(0.0,0.0)),"back":((fbxs,0.0),(fbxs,fbys),(0.0,fbys),(0.0,0.0)),"left":((lrzs,0.0),(lrzs,lrys),(0.0,lrys),(0.0,0.0)),"right":((lrzs,0.0),(lrzs,lrys),(0.0,lrys),(0.0,0.0)),"top":((tbxs,0.0),(tbxs,tbzs),(0.0,tbzs),(0.0,0.0)),"bottom":((tbxs,0.0),(tbxs,tbzs),(0.0,tbzs),(0.0,0.0))}

            
        else: # there is no auto_scaling
            self.coords = {"front":((1.0,0.0),(1.0,1.0),(0.0,1.0),(0.0,0.0)),"back":((1.0,0.0),(1.0,1.0),(0.0,1.0),(0.0,0.0)),"left":((1.0,0.0),(1.0,1.0),(0.0,1.0),(0.0,0.0)),"right":((1.0,0.0),(1.0,1.0),(0.0,1.0),(0.0,0.0)),"top":((1.0,0.0),(1.0,1.0),(0.0,1.0),(0.0,0.0)),"bottom":((1.0,0.0),(1.0,1.0),(0.0,1.0),(0.0,0.0))}
        if coords != None: # there are unique coord requirments for the image's location
            self.coords.update(coords)
        if coord_mylt != 1:
            new = {}
            for face in list(self.coords.keys())[:]:
                new[face] = []
                for coord in self.coords[face]:
                    new[face].append((coord[0]*coord_mylt,coord[1]*coord_mylt))
                new[face] = tuple(new[face])
            self.coords = new
                        
        
            
                


    def render(self):
        x1 = self.x1 - player.x
        y1 = self.y1 - player.y
        z1 = self.z1 - player.z
        x2 = self.x2 - player.x
        y2 = self.y2 - player.y
        z2 = self.z2 - player.z
        
        vert = ((x1,y1,z1),(x1,y2,z1),(x2,y2,z1),(x2,y1,z1),   (x1,y1,z2),(x1,y2,z2),(x2,y2,z2),(x2,y1,z2))

        if self.faces != None:#there are some faces
            x = -1
            for face in cuboid.surfaces:
                x += 1
                if self.faces[cuboid.faceord[x]] != None: # there is a face for this side
                    dat = self.faces[cuboid.faceord[x]] # dat = the face data
                    if type(dat) == tuple or type(dat) == list:#coloured face
                        glBegin(GL_QUADS)
                        for point in face:
                            glColor3fv(dat)
                            glVertex3fv(vert[point])
                        glEnd()
                    else:#type == string    ###image face
                        glEnable(GL_TEXTURE_2D)
                        texture.load_to_draw(dat)
                        coords = self.coords[cuboid.faceord[x]]#my coords relivent for this face
                        glBegin(GL_QUADS)
                        tc = 0
                        for point in face:
                            glTexCoord2f(*coords[tc])
                            glVertex3fv(vert[point])
                            tc += 1
                        glEnd()
                        glDisable(GL_TEXTURE_2D)
        if self.lines:
            glBegin(GL_LINES)
            glColor3fv((1,1,1))
            for edge in cuboid.edges:
                for point in edge:
                    glVertex3fv(vert[point])
            glEnd()

                

    def player_collision(self):
        cd = player.collision_distance
        if not (min(self.x1,self.x2) - cd < player.x and
                max(self.x1,self.x2) + cd > player.x and
                min(self.y1,self.y2) - cd < player.y and
                max(self.y1,self.y2) + cd > player.y and
                min(self.z1,self.z2) - cd < player.z and
                max(self.z1,self.z2) + cd > player.z
                ):
            return None
        #if reached here then is 'collidable' (i.e. close enogth to collide)
        #print("collidable")
        for n in range(0,len(Player.cc)):
            p = Player.cc[n]
            if self.point_is_in_me(p):
                #print("point inside")
                Player.calc_cco()
                op = Player.cco
                larx = max(self.x1,self.x2)
                smlx = min(self.x1,self.x2)
                lary = max(self.y1,self.y2)
                smly = min(self.y1,self.y2)
                larz = max(self.z1,self.z2)
                smlz = min(self.z1,self.z2)
                if op[n][0] < smlx and p[0] > smlx: #passed throug smallx-->bigx
                    player.x = smlx-(p[0]-player.x)
                    player.x -= player.g_strength
                    Player.calc_cc()
                elif op[n][0] > larx and p[0] < larx: #passed throug bigx-->smallx
                    player.x = larx+(player.x-p[0])
                    player.x += player.g_strength
                    Player.calc_cc()
                if op[n][1] > lary and p[1] < lary: #passed throug top
                    player.y = lary+(player.y-p[1])
                    player.vy = player.g_strength
                    Player.calc_cc()
                    player.on_ground = True
                elif op[n][1] < smly and p[1] > smly: #passed throug bottom
                    player.y = smly-(p[1]-player.y)
                    player.vy = -player.g_strength
                    Player.calc_cc()
                if op[n][2] < smlz and p[2] > smlz: #passed throug smallz-->bigz
                    player.z = smlz-(p[2]-player.z)
                    player.z -= player.g_strength
                    Player.calc_cc()
                elif op[n][2] > larz and p[2] < larz: #passed throug bigz-->smallz
                    player.z = larz+(player.z-p[2])
                    player.z += player.g_strength
                    Player.calc_cc()

    def other_collision(self):
        collidable = []
        for entity in collidable_object.objects:
            cd = entity.collision_distance
            if not (min(self.x1,self.x2) - cd < entity.x and
                max(self.x1,self.x2) + cd > entity.x and
                min(self.y1,self.y2) - cd < entity.y and
                max(self.y1,self.y2) + cd > entity.y and
                min(self.z1,self.z2) - cd < entity.z and
                max(self.z1,self.z2) + cd > entity.z
                ):
                pass
            else:
                collidable.append(entity)
        #collidable (close enoght to collide)
        if collidable == []:
            return None

        for entity in collidable:
            for n in range(0,len(entity.cc)):
                p = entity.cc[n]
                if self.point_is_in_me(p):
                    entity.calc_cco()
                    oc = entity.cco
                    larx = max(self.x1,self.x2)
                    smlx = min(self.x1,self.x2)
                    lary = max(self.y1,self.y2)
                    smly = min(self.y1,self.y2)
                    larz = max(self.z1,self.z2)
                    smlz = min(self.z1,self.z2)
                    if oc[n][0] < smlx and p[0] > smlx: #passed throug smallx-->bigx
                        entity.x = smlx-(p[0]-entity.x)
                        entity.x -= collidable_object.dither_value
                        entity.vx = 0
                        entity.calc_cc()
                    elif oc[n][0] > larx and p[0] < larx: #passed throug bigx-->smallx
                        entity.x = larx+(entity.x-p[0])
                        entity.x += collidable_object.dither_value
                        entity.vx = 0
                        entity.calc_cc()
                    if oc[n][1] > lary and p[1] < lary: #passed throug top
                        entity.y = lary+(entity.y-p[1])
                        entity.vy = pos(entity.acc[1])*1.001   #*1.001 ensures favorable rounding
                        entity.calc_cc()
                        entity.on_ground = True
                    elif oc[n][1] < smly and p[1] > smly: #passed throug bottom
                        entity.y = smly-(p[1]-entity.y)
                        entity.vy = 0
                        entity.calc_cc()
                    if oc[n][2] < smlz and p[2] > smlz: #passed throug smallz-->bigz
                        entity.z = smlz-(p[2]-entity.z)
                        entity.z -= collidable_object.dither_value
                        entity.vz = 0
                        entity.calc_cc()
                    elif oc[n][2] > larz and p[2] < larz: #passed throug bigz-->smallz
                        entity.z = larz+(entity.z-p[2])
                        entity.z += collidable_object.dither_value
                        entity.vz = 0
                        entity.calc_cc()
        
            

    def point_is_in_me(self,point):
        if (min(self.x1,self.x2) < point[0] and
            max(self.x1,self.x2) > point[0] and
            min(self.y1,self.y2) < point[1] and
            max(self.y1,self.y2) > point[1] and
            min(self.z1,self.z2) < point[2] and
            max(self.z1,self.z2) > point[2]
            ):
            return True
        return False

def tick(events):#placeholder command to allow applictions of the moduel to add there own tick logic
    pass

def Start():
    pygame.init()
    display = player.display
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL|pygame.FULLSCREEN)
    _fullscreen = True
    _setPos = True
    _setposloc = (int(display[0]/2),int(display[1]/2))

    gluPerspective(player.fov, (display[0]/display[1]), 0.1, 50.0)
    glEnable(GL_DEPTH_TEST)#required for face culling
    glEnable(GL_CULL_FACE)#deos face culling
    glAlphaFunc(GL_GREATER,0.25)#sets-up transparency
    glEnable(GL_ALPHA_TEST)#sets-up transparency
    reload_tex()
    
    player.x += 0
    player.y += 3
    player.z += 0

    while True:
        start = time()
        _ev = pygame.event.get()
        for event in _ev:
            if event.type == pygame.QUIT:
                pygame.quit()
                _setPos = False
            if event.type == pygame.MOUSEMOTION:
                if _setPos:
                    mousepos = pygame.mouse.get_pos()
                    dx = mousepos[0]-_setposloc[0] # greater than 0 ==> right side
                    dy = 0-mousepos[1]+_setposloc[1] # greater than 0 ==> up side
                    xdeg = player.fov*(dx/_setposloc[0])
                    ydeg = player.fov*(dy/_setposloc[0])*((player.inverty*2)-1)
                    glRotate(xdeg*player.sensitivity,0,1,0)
                    player.ry += xdeg*player.sensitivity
                    glRotate(ydeg,cos(player.ry*pi/180),0,sin(player.ry*pi/180))
                    player.rx += ydeg
                    pygame.mouse.set_pos(*_setposloc)
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if _fullscreen:
                        pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
                        gluPerspective(player.fov, (display[0]/display[1]), 0.1, 50.0)
                        glEnable(GL_DEPTH_TEST)
                        glEnable(GL_CULL_FACE)
                        glAlphaFunc(GL_GREATER,0.25)
                        glEnable(GL_ALPHA_TEST)
                        reload_tex()
                        glRotate(player.ry,0,1,0)
                        glRotate(player.rx,cos(player.ry*pi/180),0,sin(player.ry*pi/180))
                        _fullscreen = False
                        _setPos = False
                    else:
                        pygame.display.set_mode(display, DOUBLEBUF|OPENGL|pygame.FULLSCREEN)
                        gluPerspective(player.fov, (display[0]/display[1]), 0.1, 50.0)
                        glEnable(GL_DEPTH_TEST)
                        glEnable(GL_CULL_FACE)
                        glAlphaFunc(GL_GREATER,0.25)
                        glEnable(GL_ALPHA_TEST)
                        reload_tex()
                        glRotate(player.ry,0,1,0)
                        glRotate(player.rx,cos(player.ry*pi/180),0,sin(player.ry*pi/180))
                        _fullscreen = True
                        _setPos = True
                #if event.key == pygame.K_r:######################################################################
                #    player.y = 10
                #if event.key == pygame.K_o:######################################################################
                #    collidable_object("fireball"+str(len(collidable_object.objects)),0,4,0,0.2,0.1,1,point="fireball.png",lines=False)



            

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.z -= player.speed * cos(player.ry*pi/180)
            player.x += player.speed * sin(player.ry*pi/180)
        if keys[pygame.K_s]:
            player.z += player.speed * cos(player.ry*pi/180)
            player.x -= player.speed * sin(player.ry*pi/180)
        if keys[pygame.K_a]:
            player.z -= player.speed * sin(player.ry*pi/180)
            player.x -= player.speed * cos(player.ry*pi/180)
        if keys[pygame.K_d]:
            player.z += player.speed * sin(player.ry*pi/180)
            player.x += player.speed * cos(player.ry*pi/180)
        if keys[pygame.K_SPACE] and player.gravity == 0:
            player.y += player.speed
        if keys[pygame.K_LSHIFT] and player.gravity == 0:
            player.y -= player.speed
        if keys[pygame.K_SPACE] and player.gravity == 1 and player.on_ground:
            player.vy = player.jump_power



        tick((keys,_ev))



        
        #player motion logic
        if player.gravity == 1:#should be 1 ------------------------
            player.vy = max(-0.2,player.vy-player.g_strength)
        player.y += player.vy
        #player motion logic end
        #player collision
        player.on_ground = False
        Player.calc_cc()

        for o in solid_object.obs: #commences collision checking for all objects
            o.player_collision()

        
        #player collision end
        player.xo = player.x
        player.yo = player.y
        player.zo = player.z
        #entity motion logic
        for obj in collidable_object.objects:
            #motion before acceleration prevents phazing
            obj.x += obj.vx
            obj.y += obj.vy
            obj.z += obj.vz
            obj.vx += obj.acc[0]
            obj.vy += obj.acc[1]
            obj.vz += obj.acc[2]
            if obj.on_ground:
                obj.vx *= obj.friction
                obj.vz *= obj.friction
            if obj.vx < 0.0001 and obj.vx > -0.0001:
                obj.vx = 0
            if obj.vz < 0.0001 and obj.vz > -0.0001:
                obj.vz = 0
        #entity motion logic end
                
        #entity collision
        for obj in collidable_object.objects: #sets collision variables
            obj.on_ground = False
            obj.calc_cc()

        for o in solid_object.obs: #commences collision checking for all objects
            o.other_collision()
        #entity collision end
            
        # coord updatinator
        for obj in collidable_object.objects:
            obj.xo = obj.x
            obj.yo = obj.y
            obj.zo = obj.z
        # coord updatinator end
        
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        #rendering
        for o in solid_object.obs:
            o.render()
            
        for o in collidable_object.objects:
            o.render()
            
        glColor3fv((1,1,1))
        #rendering end
        
        end = time()
        exetim = end-start
        #print(exetim)
        exetim *= 1000
        pygame.display.flip()
        if Player._frame_value-exetim > 0:#keeps framerate smooth upto when the loop takes longer than 1 frame to complete
            pygame.time.wait(round(Player._frame_value-exetim))
        

player = Player()
#####

print("loaded pysics_engine, abalible commands:\n    cuboid()#makes environmental elements\n    collidable_object()#makes entitys\n    tick(events)#runs " + str(Player.fps) +" times a second")


#cuboid(-20,0,-20,20,1,20,{"top":"metal_plating.png"},coord_mylt = 10)


#Start()

