# Noobcash ₿ 🔗
## About the Project
Simple Blockchain System for NTUA ECE Course Distributed Systems


<p align="center">
  <img src= "https://github.com/nafsika24/Noobcash/blob/main/screenshots/LOGO.png"  width="40%" height="50%">
</p>

## Built With:
* Python
* Flask
* HTML/CSS
* JQuery

## Web Interface 
<p align="center">
  <img src= "https://github.com/nafsika24/Noobcash/blob/main/screenshots/gif.gif"  width="80%" height="70%">
</p>

## CLI
<p align="center">
  <img src= "https://github.com/nafsika24/Noobcash/blob/main/screenshots/gif_cli.gif"  width="80%" height="70%">
</p>

## Description 
The user can interact with the system by using a simple CLI or the Webapp Interface. In Noobcash App you will register nodes and simulate a blockchain system, through processes of sending and receiving money(NBC Coins), consensus, proof of work, mining etc. At the start of the system the first node to register should be the bootstrap node who will create the genesis block. After all the "children" nodes have registered the bootstrap node will give each one of them 100 NBC. Now the transactions can begin.

## Set Up
Inside the folder Project:
* pip install -r requirements.txt
* npm install

## Run Application
* bootstrap node: ``python <PORT> <IP> <Number of Children in the System> true``
 example: ``python 5000 127.0.0.1 2 true``
* simple node: ``python <PORT> <IP> <Number of Children in the System> no``
 example: ``python 5001 127.0.0.1 2 false``
* Open Web Interface: Open at your browser the IP and PORT the node is registered.
* Run CLI: ``cli.py <PORT> <IP>``

If you want to run the tests inside the folders 5nodes and 10nodes replace app.py with app_auto.py.

## Collaborators

[DImitrios Dimos](https://github.com/d-dimos)

[Nikolaos Christopoulos](https://github.com/christopni)




