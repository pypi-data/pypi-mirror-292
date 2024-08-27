import numba
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from numba import njit
import scipy
from scipy.spatial.transform import Rotation as Rot
from itertools import permutations




T=1
R=1
a = 10*R
epsilons = np.linspace(0.1,5,50)*R

steps = 1000
nsteps = 1000
dt = T/steps




etas = np.array([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])



@njit
def mul(a,b):
    ans = np.zeros((5,5,3,3))
    for i in range(5):
        for j in range(5):
            ans[i,j] = a @ b[i,j]
    return ans

def visualize(r,angles=(0,0)):
    ax = plt.figure().add_subplot(projection='3d')
    colors = ('r', 'g', 'b', 'k','y')
    ax.scatter(xs = r[:,0],ys = r[:,1] , zs=r[:,2],c=colors,s=100)
    
    for j in range(0,5):
        ax.plot(xs = [r[j,0] , r[0,0]] , ys = [r[j,1] , r[0,1]] , zs = [r[j,2] , r[0,2]],c="b")
    
    ax.view_init(angles[0],angles[1])
    return ax


def getAngle(a,b):
    return (180/np.pi)*np.arccos(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)))



@njit
def getDistanceMatrix(A):   # dij = rj - ri
    tiledPoses = tile(A)
    distances = tiledPoses - tiledPoses.transpose((1,0,2))
    return distances



@njit
def tile(x):
    tiled = np.zeros((5,5,3))
    for i in range(5):
        tiled[i,:,:] = x
        
    return tiled


def getR0(ls):
    a1,a2,a3,a4 = ls
    
    R0 = [[0, 0, 0],
    [0, 0, a1],
    [a2*np.sqrt(8)/3, 0 , -a2/3],
    [-a3*np.sqrt(8)/6, a3*np.sqrt(24)/6 , -a3/3],
    [-a4*np.sqrt(8)/6, -a4*np.sqrt(24)/6, -a4/3]]
    
    return np.array(R0)




@njit
def tile2(x):
    tiled = np.zeros((5,5,3,3))
    for i in range(3):
        for j in range(3):
            tiled[:,:,i,j] = x
        
    return tiled


@njit
def getO(d):
    d2 = d**2    
    drNorm = np.sum(d2,axis=2)**0.5
            
    
    I5_5_3_3 = np.zeros((5,5,3,3))

    for i in range(5):
        for j in range(5):
            I5_5_3_3[i,j,:,:] = np.eye(3)


    c1 = d.reshape(5,5,3,1)
    c2 = c1.transpose(0,1,3,2)    
    B = np.multiply(c1,c2)    
    c3 = tile2(drNorm)

    O = R*(I5_5_3_3 + B/(c3**2))*0.75/c3 #*R/norm(l)

    for i in range(5):  #for i=j
        O[i,i,:,:] = np.eye(3)
        
    return mul(etas,O)

@njit
def getRR(r):
    rr0 = np.array([
    
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
    [0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1]])
    
    
    rr1 = np.array([[0, -r[0,2] , r[0,1],  0, -r[1,2] , r[1,1],    0, -r[2,2] , r[2,1], 0, -r[3,2] , r[3,1]   ,0, -r[4,2] , r[4,1]],
    [r[0,2], 0 , -r[0,0],   r[1,2], 0 , -r[1,0],  r[2,2], 0 , -r[2,0],  r[3,2], 0 , -r[3,0],  r[4,2], 0 , -r[4,0]],
    [-r[0,1], r[0,0], 0 , -r[1,1], r[1,0], 0 , -r[2,1], r[2,0], 0 ,   -r[3,1], r[3,0], 0 ,  -r[4,1], r[4,0], 0 ]])
    
    


    
    return np.concatenate((rr0,rr1),axis=0)


@njit
def getOO(d):
    ##Check
    k2_3 = np.dot(d[1,0],d[1,0])*np.dot(d[2,0],d[2,0])/np.dot(d[1,0],d[2,0])
    k2_4 = np.dot(d[1,0],d[1,0])*np.dot(d[3,0],d[3,0])/np.dot(d[1,0],d[3,0])
    k2_5 = np.dot(d[1,0],d[1,0])*np.dot(d[4,0],d[4,0])/np.dot(d[1,0],d[4,0])
    k3_4 = np.dot(d[2,0],d[2,0])*np.dot(d[3,0],d[3,0])/np.dot(d[2,0],d[3,0])
    k3_5 = np.dot(d[2,0],d[2,0])*np.dot(d[4,0],d[4,0])/np.dot(d[2,0],d[4,0])

    p2_3 = np.dot(d[2,0],d[2,0])*d[0,1] - k2_3*d[0,2] 
    p2_4 = np.dot(d[3,0],d[3,0])*d[0,1] - k2_4*d[0,3] 
    p2_5 = np.dot(d[4,0],d[4,0])*d[0,1] - k2_5*d[0,4] 
    p3_4 = np.dot(d[3,0],d[3,0])*d[0,2] - k3_4*d[0,3] 
    p3_5 = np.dot(d[4,0],d[4,0])*d[0,2] - k3_5*d[0,4] 


    q2_3 = np.dot(d[1,0],d[1,0])*d[0,2] - k2_3*d[0,1] 
    q2_4 = np.dot(d[1,0],d[1,0])*d[0,3] - k2_4*d[0,1] 
    q2_5 = np.dot(d[1,0],d[1,0])*d[0,4] - k2_5*d[0,1] 
    q3_4 = np.dot(d[2,0],d[2,0])*d[0,3] - k3_4*d[0,2] 
    q3_5 = np.dot(d[2,0],d[2,0])*d[0,4] - k3_5*d[0,2] 
    
    
    OO = np.array([
        [d[1,0,0], d[1,0,1], d[1,0,2], -d[1,0,0], -d[1,0,1], -d[1,0,2], 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [d[2,0,0], d[2,0,1], d[2,0,2], 0, 0, 0, -d[2,0,0], -d[2,0,1], -d[2,0,2], 0, 0, 0, 0, 0, 0,   ],   
    [d[3,0,0], d[3,0,1], d[3,0,2], 0, 0, 0, 0, 0, 0, -d[3,0,0], -d[3,0,1], -d[3,0,2], 0, 0, 0],
    [d[4,0,0], d[4,0,1], d[4,0,2], 0, 0, 0, 0, 0, 0, 0, 0, 0, -d[4,0,0], -d[4,0,1], -d[4,0,2]],
    
    [-p2_3[0] -q2_3[0], -p2_3[1] -q2_3[1], -p2_3[2] -q2_3[2],                p2_3[0], p2_3[1], p2_3[2], q2_3[0], q2_3[1], q2_3[2], 0, 0, 0, 0, 0, 0], #2_3,
    [-p2_4[0] -q2_4[0], -p2_4[1] -q2_4[1], -p2_4[2] -q2_4[2],                p2_4[0], p2_4[1], p2_4[2], 0, 0, 0, q2_4[0], q2_4[1], q2_4[2], 0, 0, 0],  #2_4,
    [-p2_5[0] -q2_5[0], -p2_5[1] -q2_5[1], -p2_5[2] -q2_5[2],                p2_5[0], p2_5[1], p2_5[2], 0, 0, 0, 0, 0, 0, q2_5[0], q2_5[1], q2_5[2]], #2_5
    [-p3_4[0] -q3_4[0], -p3_4[1] -q3_4[1], -p3_4[2] -q3_4[2],                0, 0, 0, p3_4[0], p3_4[1], p3_4[2], q3_4[0], q3_4[1], q3_4[2], 0, 0, 0],  #3_4
    [-p3_5[0] -q3_5[0], -p3_5[1] -q3_5[1], -p3_5[2] -q3_5[2],                0, 0, 0, p3_5[0], p3_5[1], p3_5[2], 0, 0, 0, q3_5[0], q3_5[1], q3_5[2]] #3_5
    
    ])
    
    return OO




@njit
def getC(l,u):
    lu = np.zeros(4)
    for i in range(4):
        lu[i]= (l[i]*u[i])
        
    
    return np.array([*list(lu), 0,0,0,0,0,0,0,0, 0,0,0])  

#  u -> u/steps maybe



def getV(r,l,u):
    d = getDistanceMatrix(r)

    O = getO(d)
    newO = np.zeros((15,15))
    for i in range(5):
        for j in range(5):
            newO[3*i:3*i+3,3*j:3*j+3] = O[i,j]
        
    rr= getRR(r)
    mm = np.linalg.inv(newO)


    NN = np.matmul(rr,mm)
    OO = getOO(d)
    AA = np.concatenate((OO,NN),axis=0)
    
    
    

    BB = getC(l,u)
    
    return np.linalg.solve(AA,BB)
        
        
        
def step(r,L):
    for t in range(1000):
        try:
            U = L[:,t+1]-L[:,t]
        except IndexError:
            U = L[:,t]-L[:,t-1]
            
        v = getV(r,L[:,t],U).reshape((5,3))
        
        r += v  ##########
        
        
    return r  



def act(L):
    r = getR0(L[:,0])
    r_final = step(r.copy(),L)
    delta = list(r_final - r)[0]
    
    return r_final,delta,np.matmul(getE(r_final), np.linalg.inv(getE(r)))




def getE(r):
    e1 = ((r[1]-r[0])/np.linalg.norm((r[1]-r[0]))).reshape((3,1))
    e2 = ((r[2]-r[0])/np.linalg.norm((r[2]-r[0]))).reshape((3,1))
    e3 = ((r[3]-r[0])/np.linalg.norm((r[3]-r[0]))).reshape((3,1))
    
    return np.concatenate((e1,e2,e3),axis=1)



def getCircleSteps(a,epsilon,rotorStep):
    # epsilon = 3
    closing  = a - np.arange(steps+1)*epsilon/steps
    opening = a - epsilon + np.arange(steps+1)*epsilon/steps
    opened = a *np.ones(steps+1)
    closed = (a-epsilon)*np.ones(steps+1)

    totalRotation = np.eye(3)
    totalDelta = 0
    
    rf1,delta,Rotation=  act(np.array([closing,opened,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf2,delta,Rotation=  act(np.array([closed,closing,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf3,delta,Rotation=  act(np.array([closed,closed,closing,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf4,delta,Rotation=  act(np.array([closed,closed,closed,closing]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf5,delta,Rotation=  act(np.array([opening,closed,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf6,delta,Rotation=  act(np.array([opened,opening,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf7,delta,Rotation=  act(np.array([opened,opened,opening,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf8,delta,Rotation=  act(np.array([opened,opened,opened,opening]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    
    
    
    
    
    
    
    
    #rotorStep = 1000
    rotorR = np.array([0.,0.,0.])
    rotorRotation = np.eye(3)

    poses = np.zeros((rotorStep,3))
    for i in range(rotorStep):
        rotorR += np.matmul(rotorRotation,totalDelta)
        rotorRotation = np.matmul(totalRotation,rotorRotation)
        poses[i,:] = rotorR
        
        
    ax = plt.figure().add_subplot(projection='3d')

    ax.scatter(xs = poses[:,0],ys = poses[:,1], zs=poses[:,2])
    plt.savefig("2_2.png")
    plt.show()
        
        
    deltaSpringPerStep = (poses[-1]-poses[0])/rotorStep
    
    # plt.scatter(poses[:,0],poses[:,1])
    # plt.show()
    
    ys= poses[:,1] 
    maxes = np.logical_and((ys >= np.roll(ys,1)),(ys >= np.roll(ys,-1)))
    a1 = list(maxes).index(True,1)
    a2 = list(maxes).index(True,a1+1)

    circlingSteps = a2 -a1
    rotorR = np.array([0.,0.,0.])
    rotorRotation = np.eye(3)

    OneCirclePoses = np.zeros((circlingSteps,3))
    for i in range(circlingSteps):
        rotorR += np.matmul(rotorRotation,totalDelta)
        rotorRotation = np.matmul(totalRotation,rotorRotation)
        OneCirclePoses[i,:] = rotorR
    
    # plt.scatter(poses[:,0],poses[:,1])
    # plt.show()

    image = OneCirclePoses - ((OneCirclePoses[-1]-OneCirclePoses[0])/circlingSteps)*np.arange(circlingSteps).reshape((circlingSteps,1))

    # ax = plt.figure().add_subplot(projection='3d')
    # ax.scatter(xs = image[:,0],ys = image[:,1], zs=image[:,2])
    # ax.scatter(np.mean(image,axis=0)[0],np.mean(image,axis=0)[0],np.mean(image,axis=0)[0])
    # plt.show()

    meanPoing = np.mean(image,axis=0)


    return *deltaSpringPerStep,circlingSteps,np.mean(np.linalg.norm(image - meanPoing,axis=1)),ax




def getCircleSteps2(a,epsilon,rotorStep):
    # epsilon = 3
    closing  = a - np.arange(steps+1)*epsilon/steps
    opening = a - epsilon + np.arange(steps+1)*epsilon/steps
    opened = a *np.ones(steps+1)
    closed = (a-epsilon)*np.ones(steps+1)

    totalRotation = np.eye(3)
    totalDelta = 0
    
    rf1,delta,Rotation=  act(np.array([closing,opened,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf2,delta,Rotation=  act(np.array([closed,closing,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf3,delta,Rotation=  act(np.array([closed,closed,closing,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf4,delta,Rotation=  act(np.array([closed,closed,closed,closing]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf5,delta,Rotation=  act(np.array([opening,closed,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf6,delta,Rotation=  act(np.array([opened,opening,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf7,delta,Rotation=  act(np.array([opened,opened,opening,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf8,delta,Rotation=  act(np.array([opened,opened,opened,opening]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    
    
    
    
    
    
    
    
    #rotorStep = 1000
    rotorR = np.array([0.,0.,0.])
    rotorRotation = np.eye(3)

    poses = np.zeros((rotorStep,3))
    for i in range(rotorStep):
        rotorR += np.matmul(rotorRotation,totalDelta)
        rotorRotation = np.matmul(totalRotation,rotorRotation)
        poses[i,:] = rotorR
        
        
    ax = plt.figure().add_subplot(projection='3d')

    ax.scatter(xs = poses[:,0],ys = poses[:,1], zs=poses[:,2])
    plt.show()
        
        
    deltaSpringPerStep = (poses[-1]-poses[0])/rotorStep
    
    # plt.scatter(poses[:,0],poses[:,1])
    # plt.show()
    
    ys= poses[:,1] 
    maxes = np.logical_and((ys >= np.roll(ys,1)),(ys >= np.roll(ys,-1)))
    a1 = list(maxes).index(True,1)
    a2 = list(maxes).index(True,a1+1)

    circlingSteps = a2 -a1
    rotorR = np.array([0.,0.,0.])
    rotorRotation = np.eye(3)

    OneCirclePoses = np.zeros((circlingSteps,3))
    for i in range(circlingSteps):
        rotorR += np.matmul(rotorRotation,totalDelta)
        rotorRotation = np.matmul(totalRotation,rotorRotation)
        OneCirclePoses[i,:] = rotorR
    
    # plt.scatter(poses[:,0],poses[:,1])
    # plt.show()

    image = OneCirclePoses - ((OneCirclePoses[-1]-OneCirclePoses[0])/circlingSteps)*np.arange(circlingSteps).reshape((circlingSteps,1))

    # ax = plt.figure().add_subplot(projection='3d')
    # ax.scatter(xs = image[:,0],ys = image[:,1], zs=image[:,2])
    # ax.scatter(np.mean(image,axis=0)[0],np.mean(image,axis=0)[0],np.mean(image,axis=0)[0])
    # plt.show()

    meanPoing = np.mean(image,axis=0)
    return *deltaSpringPerStep,circlingSteps,np.mean(np.linalg.norm(image - meanPoing,axis=1))



def getSequences():
    sequences = np.zeros((24,4),dtype=np.int64)
    
    perm = list(permutations([1,2,3,4]))
    
    for i in range(24):
        sequences[i] = list(perm[i])
        
    return sequences
    

def getSequenceEffect(a,epsilon,rotorStep):
    # epsilon = 3
    closing  = a - np.arange(steps+1)*epsilon/steps
    opening = a - epsilon + np.arange(steps+1)*epsilon/steps
    opened = a *np.ones(steps+1)
    closed = (a-epsilon)*np.ones(steps+1)

    totalRotation = np.eye(3)
    totalDelta = 0
    
    rf1,delta,Rotation=  act(np.array([closing,opened,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf2,delta,Rotation=  act(np.array([closed,closing,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf3,delta,Rotation=  act(np.array([closed,closed,closing,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf4,delta,Rotation=  act(np.array([closed,closed,closed,closing]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf5,delta,Rotation=  act(np.array([opening,closed,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf6,delta,Rotation=  act(np.array([opened,opening,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf7,delta,Rotation=  act(np.array([opened,opened,opening,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf8,delta,Rotation=  act(np.array([opened,opened,opened,opening]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rotorR = np.array([0.,0.,0.])
    rotorRotation = np.eye(3)

    poses = np.zeros((rotorStep,3))
    for i in range(rotorStep):
        rotorR += np.matmul(rotorRotation,totalDelta)
        rotorRotation = np.matmul(totalRotation,rotorRotation)
        poses[i,:] = rotorR
        
        
    ax = plt.figure().add_subplot(projection='3d')

    ax.scatter(xs = poses[:,0],ys = poses[:,1], zs=poses[:,2])
    plt.show()
        
        
    deltaSpringPerStep1 = (poses[-1]-poses[0])/rotorStep
    
    #2  1243
    totalRotation = np.eye(3)
    totalDelta = 0
    
    rf1,delta,Rotation=  act(np.array([closing,opened,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf2,delta,Rotation=  act(np.array([closed,closing,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf3,delta,Rotation=  act(np.array([closed,closed,opened,closing]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf4,delta,Rotation=  act(np.array([closed,closed,closing,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf5,delta,Rotation=  act(np.array([opening,closed,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf6,delta,Rotation=  act(np.array([opened,opening,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf7,delta,Rotation=  act(np.array([opened,opened,closed,opening]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf8,delta,Rotation=  act(np.array([opened,opened,opening,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rotorR = np.array([0.,0.,0.])
    rotorRotation = np.eye(3)

    poses = np.zeros((rotorStep,3))
    for i in range(rotorStep):
        rotorR += np.matmul(rotorRotation,totalDelta)
        rotorRotation = np.matmul(totalRotation,rotorRotation)
        poses[i,:] = rotorR
        
        
    ax = plt.figure().add_subplot(projection='3d')

    ax.scatter(xs = poses[:,0],ys = poses[:,1], zs=poses[:,2])
    plt.show()
        
        
    deltaSpringPerStep2 = (poses[-1]-poses[0])/rotorStep
    
    
    #3 1324

    totalRotation = np.eye(3)
    totalDelta = 0
    
    rf1,delta,Rotation=  act(np.array([closing,opened,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf2,delta,Rotation=  act(np.array([closed,opened,closing,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf3,delta,Rotation=  act(np.array([closed,closing,closed,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf4,delta,Rotation=  act(np.array([closed,closed,closed,closing]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf5,delta,Rotation=  act(np.array([opening,closed,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf6,delta,Rotation=  act(np.array([opened,closed,opening,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf7,delta,Rotation=  act(np.array([opened,opening,opened,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf8,delta,Rotation=  act(np.array([opened,opened,opened,opening]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rotorR = np.array([0.,0.,0.])
    rotorRotation = np.eye(3)

    poses = np.zeros((rotorStep,3))
    for i in range(rotorStep):
        rotorR += np.matmul(rotorRotation,totalDelta)
        rotorRotation = np.matmul(totalRotation,rotorRotation)
        poses[i,:] = rotorR
        
        
    ax = plt.figure().add_subplot(projection='3d')

    ax.scatter(xs = poses[:,0],ys = poses[:,1], zs=poses[:,2])
    plt.show()
        
        
    deltaSpringPerStep3 = (poses[-1]-poses[0])/rotorStep
    
    #4   1423

    totalRotation = np.eye(3)
    totalDelta = 0
    
    rf1,delta,Rotation=  act(np.array([closing,opened,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf2,delta,Rotation=  act(np.array([closed,opened,opened,closing]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf3,delta,Rotation=  act(np.array([closed,closing,opened,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf4,delta,Rotation=  act(np.array([closed,closed,closing,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf5,delta,Rotation=  act(np.array([opening,closed,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf6,delta,Rotation=  act(np.array([opened,closed,closed,opening]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf7,delta,Rotation=  act(np.array([opened,opening,closed,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf8,delta,Rotation=  act(np.array([opened,opened,opening,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rotorR = np.array([0.,0.,0.])
    rotorRotation = np.eye(3)

    poses = np.zeros((rotorStep,3))
    for i in range(rotorStep):
        rotorR += np.matmul(rotorRotation,totalDelta)
        rotorRotation = np.matmul(totalRotation,rotorRotation)
        poses[i,:] = rotorR
        
        
    ax = plt.figure().add_subplot(projection='3d')

    ax.scatter(xs = poses[:,0],ys = poses[:,1], zs=poses[:,2])
    plt.show()
        
        
    deltaSpringPerStep4 = (poses[-1]-poses[0])/rotorStep
    
    #5 1432

    totalRotation = np.eye(3)
    totalDelta = 0
    
    rf1,delta,Rotation=  act(np.array([closing,opened,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf2,delta,Rotation=  act(np.array([closed,opened,opened,closing]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf3,delta,Rotation=  act(np.array([closed,opened,closing,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf4,delta,Rotation=  act(np.array([closed,closing,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf5,delta,Rotation=  act(np.array([opening,closed,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf6,delta,Rotation=  act(np.array([opened,closed,closed,opening]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf7,delta,Rotation=  act(np.array([opened,closed,opening,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf8,delta,Rotation=  act(np.array([opened,opening,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rotorR = np.array([0.,0.,0.])
    rotorRotation = np.eye(3)

    poses = np.zeros((rotorStep,3))
    for i in range(rotorStep):
        rotorR += np.matmul(rotorRotation,totalDelta)
        rotorRotation = np.matmul(totalRotation,rotorRotation)
        poses[i,:] = rotorR
        
        
    ax = plt.figure().add_subplot(projection='3d')

    ax.scatter(xs = poses[:,0],ys = poses[:,1], zs=poses[:,2])
    plt.show()
        
        
    deltaSpringPerStep5 = (poses[-1]-poses[0])/rotorStep
    
    
    #6 1342

    totalRotation = np.eye(3)
    totalDelta = 0
    
    rf1,delta,Rotation=  act(np.array([closing,opened,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf2,delta,Rotation=  act(np.array([closed,opened,closing,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf3,delta,Rotation=  act(np.array([closed,opened,closed,closing]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf4,delta,Rotation=  act(np.array([closed,closing,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf5,delta,Rotation=  act(np.array([opening,closed,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf6,delta,Rotation=  act(np.array([opened,closed,opening,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf7,delta,Rotation=  act(np.array([opened,closed,opened,opening]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf8,delta,Rotation=  act(np.array([opened,opening,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rotorR = np.array([0.,0.,0.])
    rotorRotation = np.eye(3)

    poses = np.zeros((rotorStep,3))
    for i in range(rotorStep):
        rotorR += np.matmul(rotorRotation,totalDelta)
        rotorRotation = np.matmul(totalRotation,rotorRotation)
        poses[i,:] = rotorR
        
        
    ax = plt.figure().add_subplot(projection='3d')

    ax.scatter(xs = poses[:,0],ys = poses[:,1], zs=poses[:,2])
    plt.show()
        
    deltaSpringPerStep6 = (poses[-1]-poses[0])/rotorStep
    
    
    return deltaSpringPerStep1,deltaSpringPerStep2,deltaSpringPerStep3,deltaSpringPerStep4,deltaSpringPerStep5,deltaSpringPerStep6
    


def getStartingEffect(a,epsilon,rotorStep):
    # epsilon = 3
    closing  = a - np.arange(steps+1)*epsilon/steps
    opening = a - epsilon + np.arange(steps+1)*epsilon/steps
    opened = a *np.ones(steps+1)
    closed = (a-epsilon)*np.ones(steps+1)

    totalRotation = np.eye(3)
    totalDelta = 0
    
    rf1,delta,Rotation=  act(np.array([closing,opened,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf2,delta,Rotation=  act(np.array([closed,closing,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf3,delta,Rotation=  act(np.array([closed,closed,closing,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf4,delta,Rotation=  act(np.array([closed,closed,closed,closing]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf5,delta,Rotation=  act(np.array([opening,closed,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf6,delta,Rotation=  act(np.array([opened,opening,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf7,delta,Rotation=  act(np.array([opened,opened,opening,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf8,delta,Rotation=  act(np.array([opened,opened,opened,opening]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rotorR = np.array([0.,0.,0.])
    rotorRotation = np.eye(3)

    poses = np.zeros((rotorStep,3))
    for i in range(rotorStep):
        rotorR += np.matmul(rotorRotation,totalDelta)
        rotorRotation = np.matmul(totalRotation,rotorRotation)
        poses[i,:] = rotorR
        
        
    ax = plt.figure().add_subplot(projection='3d')

    ax.scatter(xs = poses[:,0],ys = poses[:,1], zs=poses[:,2])
    plt.show()
        
        
    deltaSpringPerStep1 = (poses[-1]-poses[0])/rotorStep
    
    #2  1243
    totalRotation = np.eye(3)
    totalDelta = 0
    
    rf1,delta,Rotation=  act(np.array([opened,closing,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf2,delta,Rotation=  act(np.array([opened,closed,closing,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf3,delta,Rotation=  act(np.array([opened,closed,closed,closing]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf4,delta,Rotation=  act(np.array([closing,closed,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf5,delta,Rotation=  act(np.array([closed,opening,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf6,delta,Rotation=  act(np.array([closed,opened,opening,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    rf7,delta,Rotation=  act(np.array([closed,opened,opened,opening]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf8,delta,Rotation=  act(np.array([opening,opened,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rotorR = np.array([0.,0.,0.])
    rotorRotation = np.eye(3)

    poses = np.zeros((rotorStep,3))
    for i in range(rotorStep):
        rotorR += np.matmul(rotorRotation,totalDelta)
        rotorRotation = np.matmul(totalRotation,rotorRotation)
        poses[i,:] = rotorR
        
        
    ax = plt.figure().add_subplot(projection='3d')

    ax.scatter(xs = poses[:,0],ys = poses[:,1], zs=poses[:,2])
    plt.show()
        
        
    deltaSpringPerStep2 = (poses[-1]-poses[0])/rotorStep
    
    
    #3 1324

    totalRotation = np.eye(3)
    totalDelta = 0
    
    rf1,delta,Rotation=  act(np.array([opened,opened,closing,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf2,delta,Rotation=  act(np.array([opened,opened,closed,closing]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf3,delta,Rotation=  act(np.array([closing,opened,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf4,delta,Rotation=  act(np.array([closed,closing,closed,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf5,delta,Rotation=  act(np.array([closed,closed,opening,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf6,delta,Rotation=  act(np.array([closed,closed,opened,opening]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf7,delta,Rotation=  act(np.array([opening,closed,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf8,delta,Rotation=  act(np.array([opened,opening,opened,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rotorR = np.array([0.,0.,0.])
    rotorRotation = np.eye(3)

    poses = np.zeros((rotorStep,3))
    for i in range(rotorStep):
        rotorR += np.matmul(rotorRotation,totalDelta)
        rotorRotation = np.matmul(totalRotation,rotorRotation)
        poses[i,:] = rotorR
        
        
    ax = plt.figure().add_subplot(projection='3d')

    ax.scatter(xs = poses[:,0],ys = poses[:,1], zs=poses[:,2])
    plt.show()
        
        
    deltaSpringPerStep3 = (poses[-1]-poses[0])/rotorStep
    
    #4   1423

    totalRotation = np.eye(3)
    totalDelta = 0
    
    rf1,delta,Rotation=  act(np.array([opened,opened,opened,closing]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf2,delta,Rotation=  act(np.array([closing,opened,opened,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf3,delta,Rotation=  act(np.array([closed,closing,opened,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf4,delta,Rotation=  act(np.array([closed,closed,closing,closed]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf5,delta,Rotation=  act(np.array([closed,closed,closed,opening]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf6,delta,Rotation=  act(np.array([opening,closed,closed,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf7,delta,Rotation=  act(np.array([opened,opening,closed,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rf8,delta,Rotation=  act(np.array([opened,opened,opening,opened]))
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    rotorR = np.array([0.,0.,0.])
    rotorRotation = np.eye(3)

    poses = np.zeros((rotorStep,3))
    for i in range(rotorStep):
        rotorR += np.matmul(rotorRotation,totalDelta)
        rotorRotation = np.matmul(totalRotation,rotorRotation)
        poses[i,:] = rotorR
        
        
    ax = plt.figure().add_subplot(projection='3d')

    ax.scatter(xs = poses[:,0],ys = poses[:,1], zs=poses[:,2])
    plt.show()
        
        
    deltaSpringPerStep4 = (poses[-1]-poses[0])/rotorStep
    

    
    
    return deltaSpringPerStep1,deltaSpringPerStep2,deltaSpringPerStep3,deltaSpringPerStep4
    


# @njit
# def getAction(state,ratio):
#     #t=1 if state=0 and t = ratio if state = 1   ???
#     t1,t2,t3,t4 = np.where(state==0,1,ratio)
#     sum = t1*t2*t3 + t1*t2*t4 + t1*t3*t4 + t2*t3*t4
#     #probs = np.array([t2*t3*t4/sum,t1*t3*t4/sum,t1*t2*t4/sum,t2*t3*t1/sum])
#     randomNumber = np.random.uniform(0,1,1)
#     if randomNumber <= t4*t2*t3/sum:
#         changingJoint = 0
#     elif(randomNumber <= (t4*t3*t1+t4*t2*t3)/sum):  
#         changingJoint = 1
#     elif randomNumber <= (t4*t2*t1+t4*t2*t3+t4*t3*t1)/sum:
#         changingJoint = 2
#     else:
#         changingJoint = 3
#     return changingJoint,getDeltat2(t1,t2,t3,t4)


# @njit
# def doStep(Data,state,ratio):
#     action,deltat = getAction(state,ratio)
#     new_state = state.copy()
#     new_state[action] = 1 - new_state[action]
#     delta = Data[fromBinary(state)*4 + action][0,:]  #???
#     rotation = Data[fromBinary(state)*4 + action][1:,:]
#     return new_state,delta,rotation,deltat


# @njit
# def getDeltat(t1,t2,t3,t4,tc):
#     tav = 18.844
#     return ((1-1/(tav*t1))*(1-1/(tav*t2))*(1-1/(tav*t3))*(1-1/(tav*t4))*tav/tc)/(((1/t1 + 1/t2 + 1/t3 + 1/t4)**2)*(1-1/(tav*tc)))

# @njit
# def getDeltat2(t1,t2,t3,t4):
#     return 1/(1/t1 + 1/t2 + 1/t3 + 1/t4)


# @njit
# def getBinary(a):
#     return np.array([a//8,(a%8)//4,(a%4)//2,a%2])
# @njit 
# def fromBinary(binary):
#     x = 0
#     for i in range(len(binary)):
#         x += binary[::-1][i]*(2**i)
#     return x

# @njit 
# def fromBinary2d(binaries):
#     x = np.zeros(binaries.shape[0],dtype=np.int64)
#     for i in range(binaries.shape[0]):
#         x[i] = fromBinary(binaries[i])
#     return x



# def getAllPossibleActions(a,epsilon,steps):
    
#     closing = a - np.arange(steps+1)*epsilon/steps
#     closed = (a-epsilon)*np.ones(steps+1)
#     opening = a - epsilon + np.arange(steps+1)*epsilon/steps
#     opened  = a *np.ones(steps+1)
    
#     possibleActions = np.zeros((64,4,steps+1))
    
    
    
#     for i in range(16):
#         for j in range(4):
#             actionBinaryState = getBinary(i)
#             # closed for 0 and opened for 1 
#             ca = np.array([closed,closed,closed,closed])*actionBinaryState.reshape(4,1) + np.array([opened,opened,opened,opened])*(1-actionBinaryState).reshape(4,1)
#             if actionBinaryState[j] == 0:
#                 ca[j,:] = opening
#             else:
#                 ca[j,:] = closing
                
#             possibleActions[4*i+j] = ca 
        
#     return possibleActions



# @njit 
# def mul(a,b):
#     return a @ b


# @njit
# def mul2(a,v):
#     ans = np.zeros(3,dtype=np.float64)
#     for i in range(3):
#         ans[i] = a[i,0]*v[0] + a[i,1]*v[1] +a[i,2]*v[2]
#     return ans


# @njit
# def perturbe(Data,perturbingSteps,ratio):
#     time = 0
#     pertrubingPose = np.array([0.,0.,0.])
#     perturbingRotation = np.eye(3)
#     state = np.ones(4,dtype=np.int64)
#     pertrubingPoses = np.zeros((perturbingSteps,3))
#     pertrubingTimes = np.zeros(perturbingSteps)
        
#     for t in range(perturbingSteps):
#         newState,delta,rotation,deltat = doStep(Data,state,ratio)
#         state = newState
#         pertrubingPose += perturbingRotation @ delta
#         perturbingRotation = rotation @ perturbingRotation
#         pertrubingPoses[t] = pertrubingPose
#         time += deltat
#         pertrubingTimes[t] = time
        
#     return pertrubingPoses,pertrubingTimes




# @njit
# def getPerturbingDiffusionCoefForRatio(Data,ratio,iterations=10_000,perturbingSteps=10_000):
#     iterations = 10_000
#     perturbingSteps = 10_000
#     meanFinalPoses = np.zeros((perturbingSteps))
#     meanFinalTimes = np.zeros(perturbingSteps)
#     for iteration in range(iterations):
#         pertrubingPoses,pertrubingTimes = perturbe(Data,perturbingSteps,ratio)
#         #print(np.sum(np.square(pertrubingPoses[:]),axis=1).shape,meanFinalPoses.shape)
#         meanFinalPoses +=   np.sum(np.square(pertrubingPoses[:]),axis=1)
#         meanFinalTimes += pertrubingTimes
#         #print(iteration)
     
#     return meanFinalTimes/iterations,meanFinalPoses/iterations

# def getPerturbingDiffusionCoef(Data,ratios):
#     diffs =np.zeros(ratios.shape)
#     for i in range(ratios.shape[0]):
#         print(i)
#         meanFinalTimes,meanFinalPoses= getPerturbingDiffusionCoefForRatio(Data,ratios[i])
#         slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(meanFinalPoses,meanFinalTimes)
#         diffs[i] =  slope 
#     return diffs


@njit
def getOrientedAction(state,ratio,rotation,grad):
     #TODO *ratio
    #t=1 if state=0 and t = ratio if state = 1
    # print(np.dot(rotation,r0.T).T,cGrad)
    # print(np.dot(np.dot(rotation,r0.T).T,cGrad))

    grad = np.array([0., 0., grad])
    ratios = ratio + np.dot(np.dot(rotation,r0[1:].T).T,grad)

    
    t1,t2,t3,t4 = np.where(state==0,np.ones(4),ratios)
    #print(t1,t2,t3,t4)
    
    sum = t1*t2*t3 + t1*t2*t4 + t1*t3*t4 + t2*t3*t4
    #probs = np.array([t2*t3*t4/sum,t1*t3*t4/sum,t1*t2*t4/sum,t2*t3*t1/sum])
    randomNumber = np.random.uniform(0,1,1)
    if randomNumber <= t4*t2*t3/sum:
        changingJoint = 0
     #   deltat = getDeltat(t1,t2,t3,t4,t1)
    elif(randomNumber <= (t4*t2*t1+t4*t2*t3)/sum):  
        changingJoint = 1
#        deltat = getDeltat(t1,t2,t3,t4,t2)
    elif randomNumber <= (t4*t2*t1+t4*t2*t3+t4*t2*t1)/sum:
        changingJoint = 2
        # deltat = getDeltat(t1,t2,t3,t4,t3)
    else:
        changingJoint = 3
        # deltat = getDeltat(t1,t2,t3,t4,t4)

    #changingJoint = np.random.choice(np.arange(4),p=probs)
    # action = np.concatenate((state,changingJoint.reshape((1,))),axis=0)
    # deltat = 1 if state[changingJoint]==0 else ratio
    return changingJoint,getDeltat2(t1,t2,t3,t4)

@njit
def doOrientedStep(Data,state,ratio,rotation,grad):
    action,deltat = getOrientedAction(state,ratio,rotation,grad)
    new_state = state.copy()
    new_state[action] = 1 - new_state[action]
    delta = Data[fromBinary(state)*4 + action][0,:]
    rotation = Data[fromBinary(state)*4 + action][1:,:]
    return new_state,delta,rotation,deltat



@njit
def Orientedperturbe(Data,perturbingSteps,ratio,grad):
    time = 0
    pertrubingPose = np.array([0.,0.,0.])
    perturbingRotation = np.eye(3)
    state = np.ones(4,dtype=np.int64)
    pertrubingPoses = np.zeros((perturbingSteps,3))
    pertrubingTimes = np.zeros(perturbingSteps)

    for t in range(perturbingSteps):
        newState,delta,rotation,deltat = doOrientedStep(Data,state,ratio,perturbingRotation,grad)
        state = newState
        pertrubingPose += mul2(perturbingRotation,delta)
        perturbingRotation = mul(rotation,perturbingRotation)
        pertrubingPoses[t] = pertrubingPose
        time += deltat
        pertrubingTimes[t] = time

    return pertrubingPoses,pertrubingTimes




@njit
def getOrientedPerturbingDiffusionCoefForRatio(Data,ratio,grad):
    iterations = 10_00
    perturbingSteps = 10_000
    meanFinalPoses = np.zeros((perturbingSteps))
    meanFinalTimes = np.zeros(perturbingSteps)
    for iteration in range(iterations):
        pertrubingPoses,pertrubingTimes = Orientedperturbe(Data,perturbingSteps,ratio,grad)
        #print(np.sum(np.square(pertrubingPoses[:]),axis=1).shape,meanFinalPoses.shape)
        meanFinalPoses += pertrubingPoses[:,2]
        meanFinalTimes += pertrubingTimes
        #print(iteration)
     
    # plt.plot(meanFinalTimes,meanFinalPoses)
    # plt.show()
    
    # return slope  #*some Coef
    return meanFinalTimes/iterations,-meanFinalPoses/iterations

def getOrientedPerturbingDiffusionCoef(Data,ratio,grads):
    diffs =np.zeros(grads.shape)
    for i in range(grads.shape[0]):
        print(i)
        meanFinalTimes,meanFinalPoses= getOrientedPerturbingDiffusionCoefForRatio(Data,ratio,grads[i])
        slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(meanFinalTimes,meanFinalPoses)
        diffs[i] =  slope 
    return diffs


def getOrientedPerturbingDiffusionCoef2(Data,ratios,grad):
    diffs =np.zeros(grads.shape)
    for i in range(ratios.shape[0]):
        print(i)
        meanFinalTimes,meanFinalPoses= getOrientedPerturbingDiffusionCoefForRatio(Data,ratios[i],grad*ratios[i])
        slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(meanFinalTimes,meanFinalPoses)
        diffs[i] =  slope 
    return diffs


def actSequence(ns,a,epsilon,rotorStep):
    n1,n2,n3,n4 = ns
    closing  = a - np.arange(steps+1)*epsilon/steps
    opening = a - epsilon + np.arange(steps+1)*epsilon/steps
    opened = a *np.ones(steps+1)
    closed = (a-epsilon)*np.ones(steps+1)

    totalRotation = np.eye(3)
    totalDelta = 0
    
    allStart = np.array([opened,opened,opened,opened])
    
    allStart[n1-1,:] = closing
    
    rf1,delta,Rotation=  act(allStart)
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    allStart[n1-1,:] = closed
    allStart[n2-1,:] = closing

    rf2,delta,Rotation=  act(allStart)
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    allStart[n2-1,:] = closed
    allStart[n3-1,:] = closing

    rf3,delta,Rotation=  act(allStart)
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    allStart[n3-1,:] = closed
    allStart[n4-1,:] = closing

    rf4,delta,Rotation=  act(allStart)
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    allStart[n4-1,:] = closed
    allStart[n1-1,:] = opening

    rf5,delta,Rotation=  act(allStart)
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    allStart[n1-1,:] = opened
    allStart[n2-1,:] = opening

    rf6,delta,Rotation=  act(allStart)
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    allStart[n2-1,:] = opened
    allStart[n3-1,:] = opening

    rf7,delta,Rotation=  act(allStart)
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)

    allStart[n3-1,:] = opened
    allStart[n4-1,:] = opening

    rf8,delta,Rotation=  act(allStart)
    totalDelta += np.matmul(totalRotation,delta)
    totalRotation  = np.matmul(Rotation,totalRotation)
    
    # _,vs = np.linalg.eig(totalRotation)
    # for i in range(3):
    #     if np.sum(np.square(np.imag(vs[i])))==0:
    #         return vs[i].real
    
    rotorR = np.array([0.,0.,0.])
    rotorRotation = np.eye(3)

    poses = np.zeros((rotorStep,3))
    for i in range(rotorStep):
        rotorR += np.matmul(rotorRotation,totalDelta)
        rotorRotation = np.matmul(totalRotation,rotorRotation)
        poses[i,:] = rotorR
        
        

        
        
    deltaSpringPerStep1 = (poses[-1]-poses[0])/rotorStep
    
    return deltaSpringPerStep1,totalDelta,totalRotation
    