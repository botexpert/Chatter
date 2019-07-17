# Chatter - the extensible chat application

This repository contains specification for the extensible chat application - Chatter.


## Prerequisites

Before implementation is started, followings links need to be studied first:

1. [Git - Getting Started](https://git-scm.com/book/en/v1/Getting-Started),
2. [Beginner's Guide to Python](https://wiki.python.org/moin/BeginnersGuide),
3. [ZeroMQ - The Guide](http://zguide.zeromq.org/page:all).

## Problem definition

*Chatter* is a cross-platform messaging application. It allows users to send text messages
and voice messages. 

*Chatter* allows following ways of communication:

* One-on-one communication, where clients can communicate directly without a server,
* Client-server communication, where clients utilize the server in order to communicate.

Both clients and server communicate by either by exchanging JSON messages, or messages defined
by the custom *Domain-specific language*. Messages are transported via ZeroMQ library.

Clients and server are implemented in a fault tolerant way. In the client-server communication,
this means that clients will not crash if the server is not available, but also server will
stack messages intended for a client that is unavailable at that moment. In the context of 
*One-on-one*, fault tolerance means that a client will not crash if the other client is unavailable.


## Useful links

* [Client–server model](https://en.wikipedia.org/wiki/Client%E2%80%93server_model)
* [PythonQt](https://wiki.python.org/moin/PyQt)
* [Domain-specific languages](http://www.igordejanovic.net/courses/jsd.html)


## Licence

MIT
