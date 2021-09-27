import matplotlib as mp
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import threading
import socket
import Classification
import json
import time
import os

HOST='127.0.0.1'
res = [0,0,0,0]
pos = [[[0],[0],[0],[0]],[[0],[0],[0],[0]]]
flags = [['Vehicle horn',3], ['Shout',1], ['Explosion',3], ['Crushing',3], ['Fire alarm',3], ['Alarm',1], ['Emergency vehicle',2], ['Siren',2]]

t_start = time.time()
errcount = 0
logf = open('/home/pi/Desktop/HappyNewEar/log.txt', 'wt')

def noise(rate):
    duration = 0.5
    freq = 100
    print('noise')
    for i in range(rate):
        os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))

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
            if time.time() < t+0.98:
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
                    pos[0][ch] = i['x']
                    pos[1][ch] = i['y']
                    ch += 1
                    
                    
            except Exception as e:
                
                errcount += 1
                #print('err= ',e)
                #os.system('clear')
        print('{0}|{1:0>4.3f}|{2:0>4.3f}|{3:0>4.3f}'.format('getDest()', t_start, time.time(), time.time()-t_start), file = logf)
        
def pltthread():
    
    global pos
    global res
    plt.get_current_fig_manager().full_screen_toggle()

    while True:
        t_start = time.time()
        try:
            for i in flags:
                for ch in range(4):
                    if i[0] == res[ch]:
                        print('....', i[0])
                        image = mpimg.imread('/home/pi/Desktop/HappyNewEar/img/{0}.png'.format(i[0]))
                        
                        plt.imshow(image, extent=[-1,1,-1,1])
                        noise(i[1])
                    else:
                        pass
        except Exception as e:
            f = open('debuf.txt', 'wt')
            print(e, file=f)
            print(e)
            f.close()
            
        
        plt.axvline(x=0,color='r')
        plt.axhline(y=0,color='r')
        plt.xlim(-1,1)
        plt.ylim(-1,1)
        plt.scatter(pos[0][0], pos[1][0],label = res[0])
        plt.scatter(pos[0][1], pos[1][1],label = res[1])
        plt.scatter(pos[0][2], pos[1][2],label = res[2])
        plt.scatter(pos[0][3], pos[1][3],label = res[3])
        for i in res:
            print(i)
        plt.legend(loc='lower left', frameon=False)
        plt.pause(0.001)
        plt.clf()
            
        if t1.is_alive() == False:
            break
        print('{0}|{1:0>4.3f}|{2:0>4.3f}|{3:0>4.3f}'.format('pltthread()', t_start, time.time(), time.time()-t_start), file = logf)
        
    plt.close()

    
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
    