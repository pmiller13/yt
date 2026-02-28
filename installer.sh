sudo install -m 644 -o root -g root youtube-ad-scrubber.service /etc/systemd/system/
sudo systemctl daemon-reload

sudo systemctl start youtube-ad-scrubber.service
sudo systemctl status youtube-ad-scrubber.service
