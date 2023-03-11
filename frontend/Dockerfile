# Pull official latest Node Docker image
FROM --platform=linux/amd64 node:latest

# Set the working directory
WORKDIR /usr/frontend

# Add node modules into PATH
ENV PATH /usr/frontend/node_modules/.bin:$PATH

# Set the server port
EXPOSE 3000

# Install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc \
  && apt-get clean

# Install Node dependencies
COPY ./.npmrc ./package.json ./package-lock.json ./
RUN npm install

# Copy all files
COPY . .

# Copy entrypoint.sh for auto connection with postgres service
COPY ./entrypoints/retry_backend_server.sh ./entrypoints/
RUN chmod +x /usr/frontend/entrypoints/retry_backend_server.sh

# Execute entrypoint.sh
ENTRYPOINT [ "/usr/frontend/entrypoints/retry_backend_server.sh" ]

# Start up the frontend server
CMD [ "npm", "run", "start" ]
