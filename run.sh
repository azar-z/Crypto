input="$1"

sudo docker-compose build &&
  sudo docker-compose up --remove-orphans