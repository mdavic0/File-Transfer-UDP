from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

PACKET_LOSS = 10

def create_network():
    net = Mininet(autoStaticArp=True, waitConnected=True)
    net.addController('c0')

    server = net.addHost('h1')

    clients = []
    for i in range(2, 5):
        client = net.addHost(f'h{i}')
        clients.append(client)
    
    s1 = net.addSwitch('s1')
    
    serverLink = net.addLink(server, s1, cls=TCLink)

    clientLinks = []
    for client in clients:
        clientLink = net.addLink(client, s1, cls=TCLink)
        clientLinks.append(clientLink)

    net.start()
    server_start = net.get('h1')
    server_start.setIP('10.168.0.1/24')
    
    for i in range(2, 5):
        client = net.get(f'h{i}')
        client.setIP(f'10.168.0.{i + 1}/24')

    serverLink.intf1.config(loss=PACKET_LOSS)   
    for clientLink in clientLinks:
        clientLink.intf1.config(loss=PACKET_LOSS)
    server_ip = net.get('h1').IP()
    print(f"Server ip = {server_ip}")
    for i in range(2, 5):
        client = net.get(f'h{i}')
        print(f"Client{i} ip = {client.IP()}")

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_network()