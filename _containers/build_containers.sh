### This file will build and run all of our images and containers in order for our app to function correctly

#0. GO TO folder
chmod -R 777 ./
cwd=$(pwd)

docker rm -f torchserve_docker || True
docker rm -f mysql-db || True
docker rm -f tfserving || True
docker rm -f test-mongo || True

#1. torchserve
if [[ $(grep avx /proc/cpuinfo) ]]; then
    echo "Available avx instruction set"
    TENSORFLOW_UP=true
    docker build -t ubuntu-torchserve:latest _containers/_torchserve/
    docker run --rm --name torchserve_docker \
                -d \
            -p8080:8080 -p8081:8081 -p8082:8082 \
            ubuntu-torchserve:latest \
            torchserve --model-store /home/model-server/model-store/ --models object_count=fastrcnn.mar

else
    echo "Unavailable avx instruction set. Can not mount version of Tensorflow-Serving docker image."
    TENSORFLOW_UP=false 
fi

# mysql part1 - Runing the mysql container in between as it needs time to load
docker run -d -p 3306:3306 --name mysql-db -e MYSQL_ROOT_PASSWORD=secret mysql

#2. tensorflow-serving
./_containers/_tensorflow_serving/build_TF_container.sh

#3. mongodb
docker run --name test-mongo --rm --net host -d mongo:latest

#4. mysql part2 - It needed some seconds before executing 
docker exec -i mysql-db mysql -uroot -psecret mysql < _containers/_mysql/counter_obj.sql

#5. Inform process as finish
echo  \ 
echo "---------------CONTAINERS UP AND RUNNING--------------"
if [ "$TENSORFLOW_UP" = false ] ; then
    echo "---------------TENSORFLOW SERVING CONTAINER CAN NOT BEEN INSTANTIATED--------------"
fi
