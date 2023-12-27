# Build images for all services and push them to Docker Hub

set -e

cd ci

# Generate a random tag
export TAG=$(openssl rand -hex 4)

# Login to Docker Hub
docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD docker.io

# Build and push images to Docker Hub
for service in "audio-analyzer" "backend" "frontend"; do
  cd $service
  cp docker/ops/Dockerfile .
  docker build -t docker.io/vinyl-manager/$service:$TAG .
  docker push docker.io/vinyl-manager/$service:$TAG
  rm Dockerfile
done

# Deploy to Kubernetes
helm build ./helm
helm push ./helm docker.io/vinyl-manager/helm

# Update the deployment
helm upgrade vinyl-manager ./helm --install --set image.tag=$TAG --set image.pullPolicy=Always --set image.repository=docker.io/vinyl-manager