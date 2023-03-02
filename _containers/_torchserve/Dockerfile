ARG BASE_IMAGE="ubuntu:latest"
FROM ${BASE_IMAGE}

ENV PYTHONUNBUFFERED TRUE

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    ca-certificates \
    g++ \
    python3-dev \
    python3-distutils \
    python3-venv \
    openjdk-11-jre-headless \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && cd /tmp \
    && curl -O https://bootstrap.pypa.io/get-pip.py \
    && python3 get-pip.py \
    && rm get-pip.py

RUN python3 -m venv /home/venv

ENV PATH="/home/venv/bin:$PATH"

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1
RUN update-alternatives --install /usr/local/bin/pip pip /usr/local/bin/pip3 1

RUN pip install -U pip setuptools
RUN pip install torch==1.12.0+cpu torchvision==0.13.0+cpu torchaudio==0.12.0 --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install torchserve==0.2.0 torch-model-archiver==0.2.0

RUN useradd -m model-server

COPY dockerd-entrypoint.sh /usr/local/bin/dockerd-entrypoint.sh
COPY config.properties /home/model-server/config.properties
COPY model /home/model-server/model
RUN mkdir /home/model-server/model-store

RUN chmod +x /usr/local/bin/dockerd-entrypoint.sh \
    && mkdir -p /home/model-server/tmp \
    && chown -R model-server /home/model-server \
    && chown -R model-server /home/venv

RUN chown -R model-server /home/model-server/model-store \
    && cd /home/model-server/model-store

RUN wget https://download.pytorch.org/models/fasterrcnn_resnet50_fpn_coco-258fb6c6.pth

RUN torch-model-archiver    --model-name fastrcnn \
                            --version 1.0 \
                            --model-file /home/model-server/model/model.py \
                            --serialized-file fasterrcnn_resnet50_fpn_coco-258fb6c6.pth \
                            --handler object_detector \
                            --extra-files /home/model-server/model/index_to_name.json

RUN rm fasterrcnn_resnet50_fpn_coco-258fb6c6.pth
RUN mv fastrcnn.mar /home/model-server/model-store    

EXPOSE 8080 8081 8082

USER model-server
WORKDIR /home/model-server
ENV TEMP=/home/model-server/tmp
ENTRYPOINT ["/usr/local/bin/dockerd-entrypoint.sh"]
CMD ["serve"]