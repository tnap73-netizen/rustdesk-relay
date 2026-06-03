FROM rustdesk/rustdesk-server:latest

EXPOSE 21115 21116 21116/udp 21117 21118 21119

RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

COPY supervisord.conf /etc/supervisor/conf.d/rustdesk.conf

CMD ["supervisord", "-n", "-c", "/etc/supervisor/conf.d/rustdesk.conf"]
