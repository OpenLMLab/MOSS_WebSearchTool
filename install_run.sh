
#git clone https://github.com/piglaker/MOSS_Retrieval.git

FILE=serper_key
if [ -f "$FILE" ]; then
    echo "$FILE exist"
else
    echo -n "Enter your key:"
    read key
    echo ${key} > serper_key
fi

if [[ $(which docker) && $(docker --version) ]]; then
    echo "检查到Docker已安装!"
  else
    echo "安装docker环境..."
    curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
    echo "安装docker环境...安装完成!"
fi

systemctl start docker

docker login
docker pull piglake/retrieval:0.7

CC_EN=cc.en.300.bin.gz
CC_ZH=cc.zh.300.bin.gz

if [ -f "$CC_EN" ]; then
    echo "$CC_EN exist"
else
    wget https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.300.bin.gz
fi

if [ -f "$CC_ZH" ]; then
    echo "$CC_ZH exist"
else
    wget https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.zh.300.bin.gz
fi

EN_Bin=cc.en.300.bin
ZH_Bin=cc.zh.300.bin

if [ -f "$EN_Bin" ]; then
    echo "$EN_Bin exist"
else
    gunzip cc.en.300.bin.gz
fi

if [ -f "$ZH_Bin" ]; then
    echo "$ZH_Bin exist"
else
    gunzip cc.zh.300.bin.gz
fi


bash docker_run_retrieval.sh
