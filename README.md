# Voicevox for vps linux CPU Only

`git clone https://github.com/asepindrak/voicevox-linux-cpu-docker.git`

`cd voicevox-linux-cpu-docker/`

`sudo ufw allow 50021`

`sudo ufw allow 50021/tcp`

`sudo ufw allow 50022`

`sudo ufw allow 50022/tcp`

`docker compose up -d`


# SPEAK ENDPOINT

`http://your_ip_address:50022/speak?text=ラーメンはとてもおいしい！一緒に食べに行こう！&speaker=14`

