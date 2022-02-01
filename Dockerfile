FROM continuumio/anaconda3
COPY . /app
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN conda install pip && pip install -r requirements.txt && mkdir temp_images
CMD ["python", "server.py"]