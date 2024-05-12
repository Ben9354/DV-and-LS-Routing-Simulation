""" @file LinkState.py
 *  @brief Link State routing protocol.
 * 
 *  Reads topology file and creates topology graph network. Then creates and prints forwarding tables for each node using Distance Vector routing.
 *  Reads and sends messages via the forwarding tables. Applies any topology changes and repeats the previous two steps.
 * 
 *  @author Benjamin Chung
 *  @bug When printing the routing tables, the order is not enforced. 
 *  (One can tell which table it is via the destination as itself and cost as 0).
"""

from collections import defaultdict
import sys
import os.path

class Router:
    
    """ @brief Initalizes graph network as a 2D dictionary, 
     *  forwarding table as a dictionary, and list of messages to be stored.
     *
    """    
    def __init__(self):
        self.graphNodes = defaultdict(dict)
        self.forwardingTables = {}
        self.messages = []
    
    """ @brief Reads the topology file and creates the graph network as a 2D dictionary.
     *
     *  @param topologyFile     The file containing the network topology.
    """    
    def read_topology(self, topologyFile):
        with open(topologyFile, 'r') as topFile:
            for line in topFile:
                node1, node2, cost = map(int, line.split())
                self.graphNodes[node1][node2] = cost
                self.graphNodes[node2][node1] = cost
                
    """ @brief Creates the forwarding table for each node in the network using Distance Vector routing.
     *
     *  @param outputFile   File to write the forwarding table to.
    """
    def forwarding_table(self, outputFile):
        with open(outputFile, 'a') as outFile:
            for node in self.graphNodes:
                #Initalizes destination for each node in forwarding table.
                if node not in self.forwardingTables:
                    self.forwardingTables[node] = {}
                #Initalizes the node cost for per destination as infinity and 0 for its own node.
                cost = defaultdict(lambda: float('inf'))
                cost[node] = 0
                #Initalizes next hop for per node.
                nextHop = {}

                #Initalizes the costs of immediate neighbor nodes and lists them as nextHops.
                for neighbor in self.graphNodes[node]:
                    cost[neighbor] = self.graphNodes[node][neighbor]
                    nextHop[neighbor] = neighbor

                #Used to keep track of visited destinations per node.
                visited = set()
                visited.add(node)

                #While all destinations have not yet been visited:
                while len(visited) < len(self.graphNodes):
                    minNode = None
                    minCost = float('inf')
                    #Finds the destination node with least cost and has not yet been visited.
                    for dest in self.graphNodes:
                        if (dest not in visited and cost[dest] < minCost):
                            minNode = dest
                            minCost = cost[dest]
                    #Exists while loop if all destination nodes have been visited, else add destination node to visited.
                    if minNode is None:
                        break
                    else:
                        visited.add(minNode)
                    #For the previous lowest cost node, checks it's surrounding neighbors to determine 
                    #if there exists a lower cost to get to such node than the current cost.
                    for nextNode in self.graphNodes[minNode]:
                        if nextNode not in visited:
                            nextCost = self.graphNodes[minNode][nextNode]
                            if cost[minNode] + nextCost < cost[nextNode]:
                                cost[nextNode] = cost[minNode] + nextCost
                                #Next hop to take to get to next node
                                nextHop[nextNode] = nextHop[minNode]
                #For each destination in cost table, writes the nextHop to take and the cost it takes to get to each destination from node.
                for dest in cost:
                    if dest != node:
                        self.forwardingTables[node][dest] = (nextHop[dest], cost[dest])
                        outFile.write(f"{dest} {nextHop[dest]} {cost[dest]}\n")

                self.forwardingTables[node][node] = (node, 0)
                outFile.write(f"{node} {node} 0\n\n") 

    """ @brief Reads the message file and stores the messages to be sent in 'messages' as a tuple.
     *
     *  @param messageFile     The file containing the messages to be sent.
    """    
    def read_message(self, messageFile):
        with open(messageFile, 'r') as msgFile:
            for line in msgFile:
                source, dest, message = line.split(maxsplit=2)
                self.messages.append((int(source), int(dest), message.strip()))

    """ @brief Sends the messages to their respective destinations using forwarding tables. 
     *
     *  @param outputFile   File to write the messages to.
    """    
    def send_messages(self, outputFile):
        with open(outputFile, 'a') as outFile:
            #Extracts the tuple values from list of tuple messages.
            for (source, dest, message) in self.messages:
                #Checks if there is a valid path from the source to destination in the forwarding table.
                if (source in self.forwardingTables and dest in self.forwardingTables[source]):
                    nextHop, pathCost = self.forwardingTables[source][dest]
                    path = [source, nextHop]
                    outFile.write(f"from {source} to {dest} cost {pathCost} hops {' '.join(map(str, path))} message {message}\n")
                else:
                    outFile.write(f"from {source} to {dest} cost infinite hops unreachable message {message}\n")

    """ @brief Reads the topology changes file and apply the changes to the network.
     *
     *  @param changesFile      The file containing the topology changes.
     *
     *  @return     A list of tuples containing the changes to be made to the network.
    """    
    def read_topology_changes(self, changesFile):
        topologyChanges = []
        with open(changesFile, 'r') as changeFile:
            for line in changeFile:
                    node1, node2, cost = map(int, line.split())
                    topologyChanges.append((node1, node2, cost))
            return topologyChanges      

    """ @brief Applies the topology changes to the network.
     *
     *  @param topologyChanges      A list of tuples containing the changes to be made to the network.
    """    
    def apply_topology_change(self, topologyChanges):
        for change in topologyChanges:
            if change[2] == -999:
                del self.graphNodes[change[0]][change[1]]
                #KeyError prevention
                try:
                    del self.graphNodes[change[1]][change[0]]
                except KeyError:
                    pass
            else:
                self.graphNodes[change[0]][change[1]] = change[2]
                self.graphNodes[change[1]][change[0]] = change[2]        

    """ @brief Runs the logic for Distance Vector routing protocol.
     *
     *  @param topologyFile     The file containing the network topology.
     *  @param messageFile      The file containing the messages to be sent.
     *  @param changesFile      The file containing the topology changes.
     *  @param outputFile       The file to write the output to.
    """    
    def run(self, topologyFile, messageFile, changesFile, outputFile):
        #Checks if files exist
        if not os.path.exists(topologyFile):
            print("Topology file does not exist.")
            return
        if not os.path.exists(messageFile):
            print("Message file does not exist.")
            return
        if not os.path.exists(changesFile):
            print("Topology Changes file does not exist.")
            return   

        #Creates topology, forwarding table, and sends messages.
        self.read_topology(topologyFile)
        self.forwarding_table(outputFile)
        self.read_message(messageFile)
        self.send_messages(outputFile)
        
        #Applies topology changes and updates FW table and messages per update.
        topologyChanges = self.read_topology_changes(changesFile)
        for change in topologyChanges:
            self.apply_topology_change([change])
            self.forwarding_table(outputFile)
            self.send_messages(outputFile)


""" @brief Main function that instantiates and runs Router.
 *
 *  @return Should not return. 
"""
if __name__ == "__main__":
    if (len(sys.argv) != 5):
        print("Format: ./dvr.sh <topologyFile> <messageFile> <changesFile> [outputFile]")
        sys.exit(1)

    topologyFile = sys.argv[1]
    messageFile = sys.argv[2]
    changesFile = sys.argv[3]
    outputFile = sys.argv[4]

    #Instantiates router.
    router = Router()
    router.run(topologyFile, messageFile, changesFile, outputFile)