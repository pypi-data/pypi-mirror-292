# DecentMesh Network

```
                *                       
                          *             
                    **   *              
                                        
                 *    **                
           *     ***    *   **          
                      **                
 __   ___  __   ___      ___        ___  __       
|  \ |__  /  ` |__  |\ |  |   |\/| |__  /__` |__| 
|__/ |___ \__, |___ | \|  |   |  | |___ .__/ |  | 
                *     *                 
           *      *        *            
           *   *                        
             *   *                      
                 *                      
                      *                 
               *     *   *              
                   *                    
```

DecentMesh Network is a decentralized and resilient network framework designed to facilitate secure, efficient, and scalable connectivity for
distributed applications.

It enables seamless node discovery, robust communication, and easy management of decentralized environments, empowering
developers to build and maintain decentralized networks with minimal complexity.
With DecentMesh, you can effortlessly connect, monitor, and manage
nodes, ensuring reliable communication across your network.
Ideal for projects requiring high availability and security, DecentMesh simplifies the
challenges of decentralized networking.

## Installation

### Prerequisites

Before you begin, ensure you have the following installed on your Debian-based system:

```bash
sudo apt-get install autoconf automake libtool
```

### Requirement for running a Node

* Redis capable of Pub/Sub

### How to run node

```bash
decentmesh service start 127.0.0.1 8888
```