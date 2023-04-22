version="7"
##--net=host\
#--env http_proxy="http://10.176.52.116:7890" --env https_proxy="http://10.176.52.116:7890"
#--env https_proxy="http://10.176.50.14:7890" --env http_proxy="http://10.176.50.14:7890" --env all_proxy="socks5://10.176.50.14:7891"
docker run -d --rm --name="retrieval" --privileged --cap-add=SYS_PTRACE --shm-size=200g \
-w /retrieval -p7004:7004  \
-v `pwd`:/retrieval piglake/retrieval:0.${version} \
python3 retrieval_backend.py --port 7004 --timeout 60000
