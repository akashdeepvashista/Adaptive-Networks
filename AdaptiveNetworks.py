# imported python libraries
import sys
import random as r
from collections import deque, defaultdict 
import time

# Creating Access nodes = 40
access_nodes = []
for i in range(1,41):
    access_nodes.append("A"+str(i))

# Creating Edge nodes = 30
edges_nodes = []
for i in range(1,31):
    edges_nodes.append("E"+str(i))

# Creating Core nodes = 25
core_nodes = []
for i in range(1,26):
    core_nodes.append("C"+str(i))

# Creating Border nodes = 5
border_nodes = []
for i in range(1,6):
    border_nodes.append("B"+str(i))

# Shuffling all the nodes list for creating a random connections in the network
r.shuffle(access_nodes)
r.shuffle(edges_nodes)
r.shuffle(core_nodes)
r.shuffle(border_nodes)

# Introducing a new list for packet loss at each node which is randomly genereated
nodes_packetloss = {}
for p in edges_nodes:
    nodes_packetloss[p] = r.randint(1,6)
for p in core_nodes:
    nodes_packetloss[p] = r.randint(1,6)
for p in border_nodes:
    nodes_packetloss[p] = r.randint(1,6)
nodes_packetloss

# Creating a default dictonary for holding the network topology
network = defaultdict(list)

# Generating communication links between Access and Edge nodes randomly 
edgepacketSizes = defaultdict()
for i in access_nodes:
    sample_edges = {}
    reverse_edges = {}
    l = r.sample(edges_nodes,5)
    packet_size = r.randint(1,9)                                # packet size selected randomly
    fail_prob = r.randint(10,90)                                # Failure probability is randomly generated from 10(low) - 90(critical)
    attack_perc = r.randint(1,7)                                # Attack percentage is randomly generated from 1%(low) - 7%(Critical)
    cost = 1                                                    # Cost of each link is equal
    bw = 10                                                     # bandwidth
    rbw = bw - packet_size                                      # Remaining bandwidth = bandwidth - packetsize
    utilization = int((packet_size / bw) * 100)                 # Utilization is 90%(Critical) 
    for j in range(0,5):
        latency = r.randint(1,6)
        packet_loss = r.randint(1,6)
        edgepacketSizes[l[j]] = edgepacketSizes[l[j]]+packet_size if l[j] in edgepacketSizes else packet_size   # Calculating the total packetsize reaching the node.
        if(utilization<90):
            sample_edges[l[j]] = [bw,latency,packet_size,cost,fail_prob,attack_perc,rbw,utilization]            # Every link is created with these attributes
    network[i].append(sample_edges)

# Generating communication links betweeb Edge and Core nodes randomly
corepacketSizes = defaultdict()
for i in edges_nodes:
    sample_edges = {}
    reverse_edges = {}
    l = r.sample(core_nodes,4)
    packet_size = edgepacketSizes[i]                            
    bw = r.randint(40,100)
    #fail_prob = r.randint(10,90)
    attack_perc = r.randint(1,7)
    cost = 1
    rbw = bw - packet_size
    utilization = int((packet_size / bw) * 100)
    for j in range(0,4):
        latency = r.randint(1,5)
        packet_loss = r.randint(1,5)
        fail_prob = r.randint(0,90)
        corepacketSizes[l[j]] = corepacketSizes[l[j]]+packet_size if l[j] in corepacketSizes else packet_size # Calculating total packetsize reaching the node
        if(utilization<90):
            sample_edges[l[j]] = [bw,latency,packet_size,cost,fail_prob,attack_perc,rbw,utilization]   # Links are created with defined attributes
    network[i].append(sample_edges)

# Generating Communication links inside the core nodes randomly
in_corepacketSizes = defaultdict()
for i in core_nodes:
    sample_edges = {}
    reverse_edges = {}
    l = r.sample(core_nodes,2)
    fail_prob = r.randint(0,90)
    attack_perc = r.randint(1,7)
    packet_size = corepacketSizes[i]
    in_corepacketSizes[i] = in_corepacketSizes[i]+packet_size if i in in_corepacketSizes else packet_size  # Calculating the total packetsize reaching the node
    if l[0] != i:
        bw = r.randint(100,400)
        cost = 1
        rbw = bw - packet_size
        utilization = int((packet_size / bw) * 100)
        for j in range(0,2):
            latency = r.randint(1,5)
            packet_loss = r.randint(1,5)  
            if(utilization<90):
                sample_edges[l[j]] = [bw,latency,packet_size,cost,fail_prob,attack_perc,rbw,utilization]   # creating link between cores with defined attributes
                reverse_edges[i] = [bw,latency,packet_size,cost,fail_prob,attack_perc,rbw,utilization]  # creating reverse link as the cores can communicate among themselves
            network[l[j]].append(reverse_edges)
        network[i].append(sample_edges)

# Generating communication link between Core and Border nodes randomly       
borderpacketSizes = defaultdict()
for i in core_nodes:
    sample_edges = {}
    reverse_edges = {}
    l = r.sample(border_nodes,1)
    packet_size = corepacketSizes[i]
    bw = r.randint(100,400)
    #fail_prob = r.randint(10,90)
    attack_perc = r.randint(1,7)
    rbw = bw - packet_size
    utilization = int((packet_size / bw) * 100)
    cost = 1
    for j in l:
        latency = r.randint(1,5)
        fail_prob = r.randint(0,90)
        packet_loss = r.randint(1,5)    
        borderpacketSizes[j] = borderpacketSizes[j]+packet_size if j in borderpacketSizes else packet_size  # Calculationg the total packetsize reaching the node
        if(utilization<90):
            sample_edges[j] = [bw,latency,packet_size,cost,fail_prob,attack_perc,rbw,utilization]   # creating the link with all the defined atrributes   
    network[i].append(sample_edges)

# finding the initial path based on the equal cost using BFS
def shortest_path(graph, origin, destination):
    l = deque()
    visited = []
    details = ""
    path = ""
    l.append((origin,str(origin),""))
    while len(l)>0:
        e = l.popleft()
        visited.append(e[0])
        if(destination == e[0]):
            path = e[1]
            details = e[2]
            break
        for n in graph[e[0]]:
            for i in n.items():
                if i[0] not in visited:
                    l.append((i[0],e[1]+"->"+str(i[0]),e[2]+str(i[1])))
    return path,details

# Function defined for storing the initial path
def pathInitialDetails(path,lists):
    paths = path.split("->")
    l = lists.split("][")
    for i,y in enumerate(l):
        temp = y.strip(" [").strip("]")
        p = temp.split(", ")
        print("Packet Size "+paths[i]+"->"+paths[i+1]+" is: "+p[2])
        print("Link Utilization "+paths[i]+"->"+paths[i+1]+" is: "+p[7]+"%")
    print("Initial routing path:",path) 

# Function defined for analysing and finding the best reserved path based on Failure probability,  attack percentage, Utilization
def minDistance(l):
    min_fail_prob = sys.maxsize
    min_attack_perc = sys.maxsize
    max_util = 90
    for item in l:
        if len(item[3])>0 :
            if min_fail_prob > item[3][4] and min_attack_perc > item[3][5] and item[3][7] < max_util:
                min_fail_prob = item[3][4]
                min_attack_perc = item[3][5]
                val = item
        else:
            return item
    return val

# Function for analysing the reserved path for in the network
def reserve_path(graph, origin, destination):
    l = []
    details =""
    path = ""
    visited = []
    l.append((origin,str(origin),"",[]))
 
    while len(l)>0:
        e = minDistance(l)
        l.remove(e)
        visited.append(e[0])
        if(destination == e[0]):
            #print(e[1])
            #print(e[2])
            path = e[1]
            details = e[2]
            break
        for n in graph[e[0]]:
            for i in n.items():
                if i[0] not in visited:
                    l.append((i[0],e[1]+"->"+str(i[0]),e[2]+" "+str(i[1]),i[1]))
    return path,details

# soting the reserved path detail 
def pathDetails(path,lists):
    paths = path.split("->")
    l = lists.split("] [")
    for i,y in enumerate(l):
        temp = y.strip(" [").strip("]")
        p = temp.split(", ")
        if(i>0):
            print("Reserved band width "+paths[i]+"->"+paths[i+1]+" is: "+p[2])
            print("Link utilization "+paths[i]+"->"+paths[i+1]+" is: "+p[7]+"%")
    print("Reserved Path is:",path)

# For continous traffic monitoring stating at time 't1'
count = 1
while(True):
    print("At time t",count)
    count = count + 1   
    origin = r.sample(access_nodes,1)[0]                      # Randomly selecting the origion or source node
    destination = r.sample(core_nodes,1)[0]                   # Randomly selecting the destination node
    p,l = shortest_path(network,origin,destination)           # checking for initial path by calling the shortest_path function

    print("Origin: ",origin)
    print("Destination: ",destination)
    if(p==""):
        print("No communication link can be  established")                               # Checking if the communication link can be established for the origin and destination

    else:
        pathInitialDetails(p,l)                               # Storing the initial path details
    path,lists = reserve_path(network,origin,destination)     # Checking for Reserved path by calling reserve_path function
    if(path==""):
        print("No reserve communication path exists")
    else:
        pathDetails(path,lists)                               # Storing the reserved path details
    if(path == p):
        if(path == "" and p == ""):
            continue
        print("No alternate path exists, Initial path is the best available path")                     # when initial path is the best path, then we don't have an alternate path.
    time.sleep(5)                                             # used for monitoring traffic every 5 seconds

# used 'Ctrl+c' to terminate the code ***
    