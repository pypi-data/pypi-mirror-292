from colorama import Fore, Back, Style
import os
import keyboard
import time
import cursor

def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
        
def spaces(word):
    n = 0 + len(word)
    chars = []
    for i in range(n):
        chars.append(" ")
    space = "".join(chars)
    return space

class Menu:
    def __init__(self, title, options, show_cursor=False):
        self.title = title
        self.options = options
        self.selected_idd = 0
        self.max_idd = len(options)-1
        self.show_cursor = show_cursor
        self.title_color = Fore.WHITE
        self.selected_fore_color = Fore.BLACK
        self.selected_back_color = Back.WHITE
        self.selector_left_color = Fore.WHITE
        self.selector_right_color = Fore.WHITE
        self.selector_left = ">"
        self.selector_right = "<"

        if self.show_cursor == False:
            cursor.hide()
            clear()
        else:
            clear()
            
    def change_color(self, title_color, selected_fore_color, selected_back_color, selector_left_color, selector_right_color):
        self.title_color = title_color
        self.fore_color = selected_fore_color
        self.back_color = selected_back_color
        self.selector_right_color = selector_right_color
        self.selector_left_color = selector_left_color
        
    def change_selector(self, selector_left, selector_right):
        self.selector_left = selector_left
        self.selector_right = selector_right
    
    def show(self):
        print(self.title_color, self.title, '\n')
        
        for idd,name,func in self.options:
            if self.selected_idd == idd:
                print(self.selector_left_color + self.selector_left + self.selected_fore_color, self.selected_back_color+name+Style.RESET_ALL + self.selector_right_color,  self.selector_right, Style.RESET_ALL)


            else:
                print(spaces(self.selector_left)+Fore.RESET+Back.RESET, name, Style.RESET_ALL, spaces(self.selector_right))

    

    def reload(self):
        while True:
            if keyboard.is_pressed("down"):
                if self.selected_idd == self.max_idd:
                    self.selected_idd = 0
                else:
                    self.selected_idd += 1
                clear()
                self.show()
                time.sleep(0.2)
                
            elif keyboard.is_pressed("up"):
                if self.selected_idd == 0:
                    self.selected_idd = self.max_idd
                else:
                    self.selected_idd -= 1
                clear()
                self.show()
                time.sleep(0.2)
            
            elif keyboard.is_pressed('space'):
                clear()
                self.options[self.selected_idd][2]()
                time.sleep(0.5)
                break
            
    
    def open(self):
        self.show()
        self.reload()
        cursor.show()


##############################################################################################

# def a1():
#     print("ok1")
# def a2():
#     print("ok2")
# def a3():
#     print("ok3")
        
# options = [(0,"test1",a1), (1,"test2",a2), (2,"test3",a3)]

# menu = Menu("MAIN MENU TEST", options, False)
# menu.change_color(Fore.YELLOW, Fore.RED, Back.BLUE, Fore.GREEN, Fore.MAGENTA)
# menu.change_selector("*", "*")
# menu.open()