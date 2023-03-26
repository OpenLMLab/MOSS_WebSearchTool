
#git clone https://github.com/piglaker/MOSS_Retrieval.git
echo -n "Enter your key:"

read key

echo ${key} > serper_key

curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun

docker login

docker pull piglake/retrieval:0.7

yum install git

cd MOSS_Retrieval

wget https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.300.bin.gz
wget https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.zh.300.bin.gz

gunzip cc.en.300.bin.gz
gunzip cc.zh.300.bin.gz

bash docker_run_retrieval.sh
