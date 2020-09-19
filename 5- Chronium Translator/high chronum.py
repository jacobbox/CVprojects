from tkinter import *
from math import floor,sin,cos

alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
bit_bases = [2,17,27,81,390625,20,27,27,27,27]
bit_divs = [1, 17, 459, 37179, 14523046875, 290460937500, 7842445312500, 211746023437500, 5717142632812500]

def word_to_number(word):
    '''word must be only alphabet'''
    letters = list(word)
    letters.reverse()
    number = 0
    itteration = 0
    for letter in letters:
        number += (alphabet.index(letter)+1)*(27**itteration)
        itteration += 1
    return number

def class_interval(number,_min,_max):
    return ((number >= _min) and (number <= _max))

def product(number_list):
    ans = 1
    for number in number_list:
        ans *= number
    return ans

def base(number,base):
    val = 1
    itteration = -1
    while number >= val:
        val *= base
        itteration += 1
    ans = []
    while itteration >= 0:
        value = number/(base**itteration)
        if value >= 1:
            last_num = floor(value)
            ans.append(last_num)
            number -= last_num*(base**itteration)
        else:
            ans.append(0)
        itteration -= 1
    return ans

def pad_list(to_pad,length,what=0):
    padding = []
    while len(to_pad) + len(padding) < length:
        padding.append(what)
    return (padding + to_pad)

def polar(x,y,distance,angle):
    return (   x+(distance*sin(angle/57.2958))   ,   y+(distance*cos(angle/57.2958))   )

def rec_remove(old,what):
    old = old[:]
    for i in what:
        try:
            old.remove(i)
        except:
            pass
    return old

def number_to_word(number):
    if number >= 27**12:
        print('number to big')
        return None
    itteration = 12
    word = ''
    while itteration >= 0:
        value = number/(27**itteration)
        if class_interval(value,1,27):
            last_letter_num = floor(value)
            word += alphabet[last_letter_num-1]
            number -= last_letter_num*(27**itteration)
        itteration -= 1
    return word



def number_to_high_tuple(number):
    usable_base = bit_bases[1:]
    itteration = 8
    high_list = []
    while itteration >= 0:
        value = number/bit_divs[itteration]
        if value >= 1:
            last_letter_num = floor(value)
            high_list.append(last_letter_num)
            number -= last_letter_num*bit_divs[itteration]
        else:
            high_list.append(0)
        itteration -= 1
    high_list.append(1)
    return tuple(high_list)
    
def high_tuple_to_number(high_tuple):
    high_list = list(high_tuple)[:-1]
    high_list.reverse()
    number = 0
    itteration = 0
    for value in high_list:
        number += value*bit_divs[itteration]
        itteration += 1
    return number





def circle(canvas,x,y,rad,tag,*opt,**kwargs):
    canvas.create_oval(x-rad,y-rad,x+rad,y+rad,tags=tag,*opt,**kwargs)

class node:

    inner_radius = 3
    outer_radius = 6

    def __init__(self,canvas,x,y,ver,tag):
        if ver == 0:
            return None
        elif ver == 1:
            circle(canvas,x,y,node.inner_radius,tag)
        elif ver == 2:
            circle(canvas,x,y,node.inner_radius,tag,fill="#000000")
        elif ver == 3:
            circle(canvas,x,y,node.inner_radius,tag)
            circle(canvas,x,y,node.outer_radius,tag)
        elif ver == 4:
            circle(canvas,x,y,node.inner_radius,tag,fill="#000000")
            circle(canvas,x,y,node.outer_radius,tag)

class pod:

    inner_radius = 3
    outer_radius = 9

    def __init__(self,canvas,x,y,con_angle,ver,tag):#center,most,least
        circle(canvas,x,y,pod.outer_radius,tag)
        canvas.create_line(*polar(x,y,pod.outer_radius,con_angle-90),*polar(x,y,pod.outer_radius,con_angle+90),tags=tag)
        if ver[0] == 1:
            circle(canvas,x,y,pod.inner_radius,tag)
        elif ver[0] == 2:
            circle(canvas,x,y,pod.inner_radius,tag,fill='black')
        node(canvas,*polar(x,y,pod.outer_radius,con_angle+60),ver[1],tag)
        node(canvas,*polar(x,y,pod.outer_radius,con_angle-60),ver[2],tag)
        






class high_glyph:

    def set_data_from_word(self,word):
        self.set_data_from_high_tuple(number_to_high_tuple(word_to_number(word)))

    def set_data_from_number(self,number):
        self.set_data_from_high_tuple(number_to_high_tuple(number))

    known_glyphs = 0
    center_size = 4
    second_radi = 10
    third_radi = 17
    forth_radi = 25
    fifth_radi = 35

    def __init__(self,canvas,startx,starty,sentance=None,data=None):
        self.canvas = canvas
        self.sentance = sentance
        self.startx = startx
        self.starty = starty
        high_glyph.known_glyphs += 1
        self.tag = "high_glyph"+str(high_glyph.known_glyphs)
        self.data = ()
        self.high_tuple = ()
        self.size = 0
        if type(data) == tuple:
            self.set_data_from_high_tuple(data)
        elif type(data) == str:
            self.set_data_from_word(data)
        elif type(data) == int:
            self.set_data_from_number(data)
        if sentance == None:
            self.update_display()
        
    
    
    def set_data_from_high_tuple(self,high_tuple):
        self.data = [high_tuple[-1]]#center form
        self.high_tuple = tuple(high_tuple)
        self.number = high_tuple_to_number(self.high_tuple)
        self.meaning = number_to_word(self.number)
        nbyt = []
        tpv = high_tuple[-2]
        if high_tuple[-2] >= 9:#rotation 0-verticle 1-horizontal
            nbyt.append(1)
            tpv -= 9
        else:
            nbyt.append(0)
        nbyt.append(floor(tpv/3))#bottom (left)
        nbyt.append(tpv-(floor(tpv/3)*3))#top (right)
        self.data.append(tuple(nbyt))
        self.data.append(tuple(   pad_list(base(high_tuple[-3],3),3)   ))#left, right, top
        self.data.append(tuple(   pad_list(base(high_tuple[-4],3),4)   ))#NW,SW,SE,NE
        self.data.append(tuple(   pad_list(base(high_tuple[-5],5),8)   ))#NW,W,SW,S,SE,E,NE,N
        nbyt = []
        tpv = high_tuple[-6]
        if high_tuple[-6] >= 10:#inner conections 2-3: number
            nbyt.append(1)
            tpv -= 10
        else:
            nbyt.append(0)
        if tpv >= 5:#inner conections 3-4: number
            nbyt.append(1)
            tpv -= 5
        else:
            nbyt.append(0)
        nbyt.append(tpv)#inner conections 4-5: number
        self.data.append(tuple(nbyt))
        self.data.append(tuple(   pad_list(base(high_tuple[-7],3),3)   ))#center,most,least
        self.data.append(tuple(   pad_list(base(high_tuple[-8],3),3)   ))#center,most,least
        self.data.append(tuple(   pad_list(base(high_tuple[-9],3),3)   ))#center,most,least
        self.data.append(tuple(   pad_list(base(high_tuple[-10],3),3)   ))#center,most,least
        self.data = tuple(self.data)
        if sum(self.high_tuple[:-4]) > 0:#has 5
            self.size = high_glyph.fifth_radi*2
        elif sum(self.high_tuple[:-3]) > 0:#has 4
            self.size = high_glyph.forth_radi*2
        elif sum(self.high_tuple[:-2]) > 0:#has 3
            self.size = high_glyph.third_radi*2
        elif sum(self.high_tuple[:-1]) > 0:#has 2
            self.size = high_glyph.second_radi*2
        elif sum(self.high_tuple) > 0:#has 1
            self.size = high_glyph.center_size*2
        else:
            self.size = 0
        
    def delete(self):
        self.set_data_from_high_tuple((0,0,0,0,0,0,0,0,0,0))
        self.canvas.delete(self.tag)

    def update_display(self):
        self.canvas.delete(self.tag)
        if sum(self.high_tuple[:-5]) > 0:#has pods
            gsize = 6
        elif sum(self.high_tuple[:-4]) > 0:#has 5
            gsize = 5
        elif sum(self.high_tuple[:-3]) > 0:#has 4
            gsize = 4
        elif sum(self.high_tuple[:-2]) > 0:#has 3
            gsize = 3
        elif sum(self.high_tuple[:-1]) > 0:#has 2
            gsize = 2
        elif sum(self.high_tuple) > 0:#has 1
            gsize = 1
        else:#non existant
            gsize = 0
        centerx = self.startx + (self.size/2)
        centery = self.starty
        if gsize >= 1:
            if self.data[0] == 1:
                circle(self.canvas,centerx,centery,high_glyph.center_size,self.tag)
            elif self.data[0] == 2:
                circle(self.canvas,centerx,centery,high_glyph.center_size,self.tag,fill="#000000")
        if gsize >= 2:
            circle(self.canvas,centerx,centery,high_glyph.second_radi,self.tag)
        if gsize >= 3:
            circle(self.canvas,centerx,centery,high_glyph.third_radi,self.tag)
        if gsize >= 4:
            circle(self.canvas,centerx,centery,high_glyph.forth_radi,self.tag)
        if gsize >= 5:
            circle(self.canvas,centerx,centery,high_glyph.fifth_radi,self.tag)
        if not self.data[1][0]:#2nd nodes
            node(self.canvas,centerx,centery+high_glyph.second_radi-1,self.data[1][1],self.tag)
            node(self.canvas,centerx,centery-high_glyph.second_radi+1,self.data[1][2],self.tag)
        else:
            node(self.canvas,centerx-high_glyph.second_radi+1,centery,self.data[1][1],self.tag)
            node(self.canvas,centerx+high_glyph.second_radi-1,centery,self.data[1][2],self.tag)
        #3rd
        node(self.canvas,*polar(centerx,centery,high_glyph.third_radi-1,300),self.data[2][0],self.tag)
        node(self.canvas,*polar(centerx,centery,high_glyph.third_radi-1,60),self.data[2][1],self.tag)
        node(self.canvas,centerx,centery-high_glyph.third_radi+1,self.data[2][2],self.tag)
        #4th
        node(self.canvas,*polar(centerx,centery,high_glyph.forth_radi-1,225),self.data[3][0],self.tag)
        node(self.canvas,*polar(centerx,centery,high_glyph.forth_radi-1,315),self.data[3][1],self.tag)
        node(self.canvas,*polar(centerx,centery,high_glyph.forth_radi-1,45),self.data[3][2],self.tag)
        node(self.canvas,*polar(centerx,centery,high_glyph.forth_radi-1,135),self.data[3][3],self.tag)
        #5th
        node(self.canvas,*polar(centerx,centery,high_glyph.fifth_radi,203),self.data[4][0],self.tag)
        node(self.canvas,*polar(centerx,centery,high_glyph.fifth_radi,248),self.data[4][1],self.tag)
        node(self.canvas,*polar(centerx,centery,high_glyph.fifth_radi,293),self.data[4][2],self.tag)
        node(self.canvas,*polar(centerx,centery,high_glyph.fifth_radi,338),self.data[4][3],self.tag)
        node(self.canvas,*polar(centerx,centery,high_glyph.fifth_radi,23),self.data[4][4],self.tag)
        node(self.canvas,*polar(centerx,centery,high_glyph.fifth_radi,68),self.data[4][5],self.tag)
        node(self.canvas,*polar(centerx,centery,high_glyph.fifth_radi,113),self.data[4][6],self.tag)
        node(self.canvas,*polar(centerx,centery,high_glyph.fifth_radi,158),self.data[4][7],self.tag)
        if self.data[5][0]:
            valid23links = [45,135,225,315]
            if (self.data[1][0] or (self.data[1][2] == 0)) and (self.data[2][2] == 0):
                valid23links.append(180)
            if (not self.data[1][0]) or (self.data[1][2] == 0):
                valid23links.append(90)
            if (not self.data[1][0]) or (self.data[1][1] == 0):
                valid23links.append(270)
            if self.data[1][0] or (self.data[1][1] == 0):
                valid23links.append(0)
            angle = valid23links[self.high_tuple[-5]%len(valid23links)]
            self.canvas.create_line(*polar(centerx,centery,high_glyph.second_radi,angle),*polar(centerx,centery,high_glyph.third_radi,angle),tags=self.tag)
        if self.data[5][1]:
            valid34links = list(range(0,360))
            if self.data[2][2] >= 1:
                valid34links = rec_remove(valid34links,list(range(166,194)))
            if self.data[2][1] >= 1:
                valid34links = rec_remove(valid34links,list(range(46,74)))
            if self.data[2][0] >= 1:
                valid34links = rec_remove(valid34links,list(range(286,314)))
            if self.data[3][3] >= 1:
                valid34links = rec_remove(valid34links,list(range(125,146)))
            if self.data[3][2] >= 1:
                valid34links = rec_remove(valid34links,list(range(35,55)))
            if self.data[3][1] >= 1:
                valid34links = rec_remove(valid34links,list(range(305,325)))
            if self.data[3][0] >= 1:
                valid34links = rec_remove(valid34links,list(range(215,235)))
            angle = valid34links[self.high_tuple[-5]%len(valid34links)]
            self.canvas.create_line(*polar(centerx,centery,high_glyph.third_radi,angle),*polar(centerx,centery,high_glyph.forth_radi,angle),tags=self.tag)
        if self.data[5][2] >= 1:
            valid45links = list(range(0,360))
            if self.data[4][7] >= 1:
                valid45links = rec_remove(valid45links,list(range(150,166)))
            if self.data[4][6] >= 1:
                valid45links = rec_remove(valid45links,list(range(105,121)))
            if self.data[4][5] >= 1:
                valid45links = rec_remove(valid45links,list(range(60,76)))
            if self.data[4][4] >= 1:
                valid45links = rec_remove(valid45links,list(range(15,31)))
            if self.data[4][3] >= 1:
                valid45links = rec_remove(valid45links,list(range(330,346)))
            if self.data[4][2] >= 1:
                valid45links = rec_remove(valid45links,list(range(285,301)))
            if self.data[4][1] >= 1:
                valid45links = rec_remove(valid45links,list(range(240,256)))
            if self.data[4][0] >= 1:
                valid45links = rec_remove(valid45links,list(range(195,211)))
                
            if self.data[4][7] >= 3:
                valid45links = rec_remove(valid45links,list(range(146,170)))
            if self.data[4][6] >= 3:
                valid45links = rec_remove(valid45links,list(range(101,125)))
            if self.data[4][5] >= 3:
                valid45links = rec_remove(valid45links,list(range(56,80)))
            if self.data[4][4] >= 3:
                valid45links = rec_remove(valid45links,list(range(11,35)))
            if self.data[4][3] >= 3:
                valid45links = rec_remove(valid45links,list(range(326,350)))
            if self.data[4][2] >= 3:
                valid45links = rec_remove(valid45links,list(range(281,305)))
            if self.data[4][1] >= 3:
                valid45links = rec_remove(valid45links,list(range(236,260)))
            if self.data[4][0] >= 3:
                valid45links = rec_remove(valid45links,list(range(191,215)))

            if self.data[3][3] >= 1:
                valid45links = rec_remove(valid45links,list(range(126,144)))
            if self.data[3][2] >= 1:
                valid45links = rec_remove(valid45links,list(range(36,54)))
            if self.data[3][1] >= 1:
                valid45links = rec_remove(valid45links,list(range(306,324)))
            if self.data[3][0] >= 1:
                valid45links = rec_remove(valid45links,list(range(216,234)))

            for i in range(0,self.data[5][2]):
                angle = valid45links[self.high_tuple[-5]%len(valid45links)]
                self.canvas.create_line(*polar(centerx,centery,high_glyph.forth_radi,angle),*polar(centerx,centery,high_glyph.fifth_radi,angle),tags=self.tag)
                valid45links = rec_remove(valid45links,list(range(angle-5,angle+5)))
        #pods:
        podnumber = 0
        for i in range(6,10):
            if sum(self.data[i]) >= 1:
                podnumber += 1
        if podnumber < 4:
            if sum(self.data[6]) >= 1:
                pod_cl = [180,158]
                angle = pod_cl[self.high_tuple[-5]%len(pod_cl)]
                pod(self.canvas,*polar(centerx,centery,high_glyph.fifth_radi+pod.outer_radius,angle),angle,self.data[6],self.tag)
            if sum(self.data[7]) >= 1:
                pod_cl = [23]
                angle = pod_cl[self.high_tuple[-5]%len(pod_cl)]
                pod(self.canvas,*polar(centerx,centery,high_glyph.fifth_radi+pod.outer_radius,angle),angle,self.data[7],self.tag)
            if sum(self.data[8]) >= 1:
                pod_cl = [338,0]
                angle = pod_cl[self.high_tuple[-5]%len(pod_cl)]
                pod(self.canvas,*polar(centerx,centery,high_glyph.fifth_radi+pod.outer_radius,angle),angle,self.data[8],self.tag)
            if sum(self.data[9]) >= 1:
                pod_cl = [203]
                angle = pod_cl[self.high_tuple[-5]%len(pod_cl)]
                pod(self.canvas,*polar(centerx,centery,high_glyph.fifth_radi+pod.outer_radius,angle),angle,self.data[9],self.tag)
        if podnumber == 4:
            #gpls = []
            #gpls.append(self.high_tuple[-5]%2)
            #if gpls[0] == 0:
            #    gpls.append(self.high_tuple[-5]%3)
            #else:
            #    gpls.append(1+round(self.high_tuple[-5]*3.141592653589793)%2)
            #if gpls[0] == 0:
            #    gpls.append(1+round(self.high_tuple[-5]*3.141592653589793)%3)
            #else:
            #    if gpls[1] == 1:
            #areas = "01230123"
            #locations = []
            #entropy = str(round(self.high_tuple[-5]*3.141592653589793))
            gpls = []
            location = {0:0,1:0,2:0,3:0}
            allowed_set = "0123"
            entropy = self.high_tuple[-5]*3.141592653589793
            for podnum in range(1,5):
                loc = int(allowed_set[round(entropy)%len(allowed_set)])
                gpls.append(loc)
                entropy *= 7.3928563956295674
                location[loc] += 1
                if location[loc] == 2:
                    allowed_set = allowed_set.replace(str(loc),"")
            gpls.sort()

            #loc_0_slots = [158,169]
            #loc_1_slots = [23,11]
            #loc_2_slots = [338,349]
            #loc_3_slots = [203,192]
            #print(gpls)
            #if gpls[0] == 0:
            #    p1angle = loc_0_slots[self.high_tuple[-7]%len(loc_0_slots)]
            #    pod(self.canvas,*polar(centerx,centery,high_glyph.fifth_radi+pod.outer_radius,angle),angle,self.data[6],self.tag)
            #elif gpls[0] == 1:
            #    p1angle = loc_1_slots[self.high_tuple[-7]%len(loc_1_slots)]
            #    pod(self.canvas,*polar(centerx,centery,high_glyph.fifth_radi+pod.outer_radius,angle),angle,self.data[6],self.tag)
            #elif gpls[0] == 2:
            #    p1angle = loc_2_slots[self.high_tuple[-7]%len(loc_2_slots)]
            #    pod(self.canvas,*polar(centerx,centery,high_glyph.fifth_radi+pod.outer_radius,angle),angle,self.data[6],self.tag)
            pangles = []
            last_pod = -1
            loc_slots = {}
            loc_slots[0] = [158,169]
            loc_slots[1] = [23,11]
            loc_slots[2] = [338,349]
            loc_slots[3] = [203,192]
            last_center_coords = ()
            
            
            for podnum in range(0,4):
                if gpls[podnum] == last_pod:
                    if gpls[podnum] == 0 or gpls[podnum] == 3:
                        #print("here")
                        options = [pangles[-1],180]
                        options.sort()
                        sec_slots = list(range(*options))
                        pangles.append(sec_slots[self.high_tuple[3-podnum]%len(sec_slots)])
                        pod(self.canvas,*polar(last_center_coords[0],last_center_coords[1],2*pod.outer_radius,pangles[-1]),pangles[-1],self.data[6+podnum],self.tag)

                else:
                    pangles.append(loc_slots[gpls[podnum]][self.high_tuple[3-podnum]%len(loc_slots[gpls[podnum]])])
                    last_center_coords = polar(centerx,centery,high_glyph.fifth_radi+pod.outer_radius,pangles[-1])
                    pod(self.canvas,*last_center_coords,pangles[-1],self.data[6+podnum],self.tag)
                last_pod = gpls[podnum]
                
                

class high_missive:

    sentance_gap = 20
    line_size = (2*high_glyph.fifth_radi)+(4*pod.outer_radius)+sentance_gap
    valid_letters = {' ','a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','.'}

    def __init__(self,canvas,startx,starty,data=None):
        self.canvas = canvas
        self.startx = startx
        self.starty = starty
        self.max_x_len = self.canvas.winfo_width()-4
        self.max_y_len = self.canvas.winfo_height()-4
        self.underglyphs = []
        self.words = ()
        self.missive = ""
        if data != None:
            self.setdata(data)
            

    def setdata(self,missive):
        missive = missive.lower()
        missive = missive.replace("!",".").replace("?",".").replace(",",".").replace("'","")
        #error checking
        if high_missive.valid_letters.issuperset(missive):
            entry.config(fg="#000000")
        else:
            entry.config(fg="#ff0000")
            return None

        self.missive = missive
        words = []
        
        sentances = missive.split(".")
        if sentances[-1] == "":
            sentances = sentances[:-1]
        for sentance in sentances:
            words.append([])
            for word in sentance.split(" "):
                if word != "":
                    words[-1].append(word)
        twords = []
        for sentance in words:
            twords.append(tuple(sentance))
        self.words = tuple(twords)


        #make glyphs
        for glyphs in self.underglyphs:
            for glyph in glyphs:
                glyph.delete()
        self.underglyphs = []
        curx = self.startx - high_missive.sentance_gap
        cury = self.starty
        for sentance in self.words:
            self.underglyphs.append([])
            curx += high_missive.sentance_gap
            if curx + high_missive.expected_sen_size(sentance) > self.max_x_len:
                if cury + 1.5*high_missive.line_size < self.max_y_len:
                    cury += high_missive.line_size
                    curx = self.startx
                else:
                    print("WARN: sentance too large for viewing window")
                    cury += high_missive.line_size
                    curx = self.startx
            for word in sentance:
                curglyph = high_glyph(self.canvas,curx,cury,self,word)
                self.underglyphs[-1].append(curglyph)
                curx += curglyph.size
        self.reload_display()


    def reload_display(self):
        for glyphs in self.underglyphs:
            for glyph in glyphs:
                glyph.update_display()
                
                
    def expected_sen_size(sentance):
        if type(sentance) == str:
            words = sentance.lower().split(" ")
        else:
            words = sentance[:]
        size = 0
        for word in words:
            size += high_missive.expected_word_size(word)
        return size
        
    def expected_word_size(word):
        high_tuple = number_to_high_tuple(word_to_number(word))
        if sum(high_tuple[:-4]) > 0:#has 5
            return high_glyph.fifth_radi*2
        elif sum(high_tuple[:-3]) > 0:#has 4
            return high_glyph.forth_radi*2
        elif sum(high_tuple[:-2]) > 0:#has 3
            return high_glyph.third_radi*2
        elif sum(high_tuple[:-1]) > 0:#has 2
            return high_glyph.second_radi*2
        elif sum(high_tuple) > 0:#has 1
            return high_glyph.center_size*2
        else:
            return 0


            
##tk = Tk()
##canvas = Canvas(tk,width=500,height=150)
##canvas.pack() 
##
##q = high_glyph(canvas,20,75,None,'lord')
##p = high_glyph(canvas,20+q.size,75,None,'chronos')
##o = high_glyph(canvas,p.startx+p.size,75,None,'timepuardian')
##m = high_glyph(canvas,o.startx+o.size,75,None,'snxbkppidian')
##
##ttk = Toplevel(tk)
##canvas2 = Canvas(ttk,width=500,height=400)
##canvas2.pack()
##tk.geometry("+50+35")
##ttk.geometry("+100+250")
##ttk.update()
##ttk.update_idletasks()
##
##pq = high_missive(canvas2,20,75,"The lord chronos is here. fear his wrath.")

tk = Tk()
canvas = Canvas(tk,width=1000,height=700)
canvas.grid(row=0,column=0,columnspan=2)
tk.update()
tk.update_idletasks()
sentance = high_missive(canvas,20,75)
entry = Entry(tk)
entry.grid(row=1,column=0,sticky="nsew")
btn = Button(tk,text="Iridate",bg="#0000ff",fg="#00ffff",command=lambda *x: sentance.setdata(entry.get()))
btn.grid(row=1,column=1,sticky="nsew")

#ttk = Toplevel(tk)














