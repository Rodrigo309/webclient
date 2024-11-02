FROM node:22.11.0

WORKDIR /app


COPY package.json yarn.lock ./



COPY . .

RUN yarn install 


EXPOSE 3000

# Executar a aplicação
ENTRYPOINT ["yarn", "dev"]

