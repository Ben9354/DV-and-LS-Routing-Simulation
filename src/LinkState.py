""" @file LinkState.py
 *  @brief Link State routing protocol.
 * 
 *  Reads topology file and creates topology graph network. Then creates and prints forwarding tables for each node using Dijkstra's algorithm.
 *  Reads and sends messages via the forwarding tables. Applies any topology changes and repeats the previous two steps.
 * 
 *  @author Benjamin Chung
 *  @bug When printing the routing tables, the order is not enforced.
 *  (One can tell which table it is via the destination as itself and cost as 0).
"""
from dijkstar import Graph, find_path
import sys
import os.path

class Router:

    """ @brief Initalizes graph network using the dijkstar library, 
     *  forwarding table as a dictionary, and list of messages to be stored.
     *
    """
    def __init__(self):
        self.graphNodes = Graph()
        self.forwardingTables = {}
        self.messages = []
    
    """ @brief Reads the topology file and creates the graph network using the dijkstar library.
     *
     *  @param topologyFile     The file containing the network topology.
    """
    def read_topology(self, topologyFile):
        with open(topologyFile, 'r') as topFile:
            for line in topFile:
                node1, node2, cost = map(int, line.split())
                self.graphNodes.add_edge(node1, node2, cost)
                self.graphNodes.add_edge(node2, node1, cost)

    """ @brief Creates the forwarding table for each node in the network using Link State routing.
     *
     *  @param outputFile   File to write the forwarding table to.
    """
    def forwarding_table(self, outputFile):
        with open(outputFile, 'a') as outFile:
            for node in self.graphNodes:
                outFile.write(f"\n")
                #Iterates through each destination per node.
                for dest in self.graphNodes:
                    #Initalizes destination for per node in forwarding table.
                    if node not in self.forwardingTables:
                        self.forwardingTables[node] = {}
                    #Finds the shortest path along with total cost from node to destination using Dijkstra's algorithm.
                    path = find_path(self.graphNodes, node, dest)
                    if (path is not None):
                        #Appends the shortest path as a list to the forwarding table along with its total cost.
                        self.forwardingTables[node][dest] = (path.nodes, path.total_cost)
                        cost = path.total_cost
                        #If there is no avaliable path, the next hop will be to its self with a cost of 0.
                        if(len(path.nodes) > 1):
                            nextHop = path.nodes[1]
                        else:
                            nextHop = node

                        outFile.write(f"{dest} {nextHop} {cost} \n")
            outFile.write(f"\n")

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
                        path = self.forwardingTables[source][dest][0]
                        cost = self.forwardingTables[source][dest][1]
                        outFile.write(f"from {source} to {dest} cost {cost} hops {' '.join(map(str, path[:-1]))} message {message} \n")
                    else:
                        outFile.write(f"from {source} to {dest} cost infinite hops unreachable message {message} \n")

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
                self.graphNodes.remove_edge(change[0], change[1])
                #In case edge has not been removed above.
                try:
                    self.graphNodes.remove_edge(change[1], change[0])
                except KeyError:
                    pass
            else:
                self.graphNodes.add_edge(change[0], change[1], change[2])
                self.graphNodes.add_edge(change[1], change[0], change[2])

    """ @brief Runs the logic for Link State routing protocol.
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
        print("Format: ./lsr.sh <topologyFile> <messageFile> <changesFile> [outputFile]")
        sys.exit(1)

    topologyFile = sys.argv[1]
    messageFile = sys.argv[2]
    changesFile = sys.argv[3]
    outputFile = sys.argv[4]
    
    #Instantiates router.
    router = Router()
    router.run(topologyFile, messageFile, changesFile, outputFile)