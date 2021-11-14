import matplotlib as mp
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import threading
import socket
import Classification
import json
import time
import os
import pygame
from pygame.locals import *

HOST='127.0.0.1'
res = [0,0,0,0]
pos = [[0,0],[0,0],[0,0],[0,0]]
flags = [['경적',3], ['고함',1], ['폭발',3], ['충돌',3], ['화재경보',3], ['알람',1], ['응급차량',2], ['사이렌',2]]

t_start = time.time()

errcount = 0

logf = open('/home/pi/Desktop/HappyNewEar/log.txt', 'wt')

making_noise = 0

def noise(rate):
    t_start = time.time()
    
    global making_noise
    
    duration = 0.5
    freq = 100
    
    print('noise')
    
    for i in range(rate):
        making_noise = 1
        os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
        
    making_noise = 0
    print('{0}|{1:0>4.3f}|{2:0>4.3f}|{3:0>4.3f}'.format('noise()', t_start, time.time(), time.time()-t_start), file = logf)


def Sort(data):
    t_start = time.time()
    data = clf.tonumpy(data)
    data = clf.preprocess(data)

    ch1 = data[0::4]
    ch2 = data[1::4]
    ch3 = data[2::4]
    ch4 = data[3::4]

    res[0] = clf.classifier(ch1)
    res[1] = clf.classifier(ch2)
    res[2] = clf.classifier(ch3)
    res[3] = clf.classifier(ch4)
    print("="*50)

    print('{0}|{1:0>4.3f}|{2:0>4.3f}|{3:0>4.3f}'.format('Sort()', t_start, time.time(), time.time()-t_start), file = logf)

def getRaw():
    t_start = time.time()
    print('raw')
    count=0
    
    RAWclient, addr = RAWserver.accept()
    print('connected',addr)

    raw = []

    t = time.time()

    while True:
        buff = (RAWclient.recv(8192))
        
        if not buff:
            print('nothing recived')
            if count >10:
                break
            count+=1

        else:
            if time.time() < t+1:
                raw.append(buff)
            else:
                #print('====================')
                data = raw
        
                t1_1 = threading.Thread(target=Sort,args=([data]))
                t = time.time()
                t1_1.start()
                
                raw = []
    print('{0}|{1:0>4.3f}|{2:0>4.3f}|{3:0>4.3f}'.format('getRaw()', t_start, time.time(), time.time()-t_start), file = logf)

def getDest():
    print('dest')

    count=0
    DESTclient, addr = DESTserver.accept()
    print('connected',addr)
    
    global errcount

    while True:

        t_start = time.time()
        flush=DESTclient.recv(4096)
        buff = DESTclient.recv(4096)

        if not buff:
            print('nothing recived')
            if count >10:
                break
            count+=1

        else:
            ch=0
            try:

                dat = json.loads(buff.decode())
                #print('====================')               
                #print('err= ') 
                #os.system('clear')

                for i in dat['src']:
                    pos[ch][0] = int(i['x']*220+335)
                    pos[ch][1] = int(i['y']*220+240)
                    ch += 1      

            except Exception as e:

                errcount += 1
                #print('err= ',e)
                #os.system('clear') 
        print('{0}|{1:0>4.3f}|{2:0>4.3f}|{3:0>4.3f}'.format('getDest()', t_start, time.time(), time.time()-t_start), file = logf)

def pltthread():

      global pos
      global res
      global flags
      global making_noise
      
      t_start = time.time()

      pygame.init()

      BLACK = (  0,   0,   0)
      GRAY  = (125, 125, 125)
      WHITE = (255, 255, 255)
      BLUE  = (  0,   0, 255)
      GREEN = (  0, 255,   0)
      RED   = (255,   0,   0)

      size   = [800, 480]

      screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
      pygame.display.set_caption("HappyNewEar")
      font = pygame.font.SysFont("nanumgothic",15)
      
      done = False

      clock = pygame.time.Clock()

      while not done:
          clock.tick(30)

          for event in pygame.event.get(): 
              if event.type == pygame.QUIT: 
                  done=True
                  
          screen.fill(WHITE)
          
          j=0
          
          for i in flags:
              for j in range(4):
                  if i[0] == res[j]:
                      
                      print('pltthread...{0}|{1:0>4.3f}|{2:0>4.3f}|{3:0>4.3f}'.format(i[0], t_start, time.time(), time.time()-t_start), file = logf)
                      img = pygame.image.load('/home/pi/Desktop/HappyNewEar/img/{0}.png'.format(i[0]))
                      img = pygame.transform.scale(img, (460,460))
                      screen.blit(img, (105,10))
                      
                      if making_noise == 0:
                          t3_1 = threading.Thread(target=noise, args=(i[1],))
                          t3_1.start()
                      else:
                          pass
                      
                  else:
                      pass
                      
          pygame.draw.line(screen, BLACK, (335,10), (335,470), 3)
          pygame.draw.line(screen, BLACK, (10,240), (660,240), 3)
          pygame.draw.rect(screen, GRAY, [10,10,650,460],5)
          pygame.draw.circle(screen, BLUE, pos[0], 4)
          pygame.draw.circle(screen, RED, pos[1], 4)
          pygame.draw.circle(screen, GREEN, pos[2], 4)
          pygame.draw.circle(screen, BLACK, pos[3], 4)
          
          res0 = font.render('{0}'.format(res[0]), True, BLUE)
          res1 = font.render('{0}'.format(res[1]), True, RED)
          res2 = font.render('{0}'.format(res[2]), True, GREEN)
          res3 = font.render('{0}'.format(res[3]), True, BLACK)
          screen.blit(res0, (670, 95))
          screen.blit(res1, (670, 135))
          screen.blit(res2, (670, 175))
          screen.blit(res3, (670, 215))
 
          #print(pos)
          pygame.display.flip()

          if t1.is_alive() == False:
              break

      pygame.quit()
      print('{0}|{1:0>4.3f}|{2:0>4.3f}|{3:0>4.3f}'.format('pltthread()', t_start, time.time(), time.time()-t_start), file = logf)

if __name__ == '__main__':

    RAWserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    DESTserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    RAWserver.bind((HOST,9001))
    DESTserver.bind((HOST,9000))
    RAWserver.listen()
    DESTserver.listen()
    print('RAW,DEST server listening')

    clf = Classification.Classificate()

    t1 = threading.Thread(target=getRaw)
    t2 = threading.Thread(target=getDest)
    t3 = threading.Thread(target=pltthread)

    t1.start()
    t2.start()
    t3.start()

    os.chdir('odas/bin')
    os.system('./odaslive -c odas.cfg')

    t1.join()
    t2.join()
    t3.join()
    

    print('{0:0.3f}초, 오류횟수 {1}번'.format(time.time()-t_start, errcount))

    logf.close()
    RAWserver.close()
    DESTserver.close()