
FROM node:latest

# Create and change to the app directory.
WORKDIR /usr/src/app

# Copy application dependency manifests to the container image.
# A wildcard is used to ensure both package.json AND package-lock.json are copied.
# Copying this separately prevents re-running npm install on every code change.
COPY package*.json ./

# Install production dependencies.
RUN npm install

# Copy local code to the container image.
COPY . .

# Expose port 3000 to the outside once the container has launched.
EXPOSE 3000

RUN chmod +x /usr/src/app/entrypoint.sh


# Run the web service on container startup.
# CMD ["npm", "run", "dev"]
# CMD ["npm", "run", "dev"]
