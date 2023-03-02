wget https://storage.googleapis.com/intel-optimized-tensorflow/models/v1_8/rfcn_resnet101_fp32_coco_pretrained_model.tar.gz

tar -xzvf rfcn_resnet101_fp32_coco_pretrained_model.tar.gz -C .
rm rfcn_resnet101_fp32_coco_pretrained_model.tar.gz
chmod -R 777 ./rfcn_resnet101_coco_2018_01_28
mv ./rfcn_resnet101_coco_2018_01_28/saved_model/saved_model.pb _containers/_tensorflow_serving/model/1
rm -rf ./rfcn_resnet101_coco_2018_01_28

model_name=rfcn
cores_per_socket=`lscpu | grep "Core(s) per socket" | cut -d':' -f2 | xargs`
num_sockets=`lscpu | grep "Socket(s)" | cut -d':' -f2 | xargs`
num_physical_cores=$((cores_per_socket * num_sockets))
echo $num_physical_cores

docker run \
    --name=tfserving \
    -d \
    -p 8500:8500 \
    -p 8501:8501 \
    -v "$(pwd)/_containers/_tensorflow_serving/model:/models/$model_name" \
    -e MODEL_NAME=$model_name \
    -e OMP_NUM_THREADS=$num_physical_cores \
    -e TENSORFLOW_INTRA_OP_PARALLELISM=$num_physical_cores \
    intel/intel-optimized-tensorflow-serving:latest