FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Download RustDesk server binaries
RUN curl -fsSL https://github.com/rustdesk/rustdesk-server/releases/download/1.1.12/rustdesk-server-linux-amd64.zip -o /tmp/rds.zip \
    && apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/* \
    && unzip /tmp/rds.zip -d /tmp/rds \
    && find /tmp/rds -name 'hbbs' -exec cp {} /usr/local/bin/hbbs \; \
    && find /tmp/rds -name 'hbbr' -exec cp {} /usr/local/bin/hbbr \; \
    && chmod +x /usr/local/bin/hbbs /usr/local/bin/hbbr \
    && rm -rf /tmp/rds /tmp/rds.zip

COPY supervisord.conf /etc/supervisor/conf.d/rustdesk.conf

EXPOSE 21115 21116 21116/udp 21117 21118 21119

CMD ["supervisord", "-n", "-c", "/etc/supervisor/conf.d/rustdesk.conf"]
