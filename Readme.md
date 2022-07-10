## конфиг для docker-compose

    image_storage:
      build: https://github.com/Eldies/image_storage.git
      restart: always
      environment:
        UPLOAD_FOLDER: /uploads
        CLIENT_CREDENTIALS_1: client:api_key
      ports:
        - <порт>:5000
      deploy:
        resources:
          limits:
            cpus: '0.2'
      volumes:
        - ${DOCKER_CONTAINERS_DATA_FOLDER}/image_storage:/uploads
