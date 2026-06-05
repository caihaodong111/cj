# MediaCrawler Frontend Dockerfile
# Multi-stage build with Chinese mirrors for faster package installation.

ARG NODE_IMAGE=docker.m.daocloud.io/library/node:20-alpine
ARG NGINX_IMAGE=docker.m.daocloud.io/library/nginx:1.27-alpine

FROM ${NODE_IMAGE} AS builder

ARG NPM_REGISTRY=https://registry.npmmirror.com

ENV npm_config_registry=${NPM_REGISTRY}

RUN npm config set registry "${NPM_REGISTRY}"

WORKDIR /app

COPY package*.json ./
RUN npm ci && npm cache clean --force

COPY . .
RUN npm run build

FROM ${NGINX_IMAGE}

ARG ALPINE_MIRROR_HOST=mirrors.tuna.tsinghua.edu.cn

RUN sed -i "s|dl-cdn.alpinelinux.org|${ALPINE_MIRROR_HOST}|g" /etc/apk/repositories && \
    apk update && \
    apk add --no-cache curl

COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

RUN mkdir -p /var/www/backend/static /var/www/backend/media

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
