#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import TCLink
import time
import subprocess
import os,signal
##https://serverfault.com/questions/417885/configure-gateway-for-two-nics-through-static-routeing
#    ____h2____
#   /          \
# h1           h3
#   \___h4_____/
#
#os.system('modprobe mptcp_olia && sysctl -w net.ipv4.tcp_congestion_control=olia ')
#os.system('modprobe mptcp_wvegas && sysctl -w net.ipv4.tcp_congestion_control=wvegas ')
#os.system('modprobe mptcp_balia && sysctl -w net.ipv4.tcp_congestion_control=balia ')
max_queue_size = 100 
os.system('sysctl -w net.mptcp.mptcp_path_manager=fullmesh ')
os.system('modprobe mptcp_rr && sysctl -w net.mptcp.mptcp_scheduler=roundrobin ')
os.system('modprobe mptcp_olia && sysctl -w net.ipv4.tcp_congestion_control=olia ')
os.system('echo 3 | sudo tee /sys/module/mptcp_fullmesh/parameters/num_subflows')
net = Mininet( cleanup=True )
h1 = net.addHost('h1',ip='10.0.1.1')
h2 = net.addHost('h2',ip='10.0.1.2')
h3 = net.addHost('h3',ip='10.0.2.2')
h4 = net.addHost('h4',ip='10.0.3.2')
c0 = net.addController( 'c0' )
net.addLink(h1,h2,intfName1='h1-eth0',intfName2='h2-eth0', cls=TCLink , bw=2, delay='10ms', max_queue_size=max_queue_size)
net.addLink(h2,h3,intfName1='h2-eth1',intfName2='h3-eth0', cls=TCLink , bw=2, delay='10ms', max_queue_size=max_queue_size)
net.addLink(h1,h4,intfName1='h1-eth1',intfName2='h4-eth0', cls=TCLink , bw=2, delay='30ms', max_queue_size=max_queue_size)
net.addLink(h4,h3,intfName1='h4-eth1',intfName2='h3-eth1', cls=TCLink , bw=2, delay='30ms', max_queue_size=max_queue_size)
net.build()
h1.setIP('10.0.1.1', intf='h1-eth0')
h1.cmd("ifconfig h1-eth0 10.0.1.1 netmask 255.255.255.0")

h1.setIP('10.0.3.1', intf='h1-eth1')
h1.cmd("ifconfig h1-eth1 10.0.3.1 netmask 255.255.255.0")

h1.cmd("ip route flush all proto static scope global")
h1.cmd("ip route add 10.0.1.1/24 dev h1-eth0 table 5000")
h1.cmd("ip route add default via 10.0.1.2 dev h1-eth0 table 5000")

h1.cmd("ip route add 10.0.3.1/24 dev h1-eth1 table 5001")
h1.cmd("ip route add default via 10.0.3.2 dev h1-eth1 table 5001")
h1.cmd("ip rule add from 10.0.1.1 table 5000")
h1.cmd("ip rule add from 10.0.3.1 table 5001")
h1.cmd("route add default gw 10.0.1.2  dev h1-eth0")

h2.setIP('10.0.1.2', intf='h2-eth0')
h2.setIP('10.0.2.1', intf='h2-eth1')
h2.cmd("ifconfig h2-eth0 10.0.1.2/24")
h2.cmd("ifconfig h2-eth1 10.0.2.1/24")
h2.cmd("ip route add 10.0.2.0/24 via 10.0.2.2")
h2.cmd("ip route add 10.0.1.0/24 via 10.0.1.1")
h2.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")


h4.setIP('10.0.3.2', intf='h4-eth0')
h4.setIP('10.0.4.1', intf='h4-eth1')
h4.cmd("ifconfig h4-eth0 10.0.3.2/24")
h4.cmd("ifconfig h4-eth1 10.0.4.1/24")
h4.cmd("ip route add 10.0.4.0  dev h4-eth1") #via 10.0.4.2
h4.cmd("ip route add 10.0.3.0 via 10.0.3.1")

h4.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")


h3.setIP('10.0.2.2', intf='h3-eth0')
h3.cmd("ifconfig h3-eth0 10.0.2.2 netmask 255.255.255.0")
h3.setIP('10.0.4.2', intf='h3-eth1')
h3.cmd("ifconfig h3-eth1 10.0.4.2 netmask 255.255.255.0")

h3.cmd("ip route flush all proto static scope global")
h3.cmd("ip route add 10.0.2.2/24 dev h3-eth0 table 5000")
h3.cmd("ip route add default via 10.0.2.1 dev h3-eth0 table 5000")

h3.cmd("ip route add 10.0.4.2/24 dev h3-eth1 table 5001")
h3.cmd("ip route add default via 10.0.4.1 dev h3-eth1 table 5001")
h3.cmd("ip rule add from 10.0.2.2 table 5000")
h3.cmd("ip rule add from 10.0.4.2 table 5001")

net.start()
time.sleep(1)
#p3=h1.popen("tcpdump -XX -n -i h1-eth0 -w /home/zsy/MyTest/go/h1eth0.pcap")
#p4=h1.popen("tcpdump -XX -n -i h1-eth1 -w /home/zsy/MyTest/go/h1eth1.pcap")
p2 = h2.popen("./externaludp/mytcpserver -h10.0.2.2 -p1234")
p1=h1.popen("./externaludp/fileclient -h10.0.2.2 -p1234")
while 1:
    time.sleep(1)
    ret=subprocess.Popen.poll(p1)
    if ret is None:
    	continue
    else:
    	break
time.sleep(10)
os.killpg(os.getpgid(p2.pid),signal.SIGTERM)
#subprocess.Popen.kill(p3)
#subprocess.Popen.kill(p4)
p2.wait();
#p3.wait();
#p4.wait();
net.stop()
print "stop"
