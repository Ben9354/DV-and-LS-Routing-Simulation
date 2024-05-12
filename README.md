/**

@mainpage ELEC 331 Programming Assignment 2

@author Benjamin Chung

The two programs DistanceVector.py and LinkState.py are two indpendent programs that can be instantiated via ./dvr.sh <topologyFile> <messageFile> <changesFile> [outputFile] and ./lsr.sh <topologyFile> <messageFile> <changesFile> [outputFile], respectively. 

We have tested both programs using the test files (topology, messages, and changes) under TEST. Our output for both programs are listed under the output file, in which both have been able to produce the same output.
However, the order of the destinations for per node in the routing table have been neglected.
For DistanceVector, the destination path for each node it lists in the message output is only the nextHop as intended, since each node should only know the next hop in which it should route packets to.

Our main source of references used were:
https://www.youtube.com/watch?v=bdh2kfgxVuw
https://www.youtube.com/watch?v=jJU2AVX6gpU

*/