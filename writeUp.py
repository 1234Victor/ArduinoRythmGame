import pygame
import time

pygame.init()
wn = pygame.display.set_mode((800, 600))  # 設 wn 為視窗物件，長 800 高 600
drop_before_arrive = 0.8
pixel_per_second = 565 / drop_before_arrive

# Global Vars
running = True  # 操控遊戲迴圈是否繼續的變數
mouse = ""  # 存目前滑鼠的狀態
started = False  # 遊戲還沒開始
start_time = 0  # 遊戲開始時間 (開始後才會有真正的值)
drop_before_arrive = 0.8  # 音符到達判定線前多少秒要出現
pixel_per_second = 565 / drop_before_arrive  # 音符每秒要跑幾單位距離
showing_array = []
pointer = 0
loop_start_time = 0
start_time = 0
time_pass = 0

motion = [[],[]]

# Objects
mayo = pygame.image.load(
    "images\white-arrow-png-transparent-20.png"
).convert_alpha()  # 用來做落下音符的美乃滋圖片
start_menu = pygame.image.load("images\patrick_mayo.jpg").convert_alpha()  # 開始畫面
start_button = pygame.image.load("images\start_button.png").convert_alpha()  # 開始按鈕

mayoleft = pygame.transform.rotate(mayo, 180)  # 將 mayo 旋轉 90 度
mayoright = pygame.transform.rotate(mayo, 0)  # 將 mayo 旋轉 270 度
mayoup = pygame.transform.rotate(mayo, 90)  # 將 mayo 旋轉 0 度
mayodown = pygame.transform.rotate(mayo, 270)  # 將 mayo 旋轉 180 度
mayoleft = pygame.transform.scale(mayoleft, (150, 150))  # 把 mayo 的大小改為 100 * 100
mayoright = pygame.transform.scale(mayoright, (150, 150))  # 把 mayo 的大小改為 100 * 100
mayoup = pygame.transform.scale(mayoup, (150, 150))  # 把 mayo 的大小改為 100 * 100
mayodown = pygame.transform.scale(mayodown, (150, 150))  # 把 mayo 的大小改為 100 * 100
start_menu = pygame.transform.scale(start_menu, (800, 600))
start_button = pygame.transform.scale(start_button, (200, 100))

white_back = pygame.Rect(0, 0, 800, 600)  # (x位置, y位置, x長度, y長度)
border_left_line = pygame.Rect(140, 0, 10, 600)
border_right_line = pygame.Rect(650, 0, 10, 600)
display_pressed1 = pygame.Rect(150, 500, 250, 90)
display_pressed2 = pygame.Rect(400, 500, 250, 90)

music_location = "images\\jilejingtu.mp3"
track = pygame.mixer.music.load(music_location)  # 音樂載入
font = pygame.font.Font("freesansbold.ttf", 32)  # 字型

# Files
times_arrive = []
times_drop = []
notes = []
orientations = []
note_dict = {222: 0, 472: 1}
with open(f"note_and_time\\times_normal.txt", "r") as time_f:
    for i in time_f:
        i = int(i)
        i /= 1090
        i = round(i, 4)
        times_arrive.append(i)

with open(f"note_and_time\\notes_normal.txt", "r") as note_f:
    for i in note_f:
        i = int(i)
        i = note_dict[i]
        notes.append(i)

with open(f"note_and_time\\orientation_normal.txt", "r") as orientation_f:
    for i in orientation_f:
        i = int(i)
        orientations.append(i)

for i in times_arrive:
    i -= drop_before_arrive  # dropping rate
    i = round(i, 2)
    times_drop.append(i)


# Classes
class Note:
    def __init__(self, drop_time, arrive_time, xcor, ycor, block, ori):
        self.drop_time = drop_time
        self.arrive_time = arrive_time
        self.xcor = xcor
        self.ycor = ycor
        self.block = block
        self.hit = False
        self.show = True
        self.orientation = ori

    def ycor_update(self, time_pass):
        p = time_pass - self.drop_time  # 開始墜落後經過的時間。
        # 上面的時間 * 像素每秒 - (目前位置 + 60) = 要增加的座標 (60 是測試出來的緩衝座標)
        self.ycor += pixel_per_second * p - (self.ycor + 60)

    def check_remove(self, time_pass):
        orientation_check = (self.orientation == interpret(motion[self.block]))
        time_check = abs(time_pass - self.arrive_time) <= 0.1
        return orientation_check and time_check


# Functions

def interpret(motion_):
    if motion_ == [0, 0, 0, 0]:
        return -1
    elif motion_ == [1, 0, 0, 0]:
        return 0
    elif motion_ == [0, 1, 0, 0]:
        return 2
    elif motion_ == [0, 0, 1, 0]:
        return 3
    elif motion_ == [0, 0, 0, 1]:
        return 1
    else:
        return -1                                             

def pre_time_handle():
    global loop_start_time
    global start_time
    global time_pass
    loop_start_time = time.time()
    if not started:
        start_time = loop_start_time
    time_pass = float(loop_start_time - start_time)
    time_pass = round(time_pass, 4)


def post_time_handle(loop_start_time):
    now_end_time = time.time()
    now_end_time = round(now_end_time, 4)
    loop_time = now_end_time - loop_start_time
    if loop_time < 0.001:
        time.sleep(0.001 - loop_time)


def pygame_events():
    global running
    global mouse
    for event in pygame.event.get():  # 取得目前的事件
        if event.type == pygame.QUIT:  # 事件為「點下退出鍵」
            running = False  # 結束遊戲迴圈
        if event.type == pygame.MOUSEBUTTONDOWN:  # 事件為「點下滑鼠」
            mouse = "down"
        if event.type != pygame.MOUSEBUTTONDOWN:
            mouse = ""


def draw_back():  # 負責畫遊戲畫面
    pygame.draw.rect(wn, (255, 228, 225), white_back)  # (視窗, 顏色, 矩形物件)
    pygame.draw.rect(wn, (245, 255, 250), border_left_line)
    pygame.draw.rect(wn, (245, 255, 250), border_right_line)
    # 垂直線
    # pygame.draw.line(wn, (255, 255, 255), (275, 0),(275, 600)) # (視窗, 顏色, 起點, 終點)
    pygame.draw.line(wn, (245, 255, 250), (400, 0), (400, 600))
    # pygame.draw.line(wn, (255, 255, 255), (525, 0),(525, 600))
    # 水平線
    pygame.draw.line(wn, (245, 255, 250), (150, 500), (650, 500))
    pygame.draw.line(wn, (245, 255, 250), (150, 590), (650, 590))


def background_display(mouse_pos):  # 負責處理背景繪製
    global started
    global start_time
    if started:
        draw_back()
    else:
        wn.blit(start_menu, (0, 0))
        wn.blit(start_button, (370, 70))
        if mouse == "down":
            if (
                mouse_pos[0] > 300
                and mouse_pos[0] < 500
                and mouse_pos[1] > 100
                and mouse_pos[1] < 400
            ):
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play()
                started = True
                start_time = time.time()


def draw_press():  # 負責畫按鈕回饋 (就是玩家按下鍵盤後給顯示)
    if keys[pygame.K_f]:
        display2()
    if keys[pygame.K_j]:
        pygame.draw.rect(wn, (245, 255, 250), display_pressed2)
    

def showingArray_appending(time_pass):
    global showing_array
    global pointer
    coresponding_location = [222, 472]  # xcor 定位用
    while pointer < len(times_drop) and abs(time_pass - times_drop[pointer]) <= 0.1:
        # Note(drop_time, arrive_time, xcor, ycor, block)
        one_note = Note(
            times_drop[pointer],
            times_arrive[pointer],
            coresponding_location[notes[pointer]],
            -100,
            notes[pointer],
            orientations[pointer],
        )
        showing_array.append(one_note)
        pointer += 1


def note_displaying(time_pass):
    global showing_array
    #print(orientations)
    for one_note in showing_array:
        if one_note.show:
            print(one_note.orientation)
            one_note.ycor_update(time_pass)
            if one_note.orientation == 0:
                wn.blit(mayoup, (one_note.xcor, one_note.ycor))
            elif one_note.orientation == 1:
                wn.blit(mayoright, (one_note.xcor, one_note.ycor))
            elif one_note.orientation == 2:
                wn.blit(mayodown, (one_note.xcor, one_note.ycor))
            elif one_note.orientation == 3:
                wn.blit(mayoleft, (one_note.xcor, one_note.ycor))
        if one_note.ycor >= 900:
            one_note.show = False


def note_remove(time_pass):
    for one_note in showing_array:
        if one_note.check_remove(time_pass):
            if(one_note.block == 0):
                pygame.draw.rect(wn, (245, 255, 250), display_pressed1)
            else:
                pygame.draw.rect(wn, (245, 255, 250), display_pressed2)
            one_note.hit = True
            one_note.show = False




def combo_showing():
    # count combo
    combo = 0
    point = 0
    note_died_count = 0  # 已經有幾個不再顯示
    for one_note in showing_array:
        if one_note.arrive_time < time_pass:  # 判斷不再顯示的條件
            note_died_count += 1

    for i in range(
        note_died_count
    ):  # 在這些不顯示的音符裡面，有被打到 combo 就加一，否則歸零
        if showing_array[i].hit:
            combo += 1
            point += 1
        else:
            combo = 0

    # show combo
    combo_show = font.render(f"COMBO: {combo}", True, (112,128,144))
    #            ^(顯示的字, 是否用滑順字體, 顏色)
    wn.blit(combo_show, (10, 10))

    point_show = font.render(f"POINT: {point}", True, (112,128,144))
    #            ^(顯示的字, 是否用滑順字體, 顏色)
    wn.blit(point_show, (600, 10))

def pull_keys():
    global motion
    if keys[pygame.K_w]:
        motion[0] = [1, 0, 0, 0]
    elif keys[pygame.K_s]:
        motion[0] = [0, 1, 0, 0]
    elif keys[pygame.K_d]:
        motion[0] = [0, 0, 0, 1]
    elif keys[pygame.K_a]:
        motion[0] = [0, 0, 1, 0]
    else:
        motion[0] = [0, 0, 0, 0]
    
    if keys[pygame.K_UP]:
        motion[1] = [1, 0, 0, 0]
    elif keys[pygame.K_DOWN]:
        motion[1] = [0, 1, 0, 0]
    elif keys[pygame.K_RIGHT]:
        motion[1] = [0, 0, 0, 1]
    elif keys[pygame.K_LEFT]:
        motion[1] = [0, 0, 1, 0]
    else:
        motion[1] = [0, 0, 0, 0]

# Game Loop
while running:
    pre_time_handle()

    mouse_pos = pygame.mouse.get_pos()  # 取得滑鼠座標
    keys = pygame.key.get_pressed()  # 取得有哪些鍵盤上的按鍵被按下
    pull_keys()
    pygame_events()
    background_display(mouse_pos)
    showingArray_appending(time_pass)
    note_displaying(time_pass)
    note_remove(time_pass)
    draw_press()
    combo_showing()
    pygame.display.update()  # 更新視窗
    post_time_handle(loop_start_time)
pygame.quit()



