import os, math, asyncio, pygame

W, H, FPS, WORLD = 960, 540, 60, 2500
MENU, PLAY, PAUSE, WIN, LOSE = "menu", "play", "pause", "win", "lose"
WHITE=(245,248,255); BLACK=(12,14,28); NAVY=(20,30,68); BLUE=(50,135,245); CYAN=(65,225,255)
PURPLE=(115,72,215); LPURPLE=(178,128,255); YELLOW=(255,214,75); ORANGE=(255,145,48)
RED=(236,68,82); GREEN=(65,203,112); LGREEN=(145,238,142); BROWN=(112,72,48); GRAY=(105,112,140)
SKIN=(255,215,194); HAIR=(78,47,36); SHADOW=(28,30,48)
GRAVITY=.75

pygame.init()

SCREEN = pygame.display.set_mode((W, H))
pygame.display.set_caption("Aventura dos Cristais")
CLOCK = pygame.time.Clock()

F16 = pygame.font.Font(None, 22)
F18 = pygame.font.Font(None, 26)
F22 = pygame.font.Font(None, 32)
F34 = pygame.font.Font(None, 46)
F50 = pygame.font.Font(None, 66)

# Som desativado temporariamente na versão web
# para evitar travamento ao abrir no celular/tablet.
def play_sound(name):
    pass

def txt(s,msg,font,color,x,y,center=False):
    im=font.render(msg,True,color); r=im.get_rect(); r.center=(x,y) if center else r.center; r.topleft=(x,y) if not center else r.topleft; s.blit(im,r); return r

def panel(s,r,fill=(22,31,69),border=LPURPLE,alpha=238,rad=22):
    q=pygame.Surface((r.w,r.h),pygame.SRCALPHA); pygame.draw.rect(q,(*fill,alpha),q.get_rect(),border_radius=rad)
    pygame.draw.rect(q,border,q.get_rect(),3,border_radius=rad); s.blit(q,r.topleft)

def button(s,r,label,color,active=False,font=F18):
    c=tuple(min(255,v+(25 if active else 0)) for v in color); q=pygame.Surface((r.w,r.h),pygame.SRCALPHA)
    pygame.draw.rect(q,(*c,225),q.get_rect(),border_radius=18); pygame.draw.rect(q,(255,255,255,220),q.get_rect(),3,border_radius=18)
    s.blit(q,r.topleft); txt(s,label,font,WHITE,r.centerx,r.centery,True)

def gradient(s,a,b):
    for y in range(H):
        t=y/H; c=tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3)); pygame.draw.line(s,c,(0,y),(W,y))

def cloud(s,x,y,k=1):
    c=(245,250,255); pygame.draw.ellipse(s,c,(x,y+10*k,70*k,26*k)); pygame.draw.circle(s,c,(int(x+18*k),int(y+14*k)),int(18*k)); pygame.draw.circle(s,c,(int(x+40*k),int(y+9*k)),int(22*k))

def background(s,cam,f):
    gradient(s,f["sky1"],f["sky2"])
    for i in range(24): pygame.draw.circle(s,f["spark"],(((i*173-int(cam*.08))%(W+80))-40,30+(i*53)%220),1+i%3)
    pygame.draw.circle(s,f["sun"],(830,78),42)
    for off in range(-600,1800,420):
        x=off-int(cam*.12); pygame.draw.polygon(s,f["far"],[(x,420),(x+160,190),(x+330,420)])
    for off in range(-400,1900,360):
        x=off-int(cam*.22); pygame.draw.polygon(s,f["near"],[(x,455),(x+130,250),(x+290,455)])
    cloud(s,100-int(cam*.05),80,1); cloud(s,520-int(cam*.04),120,.8); cloud(s,780-int(cam*.07),45,.65)

class Player:
    def __init__(self,x=70,y=330):
        self.r=pygame.Rect(x,y,40,62); self.vx=0; self.vy=0; self.speed=5; self.jump=-15; self.ground=False
        self.life=3; self.face=1; self.inv=0; self.atk_cd=0; self.atk_time=0; self.atk=pygame.Rect(0,0,0,0)
    def respawn(self): self.r.x,self.r.y,self.vx,self.vy,self.inv=70,330,0,0,75
    def update(self,keys,plats,back=False,front=False,jump=False,attack=False):
        self.vx=0; back=back or keys[pygame.K_a] or keys[pygame.K_LEFT]; front=front or keys[pygame.K_d] or keys[pygame.K_RIGHT]
        jump=jump or keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]; attack=attack or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL] or keys[pygame.K_f]
        if back: self.vx=-self.speed; self.face=-1
        if front: self.vx=self.speed; self.face=1
        if jump and self.ground: self.vy=self.jump; self.ground=False; play_sound("pulo")
        if attack and self.atk_cd<=0: self.atk_cd=24; self.atk_time=11; play_sound("ataque")
        self.atk_cd=max(0,self.atk_cd-1); self.atk_time=max(0,self.atk_time-1); self.inv=max(0,self.inv-1)
        self.r.x+=self.vx
        for p in plats:
            if self.r.colliderect(p): self.r.right=p.left if self.vx>0 else self.r.right; self.r.left=p.right if self.vx<0 else self.r.left
        self.vy=min(18,self.vy+GRAVITY); self.r.y+=int(self.vy); self.ground=False
        for p in plats:
            if self.r.colliderect(p):
                if self.vy>0: self.r.bottom=p.top; self.vy=0; self.ground=True
                elif self.vy<0: self.r.top=p.bottom; self.vy=0
        if self.r.left<0:self.r.left=0
        if self.r.right>WORLD:self.r.right=WORLD
        if self.atk_time>0: self.atk=pygame.Rect(self.r.right-1 if self.face>0 else self.r.left-51,self.r.y+19,52,20)
        else:self.atk=pygame.Rect(0,0,0,0)
    def hurt(self):
        if self.inv<=0: self.life-=1; self.inv=90; self.vy=-8; play_sound("dano")
    def draw(self,s,cam):
        if self.inv>0 and (self.inv//6)%2==0:return
        x,y=self.r.x-cam,self.r.y; pygame.draw.ellipse(s,SHADOW,(x+5,y+55,32,7)); pygame.draw.circle(s,SKIN,(x+20,y+15),13)
        pygame.draw.arc(s,HAIR,(x+6,y+1,29,23),math.pi,math.pi*2.1,7); pygame.draw.circle(s,BLACK,(x+16,y+14),2); pygame.draw.circle(s,BLACK,(x+24,y+14),2)
        pygame.draw.rect(s,PURPLE,(x+7,y+26,26,25),border_radius=8); pygame.draw.rect(s,CYAN,(x+11,y+31,18,8),border_radius=4); pygame.draw.line(s,WHITE,(x+20,y+28),(x+20,y+49),2)
        pygame.draw.line(s,SKIN,(x+8,y+31),(x+2,y+41),4); pygame.draw.line(s,SKIN,(x+32,y+31),(x+38,y+41),4)
        pygame.draw.line(s,NAVY,(x+14,y+50),(x+12,y+61),5); pygame.draw.line(s,NAVY,(x+26,y+50),(x+28,y+61),5)
        if self.atk_time>0:
            a=self.atk.move(-cam,0)
            if self.face>0: pygame.draw.polygon(s,(225,232,245),[(a.left+8,a.centery),(a.right,a.top+2),(a.right-4,a.bottom-2)]); pygame.draw.rect(s,BROWN,(a.left,a.centery-4,15,8),border_radius=3)
            else: pygame.draw.polygon(s,(225,232,245),[(a.right-8,a.centery),(a.left,a.top+2),(a.left+4,a.bottom-2)]); pygame.draw.rect(s,BROWN,(a.right-15,a.centery-4,15,8),border_radius=3)

class Enemy:
    def __init__(self,x,y,kind="slime"):
        self.kind=kind; self.r=pygame.Rect(x,y,44,36 if kind=="slime" else 34); self.y0=y; self.left=x-100; self.right=x+100; self.v=2.0 if kind!="ghost" else 2.4; self.dir=1; self.alive=True; self.t=0
    def update(self):
        if not self.alive:return
        self.t+=1; self.r.x+=int(self.v*self.dir)
        if self.r.x<=self.left:self.dir=1
        if self.r.x>=self.right:self.dir=-1
        if self.kind=="bat":self.r.y=self.y0+int(math.sin(self.t*.08)*26)
        if self.kind=="ghost":self.r.y=self.y0+int(math.sin(self.t*.05)*18)
    def draw(self,s,cam):
        if not self.alive:return
        x,y=self.r.x-cam,self.r.y
        if self.kind=="slime":
            pygame.draw.ellipse(s,LGREEN,(x,y+4,44,30)); pygame.draw.ellipse(s,GREEN,(x+2,y+15,40,18)); pygame.draw.circle(s,BLACK,(x+14,y+16),3); pygame.draw.circle(s,BLACK,(x+30,y+16),3)
        elif self.kind=="bat":
            pygame.draw.polygon(s,LPURPLE,[(x+20,y+16),(x-10,y),(x+5,y+25)]); pygame.draw.polygon(s,LPURPLE,[(x+25,y+16),(x+54,y),(x+39,y+25)]); pygame.draw.ellipse(s,PURPLE,(x+10,y+8,25,22)); pygame.draw.circle(s,YELLOW,(x+17,y+16),2); pygame.draw.circle(s,YELLOW,(x+28,y+16),2)
        else:
            q=pygame.Surface((48,42),pygame.SRCALPHA); pygame.draw.ellipse(q,(195,235,255,220),(5,1,38,34)); pygame.draw.polygon(q,(195,235,255,220),[(7,24),(3,40),(16,32),(24,41),(33,32),(44,40),(41,23)]); pygame.draw.circle(q,BLACK,(18,17),3); pygame.draw.circle(q,BLACK,(31,17),3); s.blit(q,(x,y))

class Crystal:
    def __init__(self,x,y): self.r=pygame.Rect(x,y,28,36); self.got=False; self.t=0
    def update(self): self.t+=1
    def draw(self,s,cam):
        if self.got:return
        x,y=self.r.x-cam,self.r.y+int(math.sin(self.t*.08)*5); pts=[(x+14,y),(x+28,y+17),(x+14,y+36),(x,y+17)]
        pygame.draw.polygon(s,CYAN,pts); pygame.draw.polygon(s,WHITE,[(x+14,y+3),(x+21,y+17),(x+14,y+29),(x+8,y+17)]); pygame.draw.polygon(s,BLUE,pts,2)

class Portal:
    def __init__(self,x,y): self.r=pygame.Rect(x,y,62,90); self.t=0
    def update(self): self.t+=1
    def draw(self,s,cam,open_):
        x,y=self.r.x-cam,self.r.y; c=CYAN if open_ else GRAY; b=LPURPLE if open_ else (80,85,105)
        pygame.draw.ellipse(s,b,(x,y,62,90),8); pygame.draw.ellipse(s,NAVY,(x+10,y+10,42,70))
        if open_:
            for i in range(4): pygame.draw.circle(s,c,(x+31,y+45),6+i*7+int(2*math.sin(self.t*.08+i)),2)

PHASES=[
{"name":"Vale Celeste","sky1":(32,72,145),"sky2":(86,195,242),"spark":WHITE,"sun":(255,207,68),"far":(76,128,171),"near":(55,104,133),"ground":(57,125,83),"ground2":(36,86,57),"p":[(0,455,520,90),(610,455,420,90),(1110,455,520,90),(1715,455,410,90),(2200,455,300,90),(330,360,180,28),(760,325,170,28),(1190,350,190,28),(1540,300,180,28),(1900,345,170,28),(2250,315,150,28)],"c":[(390,318),(820,282),(1250,307),(1600,257),(2310,272)],"e":[(700,418,"slime"),(1260,418,"slime"),(1580,240,"bat"),(1970,418,"slime")],"portal":(2390,365)},
{"name":"Floresta Encantada","sky1":(34,35,82),"sky2":(60,132,118),"spark":(187,255,212),"sun":(223,236,155),"far":(43,97,92),"near":(30,72,66),"ground":(39,104,62),"ground2":(24,73,44),"p":[(0,455,450,90),(520,455,360,90),(950,455,450,90),(1480,455,420,90),(1980,455,520,90),(270,340,170,28),(640,285,160,28),(1040,330,180,28),(1420,275,180,28),(1810,340,170,28),(2170,290,170,28)],"c":[(315,297),(690,242),(1100,287),(1480,232),(2220,247)],"e":[(600,418,"slime"),(1050,255,"bat"),(1510,405,"ghost"),(2030,418,"slime"),(2210,230,"bat")],"portal":(2380,365)},
{"name":"Ruínas de Cristal","sky1":(45,24,78),"sky2":(91,59,134),"spark":(255,219,255),"sun":(255,151,88),"far":(71,47,100),"near":(54,36,78),"ground":(93,72,109),"ground2":(58,43,74),"p":[(0,455,380,90),(450,455,340,90),(860,455,350,90),(1280,455,330,90),(1690,455,360,90),(2120,455,380,90),(220,365,150,28),(520,300,170,28),(900,350,160,28),(1260,280,190,28),(1650,335,170,28),(1980,275,170,28),(2280,340,150,28)],"c":[(270,322),(570,257),(950,307),(1325,237),(2330,297)],"e":[(500,418,"ghost"),(880,285,"bat"),(1330,405,"slime"),(1710,280,"bat"),(2040,410,"ghost")],"portal":(2390,365)}]

def make_phase(i):
    f=PHASES[i]; p=Player(); plats=[pygame.Rect(*r) for r in f["p"]]; cs=[Crystal(*v) for v in f["c"]]; es=[Enemy(*v) for v in f["e"]]; po=Portal(*f["portal"]); return p,plats,cs,es,po

B_BACK=pygame.Rect(26,430,132,82); B_FRONT=pygame.Rect(168,430,145,82); B_JUMP=pygame.Rect(666,430,126,82); B_KNIFE=pygame.Rect(802,430,132,82)
B_PAUSE=pygame.Rect(720,18,72,46); B_RESTART=pygame.Rect(800,18,72,46); B_MENU=pygame.Rect(880,18,64,46)
B_START=pygame.Rect(320,408,320,72); B_NEXT=pygame.Rect(320,395,320,70)
def ev_pos(e):
    if e.type in (pygame.FINGERDOWN,pygame.FINGERMOTION,pygame.FINGERUP): return int(e.x*W),int(e.y*H)
    return getattr(e,"pos",(0,0))
def touch_controls(points): return tuple(any(r.collidepoint(p) for p in points) for r in (B_BACK,B_FRONT,B_JUMP,B_KNIFE))
def draw_controls(s,a,b,c,d):
    button(s,B_BACK,"◀ TRÁS",(72,80,120),a); button(s,B_FRONT,"FRENTE ▶",(61,133,213),b); button(s,B_JUMP,"↑ PULAR",(52,175,104),c); button(s,B_KNIFE,"⚔ FACA",(202,82,79),d)
    button(s,B_PAUSE,"II",(72,77,110)); button(s,B_RESTART,"R",(192,108,58)); button(s,B_MENU,"MENU",(33,45,78),font=F16)

def draw_platforms(s,plats,cam,f):
    for p in plats:
        r=p.move(-cam,0)
        if r.right<0 or r.left>W:continue
        pygame.draw.rect(s,f["ground2"],r,border_radius=8); top=pygame.Rect(r.x,r.y,r.w,min(14,r.h)); pygame.draw.rect(s,f["ground"],top,border_radius=8)

def hud(s,p,n,idx):
    panel(s,pygame.Rect(18,14,335,78),(17,24,54),CYAN,220,18); txt(s,PHASES[idx]["name"],F18,YELLOW,34,25); txt(s,"VIDAS",F16,WHITE,34,54)
    for i in range(3):
        cx=96+i*26; col=RED if i<p.life else (70,74,92); pygame.draw.circle(s,col,(cx-5,63),8); pygame.draw.circle(s,col,(cx+5,63),8); pygame.draw.polygon(s,col,[(cx-13,64),(cx+13,64),(cx,79)])
    txt(s,f"CRISTAIS {n}/5",F18,CYAN,188,55)

def menu_screen(s):
    gradient(s,(14,23,54),(50,96,172));
    for i in range(45): pygame.draw.circle(s,(220,240,255),((i*79)%W,20+(i*41)%330),1+i%2)
    panel(s,pygame.Rect(150,65,660,400),(19,27,66),LPURPLE,240,28); txt(s,"AVENTURA DOS CRISTAIS",F50,YELLOW,480,115,True); txt(s,"3 fases • cristais • portal • vilões",F22,WHITE,480,162,True)
    txt(s,"CONTROLES MOBILE",F22,CYAN,250,250); txt(s,"TRÁS  •  FRENTE  •  PULAR  •  FACA",F18,WHITE,250,288); txt(s,"Teclado: A/D ou setas • Espaço/W pula • Ctrl/F ataca",F16,(210,220,245),250,322); txt(s,"Objetivo: pegue 5 cristais e entre no portal.",F18,YELLOW,250,360)
    button(s,B_START,"▶ TOQUE AQUI PARA COMEÇAR",(46,175,92))

def final_screen(s,state,idx):
    q=pygame.Surface((W,H),pygame.SRCALPHA); q.fill((8,12,30,135)); s.blit(q,(0,0)); panel(s,pygame.Rect(190,120,580,300),(26,31,66),RED if state==LOSE else CYAN,245,28)
    if state==LOSE: txt(s,"GAME OVER",F50,RED,480,180,True); txt(s,"Você perdeu todas as vidas.",F22,WHITE,480,230,True); label="↻ JOGAR DE NOVO"
    else:
        last=idx==len(PHASES)-1; txt(s,"VOCÊ ZEROU O JOGO!" if last else "FASE CONCLUÍDA!",F34,YELLOW,480,180,True); txt(s,"Todos os cristais foram salvos!" if last else "Próxima: "+PHASES[idx+1]["name"],F22,WHITE,480,230,True); label="▶ JOGAR NOVAMENTE" if last else "▶ PRÓXIMA FASE"
    button(s,B_NEXT,label,(45,170,95))

async def main():
    state=MENU; idx=0; player,plats,crystals,enemies,portal=make_phase(idx); got=0; cam=0; final_sound=False
    fingers={}; mouse_down=False; mouse=(0,0); running=True
    while running:
        CLOCK.tick(FPS); click=None
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
            elif e.type==pygame.FINGERDOWN: fingers[e.finger_id]=ev_pos(e); click=ev_pos(e)
            elif e.type==pygame.FINGERMOTION: fingers[e.finger_id]=ev_pos(e)
            elif e.type==pygame.FINGERUP: click=ev_pos(e); fingers.pop(e.finger_id,None)
            elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1: mouse_down=True; mouse=e.pos; click=e.pos
            elif e.type==pygame.MOUSEMOTION and mouse_down: mouse=e.pos
            elif e.type==pygame.MOUSEBUTTONUP and e.button==1: mouse_down=False; mouse=e.pos; click=e.pos
            elif e.type==pygame.KEYDOWN:
                if state==MENU and e.key in (pygame.K_RETURN,pygame.K_KP_ENTER,pygame.K_SPACE): player,plats,crystals,enemies,portal=make_phase(idx); got=0; cam=0; final_sound=False; state=PLAY
                elif state==PLAY:
                    if e.key==pygame.K_p: state=PAUSE
                    elif e.key==pygame.K_r: player,plats,crystals,enemies,portal=make_phase(idx); got=0; cam=0
                    elif e.key==pygame.K_ESCAPE: state=MENU
                elif state==PAUSE:
                    if e.key==pygame.K_p: state=PLAY
                    elif e.key==pygame.K_ESCAPE: state=MENU
                elif state in (WIN,LOSE) and e.key in (pygame.K_RETURN,pygame.K_KP_ENTER,pygame.K_SPACE):
                    if state==WIN: idx=idx+1 if idx<len(PHASES)-1 else 0
                    player,plats,crystals,enemies,portal=make_phase(idx); got=0; cam=0; final_sound=False; state=PLAY
        if click:
            if state==MENU and B_START.collidepoint(click): player,plats,crystals,enemies,portal=make_phase(idx); got=0; cam=0; final_sound=False; state=PLAY
            elif state==PLAY:
                if B_PAUSE.collidepoint(click): state=PAUSE
                elif B_RESTART.collidepoint(click): player,plats,crystals,enemies,portal=make_phase(idx); got=0; cam=0
                elif B_MENU.collidepoint(click): state=MENU
            elif state==PAUSE:
                if B_PAUSE.collidepoint(click): state=PLAY
                elif B_MENU.collidepoint(click): state=MENU
            elif state in (WIN,LOSE) and B_NEXT.collidepoint(click):
                if state==WIN: idx=idx+1 if idx<len(PHASES)-1 else 0
                player,plats,crystals,enemies,portal=make_phase(idx); got=0; cam=0; final_sound=False; state=PLAY
        points=list(fingers.values())+([mouse] if mouse_down else []); back,front,jump,knife=touch_controls(points)
        if state==PLAY:
            player.update(pygame.key.get_pressed(),plats,back,front,jump,knife)
            for en in enemies:
                en.update()
                if en.alive and player.atk.colliderect(en.r): en.alive=False
                elif en.alive and player.r.colliderect(en.r): player.hurt()
            for c in crystals:
                c.update()
                if not c.got and player.r.colliderect(c.r): c.got=True; got+=1; play_sound("cristal")
            portal.update()
            if player.r.top>H+120: player.life-=1; play_sound("dano"); player.respawn() if player.life>0 else None
            if player.life<=0: state=LOSE; play_sound("derrota") if not final_sound else None; final_sound=True
            if got>=5 and player.r.colliderect(portal.r): state=WIN; play_sound("vitoria") if not final_sound else None; final_sound=True
            target=player.r.centerx-W//2; cam+=int((target-cam)*.10); cam=max(0,min(cam,WORLD-W))
        if state==MENU: menu_screen(SCREEN)
        else:
            f=PHASES[idx]; background(SCREEN,cam,f); draw_platforms(SCREEN,plats,cam,f)
            for c in crystals:c.draw(SCREEN,cam)
            for en in enemies:en.draw(SCREEN,cam)
            portal.draw(SCREEN,cam,got>=5); player.draw(SCREEN,cam); hud(SCREEN,player,got,idx); draw_controls(SCREEN,back,front,jump,knife)
            txt(SCREEN,"Pegue 5 cristais para liberar o portal" if got<5 else "PORTAL LIBERADO! Vá até o final da fase.",F16,YELLOW if got<5 else CYAN,480,98,True)
            if state==PAUSE:
                q=pygame.Surface((W,H),pygame.SRCALPHA); q.fill((5,8,20,150)); SCREEN.blit(q,(0,0)); panel(SCREEN,pygame.Rect(290,165,380,180),(25,30,70),CYAN,245,24); txt(SCREEN,"PAUSADO",F34,YELLOW,480,220,True); txt(SCREEN,"Toque em II para continuar",F18,WHITE,480,270,True)
            elif state in (WIN,LOSE): final_screen(SCREEN,state,idx)
        pygame.display.flip(); await asyncio.sleep(0)
    pygame.quit()

if __name__=="__main__": asyncio.run(main())
