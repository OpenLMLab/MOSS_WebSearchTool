
#git clone https://github.com/piglaker/MOSS_Retrieval.git

FILE=serper_key
if [ -f "$FILE" ]; then
    echo "$FILE exist"
else
    echo -n "Enter your key:"
    read key
    echo ${key} > serper_key
fi

docker -v
if [ $? - eq 0 ] ; then
    echo "检查到Docker已安装!"
else
    echo "安装docker环境..."
    curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
    echo "安装docker环境...安装完成!"
fi

docker login
docker pull piglake/retrieval:0.7

yum install git

cd MOSS_Retrieval

wget https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.300.bin.gz
wget https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.zh.300.bin.gz

gunzip cc.en.300.bin.gz
gunzip cc.zh.300.bin.gz

bash docker_run_retrieval.sh
