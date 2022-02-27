## конфиг для docker-compose

    image_storage:
      build: git@github.com:Eldies/image_storage.git
      restart: always
      environment:
        UPLOAD_FOLDER: /uploads
        CLIENT_API_KEY: ${IMAGE_STORAGE_CLIENT_API_KEY}
      ports:
        - <порт>:5000
      deploy:
        resources:
          limits:
            cpus: '0.2'
      volumes:
        ${DOCKER_CONTAINERS_DATA_FOLDER}/image_storage:/uploads
