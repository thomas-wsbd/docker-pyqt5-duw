FROM python:3.9-slim

COPY ./requirements.txt tmp/requirements.txt

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    make \
    gcc \
    locales \
    libgdal20 libgdal-dev\
    qt5-default\
    python3-pyqt5 && \
    python -m pip --no-cache-dir install --upgrade pip setuptools wheel && \
    python -m pip --no-cache-dir install numpy cython --no-binary numpy,cython && \
    python -m pip --no-cache-dir install \
    "rasterio>=1.0a12" fiona shapely \
    --pre --no-binary rasterio,fiona,shapely && \
    python -m pip --no-cache-dir install --no-use-pep517 -r tmp/requirements.txt --no-binary sip &&\
    python -m pip --no-cache-dir install pyqt5==5.15.4, PyQtWebEngine --no-binary pyqt5,pyqtwebengine &&\
    python -m pip uninstall -y cython && \
    rm -r /root/.cache/pip && \
    apt-get remove -y --purge libgdal-dev make gcc build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /

COPY . /

ENTRYPOINT [ "python3" ]

CMD [ "app/app.py" ]