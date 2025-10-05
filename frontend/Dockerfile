# Embiggen Your Eyes - Frontend Dockerfile
# Optimized for Google Cloud Run deployment

FROM nginx:alpine

# Copy frontend files to nginx html directory
COPY index.html /usr/share/nginx/html/
COPY styles.css /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/
COPY assets/ /usr/share/nginx/html/assets/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
