## Synopsis

Setup guide for my HomeAssistant instance

## Hardware

- Sony Vaio VGN-TZ37GN_B
- Aeotec Z-Wave USB Gen 5
- Aeotec Multisensor 6
- Xiaomi Aqara Gateway
- Xiaomi Aqara Door/Window Sensors x4
- Xiaomi Aqara Motion Sensors x4
- Xiaomi Mi Powerpoints x3
- Xiaomi Mi IR
- Philips Hue Hub
- Philips Hue Colour x4
- Harmony Hub
- Amazon Echo Dot
- ~~4x~~ 2x Chromecasts (long-term to be replaced with Sonos)
- Sonos PLAYBAR
- Sonos One x2

## Components

- Docker
- sudo
- Motion

## Installation

- Install and update Debian 9 (Stretch)
- Set Aeotec USB stick to persistent device name

## Transition to Docker

### Introduction
This section will be updated as I gradually move components into Docker containers. 

The intent behind this is to make updates of individual components easier with less risk of breaking a common dependency, as well as making backups and restorations easier.

As components are shifted to Docker the installation steps will be removed from above and entered below.

### Docker
```
apt-get install -y apt-transport-https dirmngr
echo 'deb https://apt.dockerproject.org/repo debian-stretch main' >> /etc/apt/sources.list
apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
apt-get update
apt-get install -y docker-engine
```

### Cockpit
```
apt-get -y install cockpit cockpit-docker
systemctl start cockpit
systemctl enable cockpit
```

### Create persistent file storage
```
mkdir /docker
mkdir /docker/homebridge
mkdir /docker/mqtt
mkdir /docker/mqtt/config
mkdir /docker/mqtt/data
mkdir /docker/mqtt/logs
```

### MQTT
- Create `mosquitto.conf` in `/docker/mqtt/config/mosquitto.conf`
- Edit `pwfile` location in `mosquitto.conf` to `/mosquitto/config`
- Create `pwfile` in `/docker/mqtt/config/pwfile`

### HomeBridge
- Create config.json `nano /docker/homebridge/config.json`
```
{
    "bridge": {
        "name": "Homebridge",
        "username": "CC:22:3D:E3:CE:30",
        "port": 51826,
        "pin": "031-45-154"
    },
    
    "platforms": [
  {
    "platform": "HomeAssistant",
    "name": "HomeAssistant",
    "host": "http://127.0.0.1:8123",
    "password": "yourapipassword",
    "supported_types": ["automation", "binary_sensor", "climate", "cover", "device_tracker", "fan", "group", "input_boolean","light", "lock", "media_player", "remote", "scene", "script", "sensor", "switch", "vacuum"],
    "default_visibility": "hidden",
    "logging": false,
    "verify_ssl":false
  }
]
}
```

### docker-compose file
```
version: '3'

services:
  mysql:
    image: mysql:latest
    container_name: "mysql"
    volumes:
      - /docker/mysql/data:/var/lib/mysql
    restart: always
    network_mode: "host"  
    environment:
      MYSQL_DATABASE: <DB NAME>
      MYSQL_USER: <DB USER>
      MYSQL_PASSWORD: <DB PASSWORD> 
      MYSQL_RANDOM_ROOT_PASSWORD: "yes"

  mqtt:
    image: eclipse-mosquitto:latest
    container_name: "mqtt"
    restart: always
    volumes:
      - /docker/mqtt/data:/mosquitto/data
      - /docker/mqtt/config:/mosquitto/config
      - /docker/mqtt/log:/mosquitto/log
    network_mode: "host"

  homeassistant:
    image: homeassistant/home-assistant:latest
    container_name: "homeassistant"
    restart: always
    depends_on:
      - mysql
      - mqtt
      - nginx-letsencrypt
    volumes:
      - /docker/homeassistant:/config
      - /etc/localtime:/etc/localtime:ro
      - /root/.ssh:/root/.ssh
      - /var/lib/motion:/var/lib/motion
    devices:
      - /dev/zwave:/dev/zwave
    network_mode: "host"

  appdaemon:
    image: acockburn/appdaemon:latest
    container_name: "appdaemon"
    restart: always
    depends_on:
      - homeassistant
    network_mode: host
    volumes:
      - /docker/appdaemon:/conf
      - /etc/localtime:/etc/localtime:ro

  homebridge:
    image: oznu/homebridge:latest
    container_name: "homebridge"
    restart: always
    depends_on:
      - homeassistant
    network_mode: host
    environment:
      - TZ=Australia/Melbourne
      - PGID=1000
      - PUID=1000
    volumes:
      - /docker/homebridge:/homebridge

  ha_dockermon:
    image: philhawthorne/ha-dockermon
    container_name: ha_dockermon
    restart: always
    network_mode: host
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /docker/ha_dockermon:/config

  nginx-letsencrypt:
    image: linuxserver/letsencrypt
    container_name: "nginx-letsencrypt"
    restart: always
    network_mode: host
    environment:
      - URL=<ROOT DOMAIN>
      - SUBDOMAINS=<SUBDOMAINS>
      - EMAIL=<EMAIL>
      - VALIDATION=dns
      - DNSPLUGIN=cloudflare
      - TZ=Australia/Melbourne
      - PUID=1001
      - PGID=1002
    volumes:
      - /docker/nginx-letsencrypt:/config
      - /etc/localtime:/etc/localtime:ro
    cap_add:
      - NET_ADMIN

  syncthing:
    image: linuxserver/syncthing
    container_name: "syncthing"
    restart: always
    network_mode: host
    environment:
      - PGID=0
      - PUID=0
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /docker/syncthing:/config
      - /docker:/mnt/docker
```

#### Note:
To update docker images:
```
cd /docker && docker pull acockburn/appdaemon:latest && docker-compose up -d && docker logs appdaemon --follow
```

#### Note:
If HomeKit is having issues connecting with HomeBridge after a restore, complete the following:
- Remove all devices from HomeKit
```
docker stop homebridge
rm -rf /docker/homebridge/accessories
rm -rf /docker/homebridge/persist
nano /docker/homebridge/config.json
```
- Increment the Username
- `docker start homebridge`
- Pair with HomeBridge