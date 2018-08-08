# mininet-mptcp
Some experiment mptcp test on mininet  
please substitue you own tcp client serser. Of course, the code of mytcpserver mytcpserver can get at https://github.com/sonyangchang/mininet-test/tree/master/tcpudp   
p2 = h2.popen("./tcpudp/mytcpserver -h10.0.2.2 -p1234")  
p1=h1.popen("./tcpudp/fileclient -h10.0.2.2 -p1234")  
