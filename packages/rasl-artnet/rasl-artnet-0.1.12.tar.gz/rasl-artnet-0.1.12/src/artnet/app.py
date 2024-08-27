import os
import time
from zmq.devices import ProcessProxy,ThreadProxy
import zmq
import sys
import random
from . import dataFrame
from google.protobuf.timestamp_pb2 import Timestamp
from multiprocessing.managers import SharedMemoryManager
from multiprocessing import Lock, Process, Event
from timeit import default_timer as timer
from resource import *
import concurrent.futures
from datetime import datetime
import traceback

class InternalState:
    def __init__(self, sharedMuscleState, sharedBlendshapeState, sharedAvatarState, muscleLocks, blendshapeLocks, avatarLock):
        self.muscleState = sharedMuscleState
        self.blendshapeState = sharedBlendshapeState
        self.avatarState = sharedAvatarState
        self.muscleLocks = muscleLocks
        self.blendshapeLocks = blendshapeLocks
        self.avatarLock = avatarLock            
    
    def GetMuscle(self,muscleNum):
        muscle = dataFrame.Values()
        muscle.ParseFromString(self.muscleState[muscleNum])
        return muscle
        
    def GetBlendshape(self,bsNum):
        bs = dataFrame.Values()
        bs.ParseFromString(self.blendshapeState[bsNum])
        return bs
    
    def UpdateMuscle(self,muscleNum, muscle):
        self.muscleState[muscleNum] = muscle.SerializeToString()

    def UpdateBlendshape(self, bsNum, bs):
        #print(bs)
        self.blendshapeState[bsNum] = bs.SerializeToString()
    
    def UpdateAvatarState(self, id):
        avatarState = dataFrame.AvatarState()
        avatarState.id = id
        currentTimeStamp = Timestamp()
        with self.avatarLock:
            currentTimeStamp.GetCurrentTime()
            avatarState.ParseFromString(self.avatarState[0])
            for i in range(len(self.muscleState)):
                muscle = self.GetMuscle(i)
                sortedEntries = sorted(muscle.entries.items(), key = lambda x: x[0])
                for key, entry in sortedEntries:
                    expireTime = entry.timestamp.ToMicroseconds() + entry.duration.ToMicroseconds()
                    #print(f'entry: {key} expire time: {expireTime}')
                    #print(f'current time: {currentTime}')
                    #print(f'Valid?: {expireTime > currentTime}')
                    if expireTime > currentTimeStamp.ToMicroseconds():
                        #print(f'First valid entry detected, copying entry {key} to avatar state muscle {key}')
                        avatarState.muscles[i].CopyFrom(entry)
                        break
            for i in range(len(self.blendshapeState)):
                blendshape = self.GetBlendshape(i)
                #print(blendshape)
                sortedEntries = sorted(blendshape.entries.items(), key = lambda x: x[0])
                for key, entry in sortedEntries:
                    expireTime = entry.timestamp.ToMicroseconds() + entry.duration.ToMicroseconds()
                    #print(f'entry: {key} expire time: {expireTime}')
                    #print(f'current time: {currentTime}')
                    #print(f'Valid?: {expireTime > currentTime}')
                    if expireTime > currentTimeStamp.ToMicroseconds():
                        #print(f'First valid entry detected, copying entry {key} to avatar state muscle {key}')
                        avatarState.blendshapes[i].CopyFrom(entry)
                        break
            self.avatarState[0] = avatarState.SerializeToString()
            #print(avatarState)
    def GetSerializedAvatarState(self):
        with self.avatarLock:
            return self.avatarState[0]

class DataEntryWorker:
    def __init__(self, stateTuple):
        # self.messageFrame = dataFrame.DataFrame()
        self.state = InternalState(*stateTuple)
        # self.numBlendshapes = numBlendshapes
            
    def ProcessFrame(self,messageFrame):
        #lastBS = list(messageFrame.blendshapes.keys())[-1]
        #lastP = 1
        #print(f'{self.pid} Pre-Processing Lag: {messageFrame.blendshapes[lastBS].entries[lastP].timestamp.ToMicroseconds() / 1000 - time.time()*1000}')
        #print(f'Processing time: {(end - start)*1000}')
        #print(f'{self.pid} Pre Computation Lag: {messageFrame.blendshapes[lastBS].entries[lastP].timestamp.ToMicroseconds() / 1000 - time.time()*1000}')
        # compStart = timer()
        for muscle in messageFrame.muscles.keys():
            # for each entry, aka priority 
            with self.state.muscleLocks[muscle]:
                internalState = self.state.GetMuscle(muscle)
                for entry in messageFrame.muscles[muscle].entries.keys():
                    if messageFrame.muscles[muscle].entries[entry].timestamp.ToMicroseconds() > internalState.entries[entry].timestamp.ToMicroseconds():
                        internalState.entries[entry].CopyFrom(messageFrame.muscles[muscle].entries[entry])
                self.state.UpdateMuscle(muscle,internalState)
        for blendshape in messageFrame.blendshapes.keys():
            with self.state.blendshapeLocks[blendshape]:
                internalState = self.state.GetBlendshape(blendshape)
                for entry in messageFrame.blendshapes[blendshape].entries.keys():
                    if messageFrame.blendshapes[blendshape].entries[entry].timestamp.ToMicroseconds() > internalState.entries[entry].timestamp.ToMicroseconds():
                        internalState.entries[entry].CopyFrom(messageFrame.blendshapes[blendshape].entries[entry])
                self.state.UpdateBlendshape(blendshape,internalState)
        # compEnd = timer()
        #print(f'{self.pid} Post Computation Lag: {messageFrame.blendshapes[lastBS].entries[lastP].timestamp.ToMicroseconds() / 1000 - time.time()*1000}')
        #print(f'{self.pid} Post Avatar Update Lag: {messageFrame.blendshapes[lastBS].entries[lastP].timestamp.ToMicroseconds() / 1000 - time.time()*1000}')
        # end = timer()
        # print(f'Computation Time: {compEnd - compStart}')
        #print(f'Read/Write Time: {(end - start) - (compEnd - compStart)}')
                
    def ProcessFrameUnparsed(self,msg):
        # print(msg)
        messageFrame = dataFrame.DataFrame()
        messageFrame.ParseFromString(msg)
        #lastBS = list(messageFrame.blendshapes.keys())[-1]
        #lastP = 1
        #print(f'{self.pid} Pre-Processing Lag: {messageFrame.blendshapes[lastBS].entries[lastP].timestamp.ToMicroseconds() / 1000 - time.time()*1000}')
        #print(f'Processing time: {(end - start)*1000}')
        #print(f'{self.pid} Pre Computation Lag: {messageFrame.blendshapes[lastBS].entries[lastP].timestamp.ToMicroseconds() / 1000 - time.time()*1000}')
        # compStart = timer()
        for muscle in messageFrame.muscles.keys():
            # for each entry, aka priority 
            with self.state.muscleLocks[muscle]:
                internalState = self.state.GetMuscle(muscle)
                for entry in messageFrame.muscles[muscle].entries.keys():
                    if messageFrame.muscles[muscle].entries[entry].timestamp.ToMicroseconds() > internalState.entries[entry].timestamp.ToMicroseconds():
                        # print('Copying...')
                        internalState.entries[entry].CopyFrom(messageFrame.muscles[muscle].entries[entry])
                self.state.UpdateMuscle(muscle,internalState)
        for blendshape in messageFrame.blendshapes.keys():
            with self.state.blendshapeLocks[blendshape]:
                internalState = self.state.GetBlendshape(blendshape)
                for entry in messageFrame.blendshapes[blendshape].entries.keys():
                    if messageFrame.blendshapes[blendshape].entries[entry].timestamp.ToMicroseconds() > internalState.entries[entry].timestamp.ToMicroseconds():
                        internalState.entries[entry].CopyFrom(messageFrame.blendshapes[blendshape].entries[entry])
                self.state.UpdateBlendshape(blendshape,internalState)
        # compEnd = timer()
        #print(f'{self.pid} Post Computation Lag: {messageFrame.blendshapes[lastBS].entries[lastP].timestamp.ToMicroseconds() / 1000 - time.time()*1000}')
        #print(f'{self.pid} Post Avatar Update Lag: {messageFrame.blendshapes[lastBS].entries[lastP].timestamp.ToMicroseconds() / 1000 - time.time()*1000}')
        # end = timer()
        # print(f'Computation Time: {compEnd - compStart}')
        #print(f'Read/Write Time: {(end - start) - (compEnd - compStart)}')

def SubscriberFun(port):
    context = zmq.Context()
    sub = context.socket(zmq.SUB)
    print(f'Subscribing to all topics on tcp://localhost:{port}')
    sub.connect(f'tcp://localhost:{port}')
    sub.subscribe("")
    state = dataFrame.AvatarState()
    # state = dataFrame.DataFrame()
    # print('Waiting to receive...')
    while True:
        event = sub.poll(timeout=500)
        if event == 0:
            # print('Waiting to receive...')
            pass
        else:
            msg = sub.recv_multipart()
            state.ParseFromString(msg[1])
            print(f'Received State for {msg[0]}')
    

def ProcessMsg(id, data):
    try:
        # print('In ProcessMsg Function')
        global workerDict
        workerDict[id].ProcessFrameUnparsed(data)
        # workerDict.ProcessFrameUnparsed(data)
    except Exception as e:
        print(e)

def InitFun(sDict, pPort, pPeriod, rEvent, sEvent):
    # print('Starting Pool Process!')
    try:
        global stateDict, pubEndpoint, pubPeriod, restartEvent, stopEvent, workerDict
        stateDict = sDict
        pubEndpoint = f'tcp://*:{pPort}'
        pubPeriod = pPeriod
        restartEvent = rEvent
        stopEvent = sEvent
        workerDict = {}
        for id, stateTuple in stateDict.items():
            # workerDict[id] = DataEntryWorker(stateTuple)
            workerDict[id] = DataEntryWorker(stateTuple)
    except Exception as e:
        print(e)

def PublisherFun():
    # print('In pub function')
    global stateDict, pubEndpoint, pubPeriod, restartEvent, stopEvent
    
    internalStateDict = {}
    for id, stateTuple in stateDict.items():
        internalStateDict[id] = InternalState(*stateTuple)
    
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    # print(f'Publishing on {pubEndpoint}', flush=True)
    publisher.bind(pubEndpoint)
    # publisher.connect('tcp://localhost:5552')
    pubStart = timer()
    while not (stopEvent.is_set() or restartEvent.is_set()):
        try:
            if (timer() - pubStart) >= pubPeriod:
                for id,s in internalStateDict.items():
                        s.UpdateAvatarState(id)
                        # print(f'Publishing avatar {id}...')
                        publisher.send_multipart([id.encode(),s.GetSerializedAvatarState(), datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').encode()])
                pubStart = timer()
        except Exception as e:
            print(traceback.format_exc(), flush=True)

def ProcessPoolSharedFun(streamerEndpoint,pubPort,pubHz,mConfig):
    name = "Process Pool Shared List"
    context = zmq.Context.instance()
    receiver = context.socket(zmq.PULL)
    receiver.connect(streamerEndpoint)
    restartEvent = Event()
    stopEvent = Event()
    # subscriber = context.socket(zmq.SUB)
    # subscriber.connect(f'tcp://localhost:{pubPort}')
    # subscriber.subscribe("")
    while True:
        stopEvent.clear()
        stateDict = {}
        futures = []
        count = 0
        print('Waiting to receive messages...')
        msg = receiver.recv_multipart()
        start = timer()
        id = msg[0].decode()
        stateDict[id] = createShareableListSet(*mConfig)
        fStart = timer()
        fPeriod = 1.0
        pubPeriod = 1.0 / float(pubHz)
        timeoutms = 1000
        while not stopEvent.is_set():
            restartEvent.clear()
            with concurrent.futures.ProcessPoolExecutor(initializer=InitFun, initargs=(stateDict,pubPort, pubPeriod, restartEvent, stopEvent)) as executor:
                internalStateDict = {}
                for id, stateTuple in stateDict.items():
                    internalStateDict[id] = InternalState(*stateTuple)
                f = executor.submit(ProcessMsg,id,msg[1])
                futures.append(f)
                print('Starting publisher...')
                executor.submit(PublisherFun)
                count += 1

                # shared memory and publisher has been set up
                # now repeatedly process new messages until something changes
                while not (stopEvent.is_set() or restartEvent.is_set()):

                    # worker queue stats
                    if (timer() - fStart) >= fPeriod:
                        print(f'Current work queue size: {executor._work_ids.qsize()}')
                        fStart = timer()

                    # attempt to receive new message
                    event = receiver.poll(timeout=timeoutms)

                    # if message recv times out then we stop processing and publishing
                    # until new messages are received
                    if event == 0:
                        print(f'Stopping processing...')
                        stopEvent.set()
                        executor.shutdown() # default waits for current futures to complete
                    else:                    
                        msg = receiver.recv_multipart()
                        id = msg[0].decode()
                        # restart if we receive avatar data with a new id
                        # in order to make new shared memory for it
                        if id in stateDict:
                            futures.append(executor.submit(ProcessMsg, id,msg[1]))
                            count += 1
                        else:
                            print(f'Restarting processing...')
                            stateDict[id] = createShareableListSet(*mConfig)
                            restartEvent.set()
        end = timer()
        duration = end - start - timeoutms/1000.0
        print(f'{name} Total Messages Received: {count}')
        print(f'{name} Total Time (ms): {(duration)*1000}')
        print(f'{name} Messages per Second: {count/duration}')

def CreateRandomMessages(num, ids, numMuscles, numBlendshapes, numPriorities):
    duration = 1000
    msgs = []
    for i in range(num):
        frame = dataFrame.DataFrame()        
        frame.id = random.choice(ids)
        
        for i in range(numMuscles):
            for j in range(1,numPriorities+1):
                for k in range(6):
                    frame.muscles[i].entries[j].values.append(random.random())
                frame.muscles[i].entries[j].priority = j
                frame.muscles[i].entries[j].timestamp.GetCurrentTime()
                frame.muscles[i].entries[j].duration.FromSeconds(duration)
        for i in range(numBlendshapes):
            for j in range(1,numPriorities+1):
                for k in range(1):
                    frame.blendshapes[i].entries[j].values.append(random.random())
                frame.blendshapes[i].entries[j].priority = j
                frame.blendshapes[i].entries[j].timestamp.GetCurrentTime()
                frame.blendshapes[i].entries[j].duration.FromSeconds(duration)
        msgs.append((frame.id,frame.SerializeToString()))
    return msgs

def ProxyMonitor(name, monitorPort):
    context = zmq.Context()
    monitor = context.socket(zmq.SUB)
    monitor.connect(f'tcp://localhost:{monitorPort}')
    monitor.subscribe('')
    count = 0
    receiving = False
    totalBytes = 0
    
    print(f'{name} starting...')
    
    while True:
        try:
            event = monitor.poll(timeout=500)
            if event == 0:
                if receiving:

                    end = timer()
                    receiving = False
                    print(f'{name} - Received {count} messages and {totalBytes/1000} kiloBytes in {(end-start)*1000-500} milliseconds')
                    print(f'{name} - Rate: {count / (end-start-0.5)} msgs/s ')
                    print(f'{name} - Rate: {totalBytes / (end-start-0.5) / 1000} kB/s')
                    count = 0
                    totalBytes = 0
            else:
                if count >= 1000:
                    end = timer()
                    receiving = False
                    print(f'{name} - Received {count} messages and {totalBytes/1000} kiloBytes in {(end-start)*1000} milliseconds')
                    print(f'{name} - Rate: {count / (end-start)} msgs/s ')
                    print(f'{name} - Rate: {totalBytes / (end-start) / 1000} kB/s')
                    count = 0
                    totalBytes = 0
                if not receiving:
                    start = timer()
                    receiving = True
                count += 1
                msg = monitor.recv_multipart()
                totalBytes += sys.getsizeof(msg[0])
                totalBytes += sys.getsizeof(msg[1])
            # print(f'Received a message of size {sys.getsizeof(msg)} bytes!')
        except KeyboardInterrupt:
            break


def createShareableListSet(m, numMuscles, numBlendshapes, byteLength, avatarStateByteLength):
    # create shared memory objects
    #numMuscles += 1
    #numBlendshapes += 1
    muscleSequence = []
    muscleLocks = []
    blendshapeSequence = []
    blendshapeLocks = []
    avatarStateSequence = [b' ' * avatarStateByteLength] #filled with empty bytes-- length of each element in this list. Avatar state is only the highest priority fresh data
    avatarStateLock = Lock() #locks are for race conditions... Each muscle can be accessed individually. What happens if the two workers are accessing the same state at the same time.
    #single lock associated with each muscle and blendshape... 
    for i in range(numMuscles):
        muscleSequence.append(b' ' * byteLength)
        muscleLocks.append(Lock())
    for i in range(numBlendshapes):
        blendshapeSequence.append(b' ' * byteLength)
        blendshapeLocks.append(Lock())
    
    sharedMuscleState = m.ShareableList(muscleSequence) #muscle sequence is telling the length of data... Memory size.
    sharedBlendshapeState = m.ShareableList(blendshapeSequence)
    sharedAvatarState = m.ShareableList(avatarStateSequence)


    #initialize sharedMuscleState, sharedBlendshapeState, and sharedAvatarState to default values
    frame = dataFrame.DataFrame()
    defaultState = dataFrame.AvatarState()
    sharedAvatarState[0] = defaultState.SerializeToString()
    for muscle in range(len(sharedMuscleState)):
        sharedMuscleState[muscle] = frame.muscles[muscle].SerializeToString()
    for bs in range(len(sharedBlendshapeState)):
        sharedBlendshapeState[bs] = frame.blendshapes[bs].SerializeToString()
    stateTuple = (sharedMuscleState,sharedBlendshapeState,sharedAvatarState,muscleLocks,blendshapeLocks,avatarStateLock)
    return stateTuple

def main():
    # frontendPort = 5559
    frontendPort = os.environ.get('FRONTEND_PORT')
    # backendPort = 5556
    backendPort = os.environ.get('BACKEND_PORT')
    # pubHz = 30
    pubHz = int(os.environ.get('PUBLISHER_HZ'))
    # frontendMonitorPort = 5553
    frontendMonitorPort = os.environ.get('FRONTEND_MONITOR_PORT')
    voiceFrontend = os.environ.get('VOICE_FRONTEND_PORT')
    # voiceFrontend = 5561
    voiceBackend = os.environ.get('VOICE_BACKEND_PORT')
    # voiceBackend = 5562
    

    # streamerEndpoint = 'inproc://streamer' # ThreadProxy
    streamerEndpoint = 'ipc://streamer' #ProcessProxy
    
    # streamerProxy = ThreadProxy(zmq.PULL, zmq.PUSH, zmq.PUB)
    streamerProxy = ProcessProxy(zmq.PULL, zmq.PUSH, zmq.PUB)
    streamerProxy.bind_in(f'tcp://*:{frontendPort}')
    streamerProxy.bind_out(streamerEndpoint)
    streamerProxy.bind_mon(f'tcp://*:{frontendMonitorPort}')
    streamerProxy.start()

    # voiceProxy = ThreadProxy(zmq.SUB, zmq.PUB)
    voiceProxy = ProcessProxy(zmq.SUB, zmq.PUB)
    voiceProxy.bind_in(f'tcp://*:{voiceFrontend}')
    voiceProxy.setsockopt_in(zmq.SUBSCRIBE,b'')
    voiceProxy.bind_out(f'tcp://*:{voiceBackend}')
    voiceProxy.start()

    processes = []
    processes.append(Process(target=ProxyMonitor, args=('Streamer Monitor',frontendMonitorPort)))
    # processes.append(Process(target=ProxyMonitor, args=('Publisher Monitor',backendMonitorPort)))
    # processes.append(Process(target=SubscriberFun, args=(backendPort,)))
    for p in processes:
        p.daemon = True
        p.start()

    numMuscles = int(os.environ.get("NUM_MUSCLES"))
    numBlendshapes = int(os.environ.get("NUM_BLENDSHAPES"))
    numPriorities = int(os.environ.get("NUM_PRIORITIES"))
    entryByteLength = int(os.environ.get("ENTRY_BYTE_LENGTH"))
    byteLength = entryByteLength * numPriorities 
    avatarStateByteLength = entryByteLength * (numMuscles + numBlendshapes)
    
    with SharedMemoryManager() as m:
        mConfig = (m, numMuscles, numBlendshapes, byteLength, avatarStateByteLength)
        ProcessPoolSharedFun(streamerEndpoint, backendPort, pubHz, mConfig)
        
        
if __name__ == '__main__':
    main()
    