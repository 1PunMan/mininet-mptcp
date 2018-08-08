# mininet-mptcp
Some experiment mptcp test on mininet  
please substitue you own tcp client serser. Of course, the code of mytcpserver mytcpserver can get at https://github.com/sonyangchang/mininet-test/tree/master/tcpudp   
p2 = h2.popen("./tcpudp/mytcpserver -h10.0.2.2 -p1234")  
p1=h1.popen("./tcpudp/fileclient -h10.0.2.2 -p1234")  
And the fileclient send out 10MB data to the server. The flow completion time can get in my_tcp_server_log.txt.  
results   
mp flow completion time 22473  ms   
sp   
44640 ms   

The configuration about mptcp can refer to mptcp_test.py, and the file is from https://gist.github.com/tovask/316f0dc855f2459042af403688590a7f   
