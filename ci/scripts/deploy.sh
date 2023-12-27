# Build images for all services and push them to Docker Hub

set -e

cd ci

# Login to Docker Hub
docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD harbor.k8s.local

# Build and push images to Docker Hub
for service in "audio-analyzer" "backend" "frontend"; do
  cd $service
  cp docker/ops/Dockerfile .
  docker build -t harbor.k8s.local/library/$service:latest .
  docker push harbor.k8s.local/library/$service:latest
  rm Dockerfile
done

# Deploy to Kubernetes
helm build ./helm
helm push ./helm harbor.k8s.local/library

# Update the deployment
helm upgrade --install --namespace=library library ./helm