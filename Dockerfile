FROM continuumio/anaconda3
COPY . /app
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN install_packages libc-dev libatlas3-base libgfortran5
RUN pip install -r requirements.txt -i https://www.piwheels.org/simple --extra-index-url https://pypi.org/simple
CMD ["python", "server.py"]