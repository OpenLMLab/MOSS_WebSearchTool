http http://127.0.0.1:7004/

netstat -s | egrep "listen|LISTEN"

iptables -L -v

tcpdump port 8000 -i lo

ss -lnt
