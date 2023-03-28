echo "try to stop retrieval container "
docker stop retrieval
echo "wait while docker daemon clean "
sleep 1
echo "running container"
bash docker_run.sh

