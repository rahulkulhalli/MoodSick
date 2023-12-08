#!/bin/bash

# Check if node_modules folder exists
if [ ! -d "node_modules" ]; then
  echo "node_modules not found, running npm install..."
  npm install
fi

# Run npm run dev
echo "Starting the development server..."
npm run dev
