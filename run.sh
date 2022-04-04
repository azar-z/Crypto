input="$1"

if [ "$input" = "development" ]; then
  echo "development mode..." &&
    echo "PROJECT ROOT DIR:" &&
    echo $(pwd) &&
    cp configs/docker-compose-development.conf docker-compose.yml &&
    echo "DONE"
else
  echo "production mode..." &&
    echo "PROJECT ROOT DIR:" &&
    echo $(pwd) &&
    cp configs/docker-compose-production.conf docker-compose.yml &&
    echo "DONE"
fi

sudo docker-compose build &&
  sudo docker-compose up --remove-orphans
