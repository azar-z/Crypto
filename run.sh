sudo service redis stop &&
sudo service postgresql stop &&
sudo systemctl restart docker &&
docker-compose up --remove-orphans
