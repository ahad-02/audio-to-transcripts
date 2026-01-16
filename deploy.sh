sudo tee /etc/systemd/system/audio-transcriber.service >/dev/null <<'EOF'
[Unit]
Description=Audio Transcriber (Streamlit)
After=network-online.target
Wants=network-online.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/apps/audio-transcriber/AudiTranscriber
ExecStart=/home/ubuntu/apps/audio-transcriber/AudiTranscriber/venv/bin/streamlit run /home/ubuntu/apps/audio-transcriber/app.py --server.address=0.0.0.0 --server.port=8503 --server.headless=true --server.maxUploadSize=200
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now audio-transcriber
sudo systemctl status audio-transcriber --no-pager