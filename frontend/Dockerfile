FROM node:22-slim AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf.template

ENV BACKEND_URL=http://backend:8000

EXPOSE 80

CMD ["sh", "-c", "BACKEND_HOST=$(echo $BACKEND_URL | sed 's|https\\?://||' | sed 's|/.*||') && sed -e \"s|BACKEND_URL_PLACEHOLDER|$BACKEND_URL|g\" -e \"s|BACKEND_HOST_PLACEHOLDER|$BACKEND_HOST|g\" /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
