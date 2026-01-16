sudo tee /etc/systemd/system/audio-to-transcripts.service >/dev/null <<'EOF'
[Unit]
Description=Audio to Transcripts (Streamlit)
After=network-online.target
Wants=network-online.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/apps/audio-to-transcripts/
ExecStart=/home/ubuntu/apps/audio-to-transcripts/venv/bin/streamlit run /home/ubuntu/apps/audio-to-transcripts/app.py --server.address=0.0.0.0 --server.port=8503 --server.headless=true --server.maxUploadSize=200
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now audio-to-transcripts
sudo systemctl status audio-to-transcripts --no-pager
# optional: tail logs
sudo journalctl -u audio-to-transcripts -e --no-pager