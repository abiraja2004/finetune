FROM tensorflow/tensorflow:1.11.0-gpu-py3
LABEL Author="Ben Townsend, Madison May"

# tensorboard
EXPOSE 6006

# nvidia-docker 1.0
LABEL com.nvidia.volumes.needed="nvidia_driver"
LABEL com.nvidia.cuda.version="${CUDA_VERSION}"

# nvidia-container-runtime
ENV NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility \
    NVIDIA_REQUIRE_CUDA="cuda>=8.0" \
    LANG=C.UTF-8 \
    CUDA_DEVICE_ORDER=PCI_BUS_ID

RUN apt-get update && mkdir /Finetune
ADD requirements.txt /Finetune/requirements.txt
RUN pip3 install -r /Finetune/requirements.txt && \
    python3 -m spacy download en

WORKDIR /Finetune
ADD . /Finetune
RUN python3 setup.py develop

CMD ["sleep","infinity"]
