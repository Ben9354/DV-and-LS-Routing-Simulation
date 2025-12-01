The two programs DistanceVector.py and LinkState.py are two independent programs that can be instantiated via ./dvr.sh <topologyFile> <messageFile> <changesFile> [outputFile] and ./lsr.sh <topologyFile> <messageFile> <changesFile> [outputFile], respectively. 

Both programs have been tested using the test files (topology, messages, and changes) under TEST. The outputs for both programs are listed under the output file, in which both have been able to produce the same output.
However, the order of the destinations for per node in the routing table have been neglected.
For DistanceVector, the destination path for each node it lists in the message output is only the nextHop as intended, since each node should only know the next hop in which it should route packets to.

Prompt: https://www.studocu.com/en-us/document/university-of-illinois-at-urbana-champaign/communication-networks/uiuc-cs438-2024-spring-mp3/116329154
