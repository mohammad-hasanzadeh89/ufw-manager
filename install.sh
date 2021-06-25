#!/bin/bash
clear
service ufw-mng stop
rm -rf /opt/ufw-manager
rm -f /etc/systemd/system/ufw-mng.service
echo -e '\nUFW-Manager Installer (Please run the script as root)\n\n'
echo -e 'Install Packages\n'
apt install python3-pip python3-venv git nodejs npm -y
cd /opt/
git clone https://github.com/mohammad-hasanzadeh89/ufw-manager
cd ufw-manager
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt 
cd static
npm install
npm run build 
cd ..
touch /opt/ufw-manager/config.json
echo '{
    "rate_limiting_string": "60/minute"
}' >> /opt/ufw-manager/config.json
touch /etc/systemd/system/ufw-mng.service
chmod +x /etc/systemd/system/ufw-mng.service
echo "cd /opt/ufw-manager && /opt/ufw-manager/venv/bin/gunicorn -b=0.0.0.0:8080 app:app" > /opt/ufw-manager/start.sh
chmod +x /opt/ufw-manager/start.sh
echo "[Unit]
Description=UFW Management Service (WebUI + API)
After=network.target
[Service]
Type=simple
User=root
Group=root
ExecStart=bash /opt/ufw-manager/start.sh
Restart=always
[Install]
WantedBy=multi-user.target" >> /etc/systemd/system/ufw-mng.service
systemctl daemon-reload
systemctl enable ufw-mng
systemctl start ufw-mng
clear
cd /opt/ufw-manager/ && source venv/bin/activate && sudo python3 manage.py
