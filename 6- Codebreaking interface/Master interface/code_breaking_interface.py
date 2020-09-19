from tkinter import *
from math import log
tk = Tk()
tk.title("Master code breaking interface v0.31")
#configs
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
frequency_alphabet = 'abcdefghijklmnopqrstuvwxyz' # the letters that you want counted (and that substitute to somthing)
Unencripted_char = ["’",'1', '2', '3', '4', '5', '6', '7', '8', '9', '0','"',"'", '!', ':', ';', '.', '>', ',', '<', '/', '?', '#', '~', '@', '[', ']', '{', '}', '(', ')', '*', '%', '£', '$',"-"]
safe_inferable_letters = alphabet[:]
for i in [0,1,2,3,4,5,6,7,8,9,".","!"]:
    safe_inferable_letters.append(str(i))

expected_letter_freq = {'a': 0.08167, 'b': 0.01492, 'c': 0.02782, 'd': 0.04253, 'e': 0.12702, 'f': 0.02228, 'g': 0.02015, 'h': 0.06094, 'i': 0.06966, 'j': 0.00153, 'k': 0.00772, 'l': 0.04025, 'm': 0.02406, 'n': 0.06749, 'o': 0.07507, 'p': 0.01929, 'q': 0.00095, 'r': 0.05987, 's': 0.06327, 't': 0.09056, 'u': 0.02758, 'v': 0.00978, 'w': 0.0236, 'x': 0.0015, 'y': 0.01974, 'z': 0.00074}
sd = {'a': 0.00789012, 'b': 0.003649156, 'c': 0.003611949, 'd': 0.007637117, 'e': 0.007186551, 'f': 0.004488449, 'g': 0.00365048, 'h': 0.005114745, 'i': 0.007809548, 'j': 0.001057792, 'k': 0.003598454, 'l': 0.005288391, 'm': 0.003424275, 'n': 0.005683005, 'o': 0.004855843, 'p': 0.002946276, 'q': 0.000675475, 'r': 0.00555803, 's': 0.004896678, 't': 0.009085299, 'u': 0.004026279, 'v': 0.002903394, 'w': 0.004071829, 'x': 0.00151267, 'y': 0.004860834, 'z': 0.00117573}

_modes = ("Direct Translation","Replace ?","Predictive Text")
_starting_mode = 1
_types = ("Caesar cipher","Substitution cipher","Vigenere cipher")
_starting_type = 3
_OUT_box_fonts = 'Courier 10 bold'
_DT_col = "#111111"
_K_col = "#0055ff"
_WC_col = "#000000"
_P_col = "#989898"
_C_sel_col = "#898989"
_C_seleg_col = "#d7d7ca"
_C_high_col = "#00aa00"
_SET_col = "#8888ff"

import time


box_size = [100,20]

#Global Vars

all_words = open("words-by-frequency.txt").read().split()
all_wordcost = dict((k, log((i+1)*log(len(all_words)))) for i,k in enumerate(all_words))
for n in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',".","!"]:
    all_wordcost[n] = log(2)
all_maxword = max(len(x) for x in all_words)

Mode = _modes[_starting_mode-1]
Ctype = _types[_starting_type-1]
Key_cea = 0
Data_form_cea = "normal"
sub_freq_old_message = ""

sub_freq_om_bypass = False
custom_sel_region = ()
box_just_selected = False
to_gu = False
are_guing = False
vin_old_text = ""


#code_start
key_frame = Frame(tk,padx=10)
key_frame.grid(row=1,column=1,rowspan=2)
letter_frame = Frame(key_frame)
letter_frame.grid()
cea_frame = Frame(key_frame)
vin_frame = Frame(key_frame)
option_frame = Frame(tk)
option_frame.grid(row=0,column=1,columnspan=4,sticky="w",padx=10,pady=1)
active_info_area = Frame(tk,width=300,height=712,bd=1,relief=SUNKEN)
active_info_area.grid(row=1,column=4,rowspan=3,padx=2)
box_scrollbar = Scrollbar(tk,orient=VERTICAL)
box_scrollbar.grid(row=1,column=3,sticky="nsew",rowspan=2)

def box_messagebox_force_scroll(*e):
    output_box.yview_moveto(e[0])


message_box = Text(tk,width=box_size[0],height=box_size[1],yscrollcommand=box_messagebox_force_scroll,font='Courier 10',selectbackground="#878787",fg="black")
temp = message_box.bindtags()
message_box.bindtags((temp[0],temp[1],"Post_init_box_tag","Post_init_tag",*temp[2:]))
del temp

def conditional_binding(e):
    if e.keysym in ["Shift_L","Control_L"]:
        pass
    else:
        Pre_Global_update()

message_box.bind_class("Post_init_tag","<FocusOut>",lambda *e: Pre_Global_update())
message_box.bind_class("Post_init_tag","<Key>",conditional_binding,True)

output_box = Text(tk,width=box_size[0],height=box_size[1],yscrollcommand=box_scrollbar.set,state=DISABLED,font=_OUT_box_fonts,selectbackground="#878787")
temp = output_box.bindtags()
output_box.bindtags((temp[0],temp[1],"Post_init_PrePost_outbox","Post_init_box_tag",*temp[2:]))
del temp
message_box.grid(row=1,column=2,sticky="n")
output_box.grid(row=2,column=2,sticky="n")
output_box.tag_configure("Direct Translation",foreground=_DT_col)
output_box.tag_configure("Known",foreground=_K_col)
output_box.tag_configure("Set",foreground=_SET_col)#font=_OUT_box_fonts+" underline"#font=_OUT_box_fonts[:-5]#font=_OUT_box_fonts+" bold"
output_box.tag_configure("Wild card",foreground=_WC_col)
output_box.tag_configure("Predicted",foreground=_P_col)

message_box.tag_configure("custom_sel_eg",background=_C_seleg_col)
output_box.tag_configure("custom_sel_eg",background=_C_seleg_col)
message_box.tag_configure("custom_sel",background=_C_sel_col)
output_box.tag_configure("custom_sel",background=_C_sel_col)
output_box.tag_configure("highlight_letter",foreground=_C_high_col)

def box_scrolly_cmd(*args):
    message_box.yview(*args)
    output_box.yview(*args)

def box_outbox_force_scroll(*e):
    message_box.yview_moveto(output_box.yview()[0])

output_box.bind_class("Post_init_PrePost_outbox","<MouseWheel>",box_outbox_force_scroll,True)



box_scrollbar.config(command=box_scrolly_cmd)





box_data_frame = Frame(tk)
box_data_frame.grid(row=3,column=2,sticky="nsew")
box_data_frame_left = Frame(box_data_frame)
box_data_frame_left.pack(side="left")
box_data_frame_right = Frame(box_data_frame)
box_data_frame_right.pack(side="right")

def capitalise(text):
    out = ""
    had_sentance_end = True
    for index,letter in enumerate(text):
        if letter.isalpha() and had_sentance_end:
            out += letter.upper()
            had_sentance_end = False
        else:
            if letter in [".","!","?"]:
                had_sentance_end = True
            if letter == "i" and text[index-1] == " " and text[index+1] == " ":
                out += letter.upper()
            else:
                out += letter
    return out

def fix_spacing_pressed():
    message = output_box.get(0.0,END)
    message = message.replace(" ","").lower()
    sanitised_input = ""
    for i in message:
        if i in safe_inferable_letters:
            sanitised_input += str(i)
    infered = infer_spaces(sanitised_input)
    
    out = ""
    for j,i in enumerate(infered):
        if not i in [" ",".","!"]:
            out += i
        else:
            if i == " ":
                try:
                    if infered[j-1].isdigit() and infered[j+1].isdigit():
                        pass
                    else:
                        out += i
                except IndexError:
                    print("WARN: attempted imposible operation")
            if i in [".","!"]:
                out = out[:-1]
                out += i
                out += " "
    
    out = capitalise(out)

    fltk = Toplevel(tk)
    fltk.lift(tk)
    fltk.attributes("-topmost", True)
    fltk.title("Pretty Read-out")
    def close():
        tk.focus_set()
        fltk.destroy()
    fltk.bind("<FocusOut>",lambda *e: close())
    floutputtxt = Text(fltk,wrap=WORD,font=("Times New Roman", 13),width=box_size[0],height=int(round(box_size[1]*1.8,0)))
    floutputtxt.grid(row=1)
    floutputtxt.insert(0.0,out)
    floutputtxt.focus_force()

    

def infer_spaces(s):
    """Uses dynamic programming to infer the location of spaces in a string
    without spaces."""

    # Find the best match for the i first characters, assuming cost has
    # been built for the i-1 first characters.
    # Returns a pair (match_cost, match_length).
    def best_match(i):
        candidates = enumerate(reversed(cost[max(0, i-all_maxword):i]))
        return min((c + all_wordcost.get(s[i-k-1:i], 9e999), k+1) for k,c in candidates)

    # Build the cost array.
    cost = [0]
    for i in range(1,len(s)+1):
        c,k = best_match(i)
        cost.append(c)

    # Backtrack to recover the minimal-cost string.
    out = []
    i = len(s)
    while i>0:
        c,k = best_match(i)
        assert c == cost[i]
        out.append(s[i-k:i])
        i -= k

    return " ".join(reversed(out))

def coinc(message,shift):
    ans = 0
    shifted = ("¬"*shift) + message
    for index in range(0,len(message)):
        if message[index] == shifted[index]:
            ans += 1
    return ans

def mean(values):
    return sum(values)/len(values)

class vin_len_con_box:

    instances = {}

    def __init__(self,master,shift):
        self.shift=shift
        self.master = master
        self.canvas = Canvas(master,width=290,height=20)
        self.canvas.grid(row=shift,column=0,pady=0)
        self.bar = self.canvas.create_rectangle(2,2,290,20,fill="#338494")
        self.text = self.canvas.create_text(5,12,anchor="w",text=str(shift),font="Courier 9")
        vin_len_con_box.instances[shift] = self

    def update(data):
        maxval = max(data.values())
        for i in range(1,21):
            vin_len_con_box.instances[i]._own_update(data[i],maxval)

    def _own_update(self,val,maxval):
        text = str(self.shift) + ": "
        if len(text) == 3:
            text += " "
        text += str(val)
        self.canvas.itemconfig(self.text,text=text)
        self.canvas.coords(self.bar,2,2,2+round(((val/maxval)*288)),20)
        
            









def remrep(lis):
    new_list = []
    for i in lis:
        if not i in new_list:
            new_list.append(i)
    return new_list

def freq_set_alpha():
    global frequency_alphabet
    astk = Toplevel(tk)
    astk.lift(tk)
    astk.attributes("-topmost", True)
    astk.title("Set Alphabet")
    def close():
        global frequency_alphabet
        frequency_alphabet = "".join(sorted("".join(set(str(ase1.get(0.0,END)).replace("\n","")))))
        tk.focus_set()
        astk.destroy()
    astk.bind("<FocusOut>",lambda *e: close())
    Label(astk,text="The letters you want counted or\n that are the encrypted substitution for somthing",width=50,height=2).grid(row=0)
    ase1 = Text(astk,width=50,height=5)
    ase1.grid(row=1)
    ase1.insert(0.0,frequency_alphabet)
    ase1.focus_force()

def frq_to_percent(dic):
    book_pd = {}
    bsum = sum(dic.values())
    for i in list(dic.keys())[:]:
        book_pd[i] = round(dic[i]/bsum,7)
    return book_pd

def pos(x):
    if x < 0:
        return -x
    return x

def inside(val1,val2,sd):
    delta = pos(val1-val2)
    return (delta/sd)

def pad_to_y(x,y):
    if len(x) > y:
        return x
    else:
        return str(x) + ((y-len(x))*" ")

def sub_freq_ei_func():
    global sub_freq_om_bypass
    sub_freq_om_bypass = True
    active_update()

def mode_changed():
    global Mode
    Mode = opt_mode.get()
    Pre_Global_update()

def type_changed():
    global Ctype,current_key,current_btns
    Ctype = opt_type.get()
    current_key.grid_forget()
    current_btns.grid_forget()
    current_active.grid_forget()
    if Ctype == "Caesar cipher":
        current_key = cea_frame
        current_btns = active_button_section_cea
        active_btn_clicked("cea-pred")
    elif Ctype == "Substitution cipher":
        current_key = letter_frame
        current_btns = active_button_section_sub
        active_btn_clicked("sub-freq")
    elif Ctype == "Vigenere cipher":
        current_key = vin_frame
        current_btns = active_button_section_vin
        active_btn_clicked("vin-len")
    current_key.grid()
    current_btns.grid(row=1,column=0,sticky="nsew")
    Pre_Global_update()


def Theorum():
    message = message_box.get(0.0,END)
    length = vin_length.get()

#box_datas
def box_data_update(e):
    index = str(e.widget.index(CURRENT)).split(".")
    line = int(index[0]) + (int(index[1])//box_size[0])
    col = int(index[1]) % box_size[0]
    box_data_label_ln.config(text="Ln: " + str(line))
    box_data_label_col.config(text="Char: " + str(col))

def sel_other_in_box(e):
    message_box.tag_remove("custom_sel",0.0,END)
    output_box.tag_remove("custom_sel",0.0,END)
    index_region = e.widget.tag_nextrange(SEL,0.0)
    if len(index_region) == 0:
        return True
    if index_region[0] == index_region[1]:
        sel_box_clear()
    global custom_sel_region
    custom_sel_region = index_region
    message_box.tag_add("custom_sel",*index_region)
    output_box.tag_add("custom_sel",*index_region)
    sel_findex = str(e.widget.index(SEL_FIRST)).split(".")
    fline = int(sel_findex[0]) + (int(sel_findex[1])//box_size[0])
    fcol = int(sel_findex[1]) % box_size[0]
    sel_lindex = str(e.widget.index(SEL_LAST)).split(".")
    lline = int(sel_lindex[0]) + (int(sel_lindex[1])//box_size[0])
    lcol = int(sel_lindex[1]) % box_size[0]
    box_data_label_sel.config(text="Sel: ["+str(fline)+":"+str(fcol)+" , " + str(lline)+":"+str(lcol) + "]")
    if len(e.widget.get(*index_region)) >= 3:
        sel_simmilar(e)

def sel_simmilar(e):
    index_region = e.widget.tag_nextrange(SEL,0.0)
    if len(index_region) == 0:
        return True
    if index_region[0] == index_region[1]:
        sel_box_clear()
    e.widget.tag_remove("custom_sel_eg",0.0,END)
    sel_dat = e.widget.get(*index_region)
    found_index = "1.0"
    if e.widget.search(sel_dat,"1.0",END) == "1.0":
        found_indexes = ["1.0"]
    else:
        found_indexes = []
    while found_index != "":
        found_index = e.widget.search(sel_dat,found_index + "+ 1 chars",END)
        if found_index != "":
            found_indexes.append(found_index)
    for indexsel in found_indexes:
        e.widget.tag_add("custom_sel_eg",indexsel,indexsel+" + "+str(len(sel_dat))+" chars")
        
def _sel_sim_sanitiser(e):
    try:
        if len(e.widget.get(*e.widget.tag_nextrange(SEL,0.0))) >= 2:
            sel_simmilar(e)
    except:
        sel_simmilar(e)

def sel_box_clear():
    message_box.tag_remove("custom_sel",0.0,END)
    output_box.tag_remove("custom_sel",0.0,END)
    message_box.tag_remove("custom_sel_eg",0.0,END)
    output_box.tag_remove("custom_sel_eg",0.0,END)
    global custom_sel_region
    custom_sel_region = ()
    box_data_label_sel.config(text="")
    
    
message_box.bind_class("Post_init_box_tag","<Motion>",box_data_update ,True)
message_box.bind_class("Post_init_box_tag","<B1-Motion>",sel_other_in_box ,True)
message_box.bind_class("Post_init_box_tag","<Button-1>",lambda *e: sel_box_clear() ,True)
message_box.bind_class("Post_init_box_tag","<FocusOut>",lambda *e: sel_box_clear() ,True)
message_box.bind_class("Post_init_box_tag","<Double-Button-1>",sel_other_in_box ,True)
message_box.bind_class("Post_init_box_tag","<ButtonRelease-1>", _sel_sim_sanitiser ,True)
box_data_label_ln = Label(box_data_frame_left,text="Ln: ???")
box_data_label_col = Label(box_data_frame_left,text="Char: ???")
box_data_label_ln.grid(row=0,column=0,sticky="wns")
box_data_label_col.grid(row=0,column=1,sticky="wns")
box_data_label_sel = Label(box_data_frame_left,text="")
box_data_label_sel.grid(row=0,column=2,sticky="wns")

box_data_fix_spacing = Button(box_data_frame_right,text="Fix Spacing",command=lambda x=0: fix_spacing_pressed())
box_data_fix_spacing.grid(row=0,column=99,sticky="ens")

#options
Label(option_frame,text="Type:").grid(row=0,column=0)
opt_type = StringVar(option_frame)
opt_type.set(Ctype)
opt_type.trace("w",lambda *e: type_changed())
opt_type_w = OptionMenu(option_frame,opt_type,*_types)
opt_type_w.config(width=15)
opt_type_w.grid(row=0,column=1)
Label(option_frame,text="   Mode:").grid(row=0,column=2)
opt_mode = StringVar(option_frame)
opt_mode.set(Mode)
opt_mode.trace("w",lambda *e: mode_changed())
opt_mode_w = OptionMenu(option_frame,opt_mode,*_modes)
opt_mode_w.config(width=15)
opt_mode_w.grid(row=0,column=3)
Label(option_frame,text="   Structured:").grid(row=0,column=4)
opt_struc = IntVar(option_frame)
opt_struc.set(0)
opt_struc.trace("w",lambda *e: Pre_Global_update())
opt_struc_w = Checkbutton(option_frame,variable=opt_struc)
opt_struc_w.grid(row=0,column=5)
Label(option_frame,text="   Error highlighting:").grid(row=0,column=6)
opt_error = IntVar(option_frame)
opt_error.set(1)
opt_error_w = Checkbutton(option_frame,variable=opt_error)
opt_error_w.grid(row=0,column=7)
#actives - commands
def active_btn_clicked(which):
    global current_active,current_active_name
    current_active.grid_forget()
    if which == "sub-dict":
        current_active = sub_dict_frame
    elif which == "sub-freq":
        current_active = sub_freq_frame
    elif which == "cea-pred":
        current_active = cea_pred_frame
    elif which == "vin-len":
        current_active = vin_len_frame
    elif which == "vin-tool":
        current_active = vin_tool_frame
    elif which == "vin-the":
        current_active = vin_the_frame
    current_active.grid()
    current_active_name = which
    active_update()



def active_update(force=None):
    if force != None:
        which = force
    else:
        which = current_active_name
    if which == "cea-pred":
        text = "Likely Preditions:\n\n"
        message = message_box.get(0.0,END)
        message = message.lower().replace("\n","")
        if opt_struc.get():
            words_incp = message.split(" ")
            single_letter_words = []
            follows_aps = []
            for word in words_incp:
                if len(word) == 1:
                    if not word in single_letter_words:
                        single_letter_words.append(word)
                if len(word) >= 3:
                    if word[-2] in ["’","'"]:
                        if not word[-1] in follows_aps:
                            follows_aps.append(word[-1])
            slrot = []
            if len(single_letter_words) > 2:
                text += "More than 2 one letter words! ("+",".join(single_letter_words)+")\n\n"
            else:
                for letter in single_letter_words:
                    slrot.append((26-alphabet.index(letter)+alphabet.index("a"))%26)
                    slrot.append((26-alphabet.index(letter)+alphabet.index("i"))%26)
                    text += str(letter) + " is likely a or i (" + str(slrot[-2]) + ","+ str(slrot[-1]) + ")\n"
                text += "\n"
            aprot = []
            if len(single_letter_words) > 4:
                text += "More than 4 letters that follow a [']! ("+",".join(follows_aps)+")\n\n"
            elif len(single_letter_words) > 2:
                text += "More than 2 letters that follow a [']! ("+",".join(follows_aps)+")\n    Likely: t,s or rarely m,d\n\n"
            else:
                for letter in follows_aps:
                    aprot.append((26-alphabet.index(letter)+alphabet.index("t"))%26)
                    aprot.append((26-alphabet.index(letter)+alphabet.index("s"))%26)
                    text += str(letter) + " is likely t or s (" + str(aprot[-2]) + ","+ str(aprot[-1]) + ")\n"
                text += "\n"

            if len(slrot+aprot) != 0:
                likly_hood = {}
                for i in remrep(slrot+aprot):
                    likly_hood[i] = slrot.count(i)+aprot.count(i)

                temp = sorted(likly_hood.items(), key=lambda kv: kv[1])
                temp.reverse()

                def temp_c(dic):
                    isum = 0
                    for i in dic.values():
                        isum += i**2
                    return isum
                    

                text += "Most likely key is: " + str(temp[0][0]) + " (certainty:~" + str(round((temp[0][1]**2/temp_c(likly_hood))*100,0)) + "%)"
                global Key_cea
                Key_cea = temp[0][0]

        else:
            Key_cea = 0#temp
        cea_pred_label.config(text=text)
    if which == "sub-freq":
        text = "Frequency Analysis:\n\n"
        message = message_box.get(0.0,END).lower()
        if message == "\n":
            text += "Error: No message detected"
            sub_freq_label.config(text = text)
            return None
        global sub_freq_old_message,sub_freq_om_bypass
        if message.replace(" ","") == sub_freq_old_message and (not sub_freq_om_bypass):
            sub_freq_om_bypass = False
            return None
        letterqs = {}
        global frequency_alphabet
        for letter in frequency_alphabet:
            letterqs[letter] = message.count(letter)
        if sum(letterqs.values()) == 0:
            text += "Error: Letters sum to Zero"
            sub_freq_label.config(text = text)
            print("Error: Letters sum to Zero")
            return None
        freq_list = sorted(letterqs.items(), key=lambda kv: kv[1])
        freq_list.reverse()
        if len(frequency_alphabet) == 26:
            convert = {}
            pecf = frq_to_percent(letterqs)
            for i in list(letterqs.keys())[:]:
                rel_chance = pecf[i]
                vlike = ["?",100]
                likely = []
                possible = []
                for z in alphabet:
                    dif = inside(rel_chance,expected_letter_freq[z],sd[z])
                    if dif < vlike[1]:
                        vlike = [str(z),dif]
                    elif dif < 1.5:
                        likely.append(z)
                    elif dif < 5:
                        possible.append(z)
                convert[i] = (vlike,likely,possible)
            pad_val = len(str(freq_list[0][1]))
            if sub_freq_ei_var.get():
                for letter in freq_list:
                    new_text = str(letter[0]).upper() + ": " + pad_to_y(str(letter[1]),pad_val) + " Likely:" + convert[letter[0]][0][0].upper() + " (" + str(round(convert[letter[0]][0][1],1)) + (") ["+",".join(convert[letter[0]][1])+"||"+",".join(convert[letter[0]][2])).replace("[||","[")+"]\n"
                    if len(new_text) > 43:
                        new_text = new_text[:39] + "…]\n"
                    text += new_text
            else:
                for letter in freq_list:
                    new_text = str(letter[0]).upper() + ": " + pad_to_y(str(letter[1]),pad_val) + " Likely:" + convert[letter[0]][0][0].upper() + " (" + str(round(convert[letter[0]][0][1],1)) + ") ["+",".join(convert[letter[0]][1])+"]\n"
                    if len(new_text) > 43:
                        new_text = new_text[:39] + "…]\n"
                    text += new_text
        else:
            for letter in freq_list:
                text += str(letter[0]) + ": " + str(letter[1]) + "\n"
            

        sub_freq_label.config(text = text)
        sub_freq_old_message = text.replace(" ","")
    if which == "vin-len":
        message = message_box.get(0.0,END)
        message = message.lower().replace("\n","").replace(" ","")
        global vin_old_text
        if message == vin_old_text or len(message) < 5:
            return None
        print("run")
        vin_old_text = message
        data = {}
        datas = []
        for i in range(1,21):
            cons = coinc(message,i)
            data[i] = cons
            datas.append(cons)
        vin_len_con_box.update(data)
        optimal_len = {}
        
        for trylen in range(2,11):
            nth = datas[trylen-1::trylen]
            nnth = datas[:]
            for i in nth:
                nnth.remove(i)
            optimal_len[round(mean(nth)/((mean(nnth)+1)*(1.01**trylen)),5)] = trylen
        vin_len_conlabel.config(text="Predicted length: "+str(optimal_len[max(optimal_len.keys())]))
            
        
        

#actives - btns
active_button_section_sub = Frame(active_info_area)
active_button_section_sub.grid(row=1,column=0,sticky="nsew")
active_button_section_cea = Frame(active_info_area)
active_button_section_vin = Frame(active_info_area)
sub_dic_btn = Button(active_button_section_sub,text="Dictionary",bg="#767698",command=lambda *e: active_btn_clicked("sub-dict"))
sub_dic_btn.grid(row=0,column=0,sticky="nsew")
sub_freq_btn = Button(active_button_section_sub,text="Frequency",bg="#767698",command=lambda *e: active_btn_clicked("sub-freq"))
sub_freq_btn.grid(row=0,column=1,sticky="nsew")
cea_pred_btn = Button(active_button_section_cea,text="Predition",bg="#767698",command=lambda *e: active_btn_clicked("cea-pred"))
cea_pred_btn.grid(row=0,column=0,sticky="nsew")
vin_len_btn = Button(active_button_section_vin,text="Length",bg="#767698",command=lambda *e: active_btn_clicked("vin-len"))
vin_len_btn.grid(row=0,column=0,sticky="nsew")
vin_tool_btn = Button(active_button_section_vin,text="Tools",bg="#767698",command=lambda *e: active_btn_clicked("vin-tool"))
vin_tool_btn.grid(row=0,column=1,sticky="nsew")
vin_tool_btn = Button(active_button_section_vin,text="Theorum",bg="#767698",command=lambda *e: active_btn_clicked("vin-the"))
vin_tool_btn.grid(row=0,column=2,sticky="nsew")
#actives - data
active_data_frame = Frame(active_info_area,width=300,height=642)
active_data_frame.grid(row=2,column=0,columnspan=10)
active_data_frame.grid_propagate(False)

sub_dict_frame = Frame(active_data_frame)
sub_freq_frame = Frame(active_data_frame)
sub_poss_frame = Frame(active_data_frame)
cea_pred_frame = Frame(active_data_frame)
vin_len_frame = Frame(active_data_frame)
vin_tool_frame = Frame(active_data_frame)
vin_the_frame = Frame(active_data_frame)
sub_dict_frame.grid()
current_active = sub_dict_frame
current_active_name = "sub-dict"

cea_pred_label = Label(cea_pred_frame,text="test-cea-pred",justify=LEFT)
cea_pred_label.grid()
sub_freq_btn_alpha = Button(sub_freq_frame,text="Set alphabet",width=41,fg="#5555ff",bg="#0000aa",anchor="center",command=lambda *e: freq_set_alpha())
sub_freq_btn_alpha.grid(row=0,columnspan=3,column=0,sticky="nsew")
sub_freq_ei_frame = Frame(sub_freq_frame,relief=RIDGE,bd=1)
sub_freq_ei_frame.grid(row=1,columnspan=3,column=0,sticky="nsew")
Label(sub_freq_ei_frame,text="Extended info:").grid(row=1,column=0,sticky="nes")
sub_freq_ei_var = IntVar(sub_freq_frame)
sub_freq_ei_var.set(0)
sub_freq_ei_w = Checkbutton(sub_freq_ei_frame,variable=sub_freq_ei_var)
sub_freq_ei_w.grid(row=1,column=1,sticky="nws")
sub_freq_ei_var.trace("w",lambda *e: sub_freq_ei_func())
sub_freq_label = Label(sub_freq_frame,text="test-sub-freq",justify=LEFT,anchor="nw",font="Courier 9")
sub_freq_label.grid(row=2,column=0,columnspan=2)
vin_len_label = Label(vin_len_frame,text="Coincidences",justify=CENTER,anchor="n")
vin_len_label.grid(row=0,column=0)
for i in range(1,21):
    vin_len_con_box(vin_len_frame,i)
vin_len_conlabel = Label(vin_len_frame,text="Predicted length:?",justify=CENTER,anchor="n")
vin_len_conlabel.grid(row=21,column=0)

vin_tool_label = Label(vin_tool_frame,text="Required shift",justify=CENTER,anchor="n")
vin_tool_label.grid(row=0,column=0)
vin_tool_rshiftf = Frame(vin_tool_frame)
vin_tool_rshiftf.grid(row=1,column=0)

vin_the_calb = Button(vin_the_frame,command=Theorum,text="calculate",bg="#0066ff",fg="#22ffff")
vin_the_calb.grid(row=0,column=0)
vin_the_outl = Label(vin_the_frame,text="???")
vin_the_calb.grid(row=1,column=0)





def _vin_update_rshift():
    encr = _vin_tool_encr_var.get().lower()
    becomes = _vin_tool_becomes_var.get().lower()
    if encr == "" or becomes == "":
        return True
    keyindex = alphabet.index(encr) - alphabet.index(becomes)
    keyvalue = alphabet[keyindex]
    vin_tool_rshiftout.config(text="Requires:"+str(keyvalue.upper())+" ("+str(keyindex)+")")
    

def check_input_and_call_update(this,var):
    data = var.get().lower()
    if len(data) >= 2:
        data = data[-1]
        var.set(data)
    var.set(data.upper())
    if not data in alphabet:
        data = ""
        var.set("")
    _vin_update_rshift()

_vin_tool_encr_var = StringVar(vin_tool_rshiftf)
_vin_tool_becomes_var = StringVar(vin_tool_rshiftf)
_vin_tool_encr_var.trace("w",lambda *e: check_input_and_call_update(vin_tool_encr,_vin_tool_encr_var))
_vin_tool_becomes_var.trace("w",lambda *e: check_input_and_call_update(vin_tool_becomes,_vin_tool_becomes_var))


vin_tool_encr = Entry(vin_tool_rshiftf,width=2,justify='center',textvariable=_vin_tool_encr_var)
vin_tool_becomes = Entry(vin_tool_rshiftf,width=2,justify='center',textvariable=_vin_tool_becomes_var)
Label(vin_tool_rshiftf,text="   ").grid(row=0,column=0)
vin_tool_encr.grid(row=0,column=1)
Label(vin_tool_rshiftf,text="->").grid(row=0,column=2)
vin_tool_becomes.grid(row=0,column=3)
vin_tool_rshiftout = Label(vin_tool_rshiftf,anchor="w",text="Requires:?")
vin_tool_rshiftout.grid(row=0,column=4)


#types
current_key = letter_frame
current_btns = active_button_section_sub




class letter_set:

    conv = {}
    letters = {}

    def __init__(self,master,letter):
        self.dup = False
        self.letter = letter.lower()
        self._y = len(letter_set.letters)
        letter_set.letters[self.letter] = self
        self._var = StringVar(master)
        self._var.trace("w",lambda *e: self.letter_changed())
        Label(master,text=str(letter)).grid(row=self._y,column=0,pady=1)
        Label(master,text="= ").grid(row=self._y,column=1,pady=1)
        self.ent = Entry(master,width=2,justify='center',textvariable=self._var)
        self.ent.grid(row=self._y,column=2,pady=1)
        self.ent.bind("<FocusIn>",lambda *e: self.get_focus())
        self.ent.bind("<FocusOut>",lambda *e: self.lose_focus())
        self.set = False
        self.ent.bind("<Shift-Button-1>",lambda *e: self.toggle_setness())

    def toggle_setness(self):
        if self.set:
            self.set = False
        else:
            self.set = True
        self.update_own_graf()
        Global_update()


    def update_own_graf(self):
        if self.set:
            if self.dup:
                self.ent.config(relief=FLAT,state=DISABLED,disabledbackground="#deb999")
            else:
                self.ent.config(relief=FLAT,state=DISABLED,disabledbackground="#eeeeee")
        else:
            if self.dup:
                self.ent.config(relief=SUNKEN,state=NORMAL,bg="#ff8800")
            else:
                self.ent.config(relief=SUNKEN,state=NORMAL,bg="#ffffff")

    def get_focus(self): 
        cont = self.ent.get().lower()
        if cont == "":
            return self.lose_focus()
        output_box.tag_remove("highlight_letter",0.0,END)

        found_indexes = []
        box_dicon = output_box.get(0.0,END)[:-1]
        box_cont = box_dicon.split("\n")
        for line in range(1,len(box_cont)+1):
            for char in range(0,len(box_cont[line-1])):
                if box_cont[line-1][char] == cont:
                    found_indexes.append(str(line)+"."+str(char))
        
        for indexsel in found_indexes:
            if "Known" in output_box.tag_names(indexsel):
                output_box.tag_add("highlight_letter",indexsel,indexsel+" + 1 chars")
        
        
        

    def lose_focus(self):
        output_box.tag_remove("highlight_letter",0.0,END)
        

    def letter_changed(self):
        data = self._var.get().lower()
        if len(data) >= 2:
            data = data[-1]
            self._var.set(data)
        self._var.set(data.upper())
        if data in alphabet or data == "":
            self.ent.config(fg="black",bg="#ffffff")
        else:
            self.ent.config(fg="#ff6600",bg="#ffffff")
        if data == "":
            del(letter_set.conv[self.letter])
        else:
            letter_set.conv[self.letter] = data
        letter_set.find_inp_letters(self)
        Pre_Global_update()
        self.get_focus()

    def find_inp_letters(caller=None):
        letters = list(letter_set.conv.values())[:]
        for letter in list(letter_set.letters.values())[:]:
            letter.dup = False
            letter.update_own_graf()
        if len(letters) != len(set(letters)):
            bad = []
            for i in set(letters):
                if letters.count(i) >= 2:
                    bad.append(i)
            for i in list(letter_set.conv.keys())[:]:
                if letter_set.conv[i] in bad:
                    letter_set.letters[i].dup = True
                    letter_set.letters[i].update_own_graf()
                

for letter in alphabet:
    letter_set(letter_frame,letter.upper())

def cea_key_changed():
    global Data_form_cea
    if Data_form_cea == "normal":
        data = cea_key.get()
        if len(data) >= 3:
            data = data[-2:]
            cea_key.set(data)
        try:
            data = int(data)
            if data > 26:
                cea_ent.config(fg="#ff6600")
            else:
                cea_ent.config(fg="black")
        except:
            cea_ent.config(fg="#ff0000")
        Pre_Global_update()
    else:
        cea_ent.config(fg="#989898")

def cea_ent_focused():
    global Data_form_cea
    if Data_form_cea == "predictive":
        cea_key.set("")
        Data_form_cea = "normal"

cea_key = StringVar(cea_frame)
cea_key.trace("w",lambda *e: cea_key_changed())
Label(cea_frame,text="key").grid(row=1,column=0,pady=1)
Label(cea_frame,text="= ").grid(row=1,column=1,pady=1)
cea_ent = Entry(cea_frame,width=3,justify='center',textvariable=cea_key)
cea_ent.grid(row=1,column=2,pady=1)
cea_ent.bind("<FocusIn>",lambda *e: cea_ent_focused())

def vin_len_set():
    vin_letter_set.update_visible()

vin_length = IntVar(vin_frame)
vin_length_drop = OptionMenu(vin_frame,vin_length,2,3,4,5,6,7,8,9,10,11,12,13,14,15)
vin_length_drop.config(width=1)
vin_length_drop.grid(row=1,column=0,columnspan=3)
vin_length.set(3)
vin_length.trace("w",lambda *e: vin_len_set())

class vin_letter_set:

    letters = {}
    key = ""

    def __init__(self,master,number):
        self.number = number
        self.master = master
        self.labn = Label(master,text=str(number))
        self.labe = Label(master,text="= ")
        self._var = StringVar(master)
        self._var.trace("w",lambda *e: self.letter_changed())
        self.ent = Entry(master,width=2,justify='center',textvariable=self._var)
        vin_letter_set.letters[number] = self
        self.ent.bind("<FocusIn>",lambda *e: self.get_focus())
        self.ent.bind("<FocusOut>",lambda *e: self.lose_focus())
        

    def letter_changed(self):#key must be alpha
        data = self._var.get().lower()
        if len(data) >= 2:
            data = data[-1]
            self._var.set(data)
        if data in alphabet or data == "" or data == "*":
            self.ent.config(fg="black",bg="#ffffff")
        else:
            data = ""
        self._var.set(data)

        
        vin_letter_set.update_key()
        Pre_Global_update()
        self.get_focus()

    def update_key():
        key = ""
        for i in range(1,vin_length.get()+1):
            val = vin_letter_set.letters[i]._var.get()
            if val == "":
                val = "*"
            key += val
        vin_letter_set.key = key.lower()

    def show(self):
        self.labn.grid(row=self.number+1,column=0,pady=1)
        self.labe.grid(row=self.number+1,column=1,pady=1)
        self.ent.grid(row=self.number+1,column=2,pady=1)

    def hide(self):
        self.labn.grid_forget()
        self.labe.grid_forget()
        self.ent.grid_forget()

    def update_visible():
        limit = vin_length.get()
        for i in list(vin_letter_set.letters.values()):
            i.hide()
        for i in range(1,limit+1):
            vin_letter_set.letters[i].show()

            
    def get_focus(self): 
        box_cont = output_box.get(0.0,END)[:-1]
        for i in range(0,len(box_cont)):
            if (i % len(vin_letter_set.key)) == (self.number-1):
                pass### needs reworking
                #output_box.tag_add("highlight_letter","0.0+"+str(i)+"chars","0.0+"+str(i)+"chars+1chars")
        
        

    def lose_focus(self):
        output_box.tag_remove("highlight_letter",0.0,END)

for n in range(1,16):
    vin_letter_set(vin_frame,n)
vin_letter_set.update_visible()
vin_letter_set.update_key()


def Pre_Global_update():
    print("GU")
    global to_gu,are_guing
    if are_guing:
        to_gu = True
    else:
        are_guing = True
        Global_update()
        are_guing = False
        if to_gu == True:
            to_gu = False
            Pre_Global_update()

def Global_update():
    global message_box
    output_box.config(state=NORMAL)
    output_box.delete(0.0,END)
    message = message_box.get(0.0,END)
    message = message.lower()
    if Ctype == "Caesar cipher":
        if Mode in ("Direct Translation","Replace ?"):
            key = cea_key.get()
            if key == "":
                for letter in message:
                    output_box.insert(END,letter,["Direct Translation"])
            else:
                try:
                    key = int(key)
                    key = key % 26
                    letter_albet = alphabet*2
                    for letter in message:
                        if letter in letter_albet:
                            output_box.insert(END,letter_albet[letter_albet.index(letter)+key],("Known"))
                        else:
                            output_box.insert(END,letter,["Direct Translation"])
                except:
                    pass
        elif Mode == "Predictive Text":
            active_update("cea-pred")
            key = cea_key.get()
            global Data_form_cea,Key_cea
            if key == "":
                if tk.focus_get() == cea_ent:
                    message_box.focus_set()
                Data_form_cea = "predictive"
                key = Key_cea
                cea_key.set(key)
            if Data_form_cea == "normal":
                try:
                    key = int(key)
                    key = key % 26
                    letter_albet = alphabet*2
                    for letter in message:
                        if letter in letter_albet:
                            output_box.insert(END,letter_albet[letter_albet.index(letter)+key],("Known"))
                        else:
                            output_box.insert(END,letter,["Direct Translation"])
                except:
                    pass
            else:
                key = Key_cea
                cea_key.set(key)
                key = int(key)
                letter_albet = alphabet*2
                for letter in message:
                    if letter in letter_albet:
                        output_box.insert(END,letter_albet[letter_albet.index(letter)+key],("Predicted"))
                    else:
                        output_box.insert(END,letter,["Direct Translation"])
            
                
                

    elif Ctype == "Substitution cipher":
        if Mode == "Direct Translation":
            known_trans = list(letter_set.conv.keys())[:]
            for letter in message:
                if letter in known_trans:
                    if letter_set.letters[letter].set:
                        output_box.insert(END,letter_set.conv[letter],("Known","Set"))
                    else:
                        output_box.insert(END,letter_set.conv[letter],("Known"))
                else:
                    output_box.insert(END,letter,["Direct Translation"])
        elif Mode == "Replace ?":
            known_trans = list(letter_set.conv.keys())[:]
            for letter in message:
                if letter in known_trans:
                    output_box.insert(END,letter_set.conv[letter],("Known"))
                elif letter in Unencripted_char or letter == " ":
                    output_box.insert(END,letter,("Known"))
                else:
                    output_box.insert(END,"?",["Wild card"])
    elif Ctype == "Vigenere cipher":
        if Mode == "Direct Translation":
            key = vin_letter_set.key
            effective_letter_count = 0
            for letter in message:
                if letter in alphabet:
                    key_letter = key[effective_letter_count%len(key)]
                    effective_letter_count += 1
                    if key_letter == "*":
                        output_box.insert(END,letter,("Direct Translation"))
                    else:
                        conv = alphabet[(   alphabet.index(letter)-alphabet.index(key_letter)   )%26]
                        output_box.insert(END,conv,("Known"))
                    
                else:
                    output_box.insert(END,letter,["Direct Translation"])
            

    if output_box.get(0.0,END)[-2:] == "\n\n":
        output_box.delete(END + "- 1 chars",END)
    
    output_box.config(state=DISABLED)
    global custom_sel_region
    if len(custom_sel_region) == 2:
        output_box.tag_add("custom_sel",*custom_sel_region)
    active_update()

#post init

type_changed()
tk.update()
tk.update_idletasks()



#temp

#message_box.insert(0.0,"AOL ZPNUZ DLYL ZBIASL, HUK PA AVVR TL H DOPSL AV ZWVA AOLT, IBA NYHKBHSSF P ZAHYALK AV THRL AOLT VBA, HUK SPRL VUL VM AOVZL VSK MHZOPVULK 3K WPJABYLZ, AOHA ZWYPUNZ PUAV MVJBZ DOLU FVB JYVZZ FVBY LFLZ HUK JVBUA AV H OBUKYLK, AOL AYBAO JYFZAHSSPZLK HUK P YLHSPZLK AOHA P OHK ILLU ZLHYJOPUN MVY PA HSS HSVUN. PA DHZU’A AOHA P MVBUK ZVTLAOPUN WHYAPJBSHY. DOHA P UVAPJLK DHZ HJABHSSF HU HIZLUJL, H DOVSL JVSSLJAPVU VM HWWHYLUASF BUYLSHALK AOPUNZ AOHA ZOVBSK OHCL LEPZALK IBA KPKU’A. HUK QBZA HZ P OHK MPNBYLK AOHA VBA, ZVTLVUL, HUK IHJR AOLU P KPKU’A RUVD DOV, DYVAL AV ALSS TL HIVBA PA. AOLF VICPVBZSF OHK H ZLUZL VM AOL KYHTHAPJ, HUK HU LEJLSSLUA ZLUZL VM APTPUN. PM AOLF OHK ZLUA PA AV TL LCLU H MLD KHFZ ILMVYL P DVBSK OHCL HZZBTLK PA DHZ ZVTL RPUK VM JYHGF HKCLYAPZPUN ZABUA, IBA DOLU AOL WVZAJHYK HYYPCLK, PA DHZ PTTLKPHALSF VICPVBZ AV TL DOHA PA YLMLYYLK AV. PA JHYYPLK QBZA AOYLL DVYKZ, HUK PA KLZJYPILK WLYMLJASF AOL TPZZPUN WPLJLZ PU TF WBGGSL. PA QBZA ZHPK: AOL ZOHKVD HYJOPCL.".replace(" ",""))
#letter_set.letters["a"]._var.set("t")
#letter_set.letters["o"]._var.set("h")
#letter_set.letters["l"]._var.set("e")
#message_box.insert(END,"12!34")

#message_box.insert(0.0,"REPBCGPNYWIJSEUKWUYVISREYRYCGFOQCDSUOENYRGCICKVRRUSKOCCXFORUORCOHRYOLYAFYADKVQRIFKHEYXGRETOWCXXRBMLSXWSRRYAMBOSXHCBGMFIPSRHKQCVMYCPYLELNXYCOCNLCBXMDVWDSGXJGVXPKXCNCLKQGHJPYQRRIPOXPSRGDCGCRRDSMRENZCRRIPONYWIJSEQYJDSGCSWLDQSMLZSKEOVRRELKFPYSKMPMCIRLYRGILOIBDSRBCRYJGXHRRIAYHCLEQOVCPIPBIBDSGXXFOLGNHCXHGKVWORRBCGXXFOQCKRRSQCSLYFIZOILGSPUMLQSLDLCVMQDSDAYCCXGYRQISSKRBTEKOPGKACBIYCOGXKDSVQDAFIHGNQYBXGXPCKZCKGAYVBSREDSFSWDVERWEROLCPPCGXMQILOZYPSPDEJUWUSXFKGMWTYXCAKPJOHASXYNIJVIMEVJYGYVEEORRCEPOQYUMLQILAYGBMCCFSDMRCICWWRRERDLCIEPOXFKXPKVCCXMPXFSRECELOWRKFJSWFOHYBQQWELEJYMXSBIPGMRRQMXIWGSPBMCCWCMSLNAFOVCSWKKVRSRLYALYSLOOLYAQMMRKHCVPCNILIELIOLYAJOHEOSDRMKKRBDLCBIGCRMBIAYVBYJFSQJOETSREDLCMSSXXPILCREQNMQKTNOEPOHRRIKYWRSRRBMEEMLQXFSREPVMWNYWIJSEQVEQDQCCWYQIGCXFOVCPIPORAOXMDLCZHQCCLNMAKXCSLYFIFOEPNVSWSSBWMPXFSWKIWCVJGXAFSXCREJVMRSWYVPTOVWRYQRLSCLYXHGDMQXSROZCXGJOEPSJGDMQKRMPJGMMYVMLSXGKXGFIRRIZSKLOAQPSPXSUSWYLVCKORRVMEKFYRRRIQYGYVPCNWSSGGNILYXCQMTORFYAQWEJVNYWIJSEQYJDSGCGEQDVGXMRIAMXHCBIBGLWCLCREBUINDEZBSIORNBMLDIPSRRRIPORCHXRYXFOAMBOGXKMXIRBMLSXWYTCXIBSXSZELNJMERBKJCGQMNMDSGYDMMXWURMARTMSRROHRRIJKWCBWRBEGQLRKXRRINKTCBMLCXCKHMPXFOHPEQQRIEYXGXXMEGFGMRRXFOPYLELNKMDXFOQRYXYUIYXSRRIPVSMUERDLCVIRDIPDLCIJMERBDLCKXRKGFOHKOWQKKCLYPXIBSRRYXFOTYZIPPMZBIQSXGCMKZSQCMZVIRYWCOAGDLRRILKOCNIWOFSDXFOGFKVPSRECLMGWSZYLNIPRMERTMGIPOHDVYMBSQMSNISTOVRYCMEJMBXFOHCMVWZXGYR")
#Pre_Global_update()

#tk.mainloop()
