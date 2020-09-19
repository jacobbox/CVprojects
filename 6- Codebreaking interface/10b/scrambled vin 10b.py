alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

convert ={
    1:{"c":"b","a":"g","l":"k","y":"x","n":"m","b":"w","v":"u","x":"v","a":"h","u":"t","i":"g","w":"o","q":"p","g":"f","z":"y","d":"a","f":"e","e":"c","t":"r","p":"n","h":"s","m":"l","o":"d","j":"i"},
    2:{"m":"x","g":"q","w":"k","a":"g","c":"m","r":"h","x":"w","t":"a","q":"s","z":"c","j":"t","v":"o","b":"l","f":"p","i":"r","u":"d","y":"b","e":"n","s":"e","k":"u","n":"y","k":"u","d":"i","l":"v","j":"t","h":"f"},
    3:{"n":"k","s":"x","z":"v","f":"b","y":"u","j":"f","d":"s","v":"r","q":"m","h":"y","k":"g","o":"h","c":"o","x":"t","i":"e","l":"i","m":"j","w":"a","g":"c","t":"p","e":"w","r":"n","p":"l","b":"d","c":"o","o":"h","h":"y"},
    4:{"u":"k","w":"x","l":"b","v":"l","s":"q","d":"u","q":"g","o":"v","b":"y","m":"c","i":"d","y":"n","x":"m","k":"w","f":"h","h":"r","a":"t","j":"o","n":"e","r":"i","p":"f","g":"a","y":"n","z":"p","e":"s"},
    5:{"v":"k","m":"b","l":"w","b":"x","u":"j","s":"p","g":"h","r":"g","n":"c","w":"v","x":"l","q":"f","d":"t","p":"e","c":"y","f":"s","o":"u","t":"i","i":"a","y":"m","z":"n","j":"d","k":"o","a":"r"},
    6:{"r":"x","f":"k","k":"p","p":"u","e":"j","a":"b","w":"f","g":"l","t":"y","l":"q","z":"d","h":"w","j":"n","s":"o","x":"h","m":"r","q":"v","d":"c","c":"i","v":"s","i":"m","b":"g","y":"a","b":"g","o":"e","n":"t","n":"t"},
    0:{"a":"x","q":"k","g":"w","d":"y","r":"l","h":"v","e":"d","l":"f","m":"g","j":"c","f":"o","i":"b","k":"e","u":"n","v":"p","b":"h","z":"t","t":"m","n":"i","y":"r","c":"a","w":"s","s":"u"},
    }
#convert = {0:{},1:{},2:{},3:{},4:{},5:{},6:{},}

from tkinter import *
tk = Tk()
text = Text(tk,width=100,height=40,background="#000000",foreground="#ffffff")
text.tag_configure("sub1",foreground="#0000ff")
text.tag_configure("sub2",foreground="#00ff00")
text.tag_configure("sub3",foreground="#ffff00")
text.tag_configure("sub4",foreground="#ff8800")
text.tag_configure("sub5",foreground="#ff00ff")
text.tag_configure("sub6",foreground="#ff0000")
text.tag_configure("sub0",foreground="#8800ff")
text.tag_configure("conv",background="#aaaaaa")
text.pack()

message = open("mess.txt").read().lower()

count = 1
for letter in message:
    if letter in alphabet:
        if letter in convert[count].keys():
            text.insert(END,convert[count][letter],["sub"+str(count),"conv"])
            count = (count + 1) % 7
        else:
            text.insert(END,letter,["sub"+str(count)])
            count = (count + 1) % 7
    else:
        text.insert(END,letter)
