#!/usr/bin/python

"""
http://www.multipath-tcp.org/
http://blog.multipath-tcp.org/blog/html/2014/09/16/recommended_multipath_tcp_configuration.html
http://blog.multipath-tcp.org/blog/html/2015/02/06/mptcptrace_demo_experiment_five.html
http://mininet.org/api/classmininet_1_1net_1_1Mininet.html
https://github.com/mininet/mininet/blob/master/mininet/node.py
https://www.wireshark.org/docs/man-pages/tshark.html
https://www.wireshark.org/docs/dfref/t/tcp.html
http://www.packetlevel.ch/html/tcpdumpf.html
tshark -G | grep Multipath
https://iperf.fr/iperf-doc.php
https://github.com/ouya/iperf/
https://docs.python.org/2/library/xml.etree.elementtree.html
http://effbot.org/downloads#elementtree
https://github.com/remichauvenne/mptcp-model-thesis
"""

"""
questions:
 - what is a mininet.controller (c0)? why it's not working without that?
 - why are host trend to be behind a switch?
 - how to meansure/monitor bandwith/delay?
 - iperf 'Connection refused' sometimes...
 - double delay on the first ping
 - iperf freeze if swith's interface turn down, but good handover if host's intf down
 - mininet learn between runs, ping breaks arp/handover ?!?!?!?!?!?!?!???
 - 
Notes:
 - run program on a host: run long process at background and pipe it's output to file, so other short processes can run meanwhile (sendCmd don't block the caller script, but sets waiting to True)
"""


### CONFIGURATIONS ###

#sysctl net.mptcp
#sysctl net | grep congestion
#sysctl net | grep 'mptcp\|congestion'

"congestion controls:"
#os.system('sysctl -w net.ipv4.tcp_congestion_control=cubic ')
#os.system('modprobe mptcp_coupled && sysctl -w net.ipv4.tcp_congestion_control=lia ')
#os.system('modprobe mptcp_olia && sysctl -w net.ipv4.tcp_congestion_control=olia ')
#os.system('modprobe mptcp_wvegas && sysctl -w net.ipv4.tcp_congestion_control=wvegas ')
#os.system('modprobe mptcp_balia && sysctl -w net.ipv4.tcp_congestion_control=balia ')

"path-managers:"
#os.system('sysctl -w net.mptcp.mptcp_path_manager=default ')
#os.system('sysctl -w net.mptcp.mptcp_path_manager=fullmesh ')
#os.system('echo 1 | sudo tee /sys/module/mptcp_fullmesh/parameters/num_subflows')
#os.system('modprobe mptcp_ndiffports && sysctl -w net.mptcp.mptcp_path_manager=ndiffports ')
#os.system('echo 1 | sudo tee /sys/module/mptcp_ndiffports/parameters/num_subflows')
#os.system('modprobe mptcp_binder && sysctl -w net.mptcp.mptcp_path_manager=binder ')

"scheduler:"
#os.system('sysctl -w net.mptcp.mptcp_scheduler=default ')
#os.system('modprobe mptcp_rr && sysctl -w net.mptcp.mptcp_scheduler=roundrobin ')
#os.system('echo 1 | sudo tee /sys/module/mptcp_rr/parameters/num_segments')
#os.system('echo Y | sudo tee /sys/module/mptcp_rr/parameters/cwnd_limited')
#os.system('modprobe mptcp_redundant && sysctl -w net.mptcp.mptcp_scheduler=redundant ')


import time
import os,signal
import sys
import re
import xml.etree.ElementTree
from mininet.net import Mininet
from mininet.link import TCLink
import subprocess
test_bandwith = True
capture_mptcp_headers =True
cut_a_link = True
add_a_link = True
max_queue_size = 100
use_custom_meter = False
test_duration = 200 # seconds
os.system('sysctl -w net.mptcp.mptcp_path_manager=fullmesh ')
os.system('modprobe mptcp_rr && sysctl -w net.mptcp.mptcp_scheduler=roundrobin ')
#os.system('modprobe mptcp_olia && sysctl -w net.ipv4.tcp_congestion_control=cubic')
os.system('echo 3 | sudo tee /sys/module/mptcp_fullmesh/parameters/num_subflows')
net = Mininet( cleanup=True )

h1 = net.addHost( 'h1', ip='10.0.1.1')
h2 = net.addHost( 'h2', ip='10.0.2.1')

s3 = net.addSwitch( 's3' )
s4 = net.addSwitch( 's4' )
c0 = net.addController( 'c0' )

net.addLink( h1, s3, cls=TCLink , bw=2, delay='30ms', max_queue_size=max_queue_size )
net.addLink( h1, s4, cls=TCLink , bw=2, delay='10ms', max_queue_size=max_queue_size )
net.addLink( h2, s3, cls=TCLink , bw=2, delay='10ms', max_queue_size=max_queue_size )
net.addLink( h2, s4, cls=TCLink , bw=2, delay='10ms', max_queue_size=max_queue_size )


h1.setIP('10.0.1.1', intf='h1-eth0')
h1.setIP('10.0.1.2', intf='h1-eth1')

h2.setIP('10.0.2.1', intf='h2-eth0')
h2.setIP('10.0.2.2', intf='h2-eth1')

net.start()
time.sleep(1)
print "host1 ip",h1.IP()
print "host2 ip", h2.IP()
p3=h1.popen("tcpdump -XX -n -i h1-eth0 -w /home/zsy/MyTest/go/h1eth0.pcap")
p4=h1.popen("tcpdump -XX -n -i h1-eth1 -w /home/zsy/MyTest/go/h1eth1.pcap")
p2 = h2.popen("./externaludp/mytcpserver -h"+h2.IP()+' -p1234')
p1=h1.popen("./externaludp/fileclient -h"+h2.IP()+' -p1234')
while 1:
    time.sleep(1)
    ret=subprocess.Popen.poll(p1)
    if ret is None:
    	continue
    else:
    	break
time.sleep(10)
os.killpg(os.getpgid(p2.pid),signal.SIGTERM)
subprocess.Popen.kill(p3)
subprocess.Popen.kill(p4)
p2.wait();
p3.wait();
p4.wait();
c0.stop();
net.stop()

print
