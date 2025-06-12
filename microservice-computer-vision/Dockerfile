FROM python:3.9
COPY video.bag /data/video.bag
RUN apt update && apt -y install libgl1-mesa-glx libusb-1.0-0-dev
COPY src/ /code
COPY build_temp/dummy_dvde_api.py code/
WORKDIR /code
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt
CMD python3 run.py -i /data/video.bag