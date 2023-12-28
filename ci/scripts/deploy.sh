# Build images for all services and push them to Docker Hub
set -e

# Parse arguments
# 1. Target (build,deploy) - default: build,deploy
TARGET=${1:-"build,deploy"}

# Change to the ci directory
cd ../..

# Use current git commit hash as tag, prefixed with the current date
TAG=$(date +%Y%m%d)-$(git rev-parse --short HEAD)

# Login to Docker Hub
echo $GITHUB_TOKEN | docker login ghcr.io -u timosur --password-stdin

# Check if the build target is set
if [[ $TARGET == *"build"* ]]; then
  # Build and push images to Docker Hub
  for service in "audio-analyzer" "backend" "frontend"; do
    cd $service
    cp docker/ops/Dockerfile .
    docker build -t ghcr.io/timosur/vinyl-manager-$service:$TAG .
    docker push ghcr.io/timosur/vinyl-manager-$service:$TAG
    rm Dockerfile
    cd ..
  done
fi

# Check if the deploy target is set
if [[ $TARGET == *"deploy"* ]]; then
  # Deploy to Kubernetes
  cd ci

  # Create namespace
  kubectl apply -f k8s/namespace.yaml
  # Deploy stackgres cluster
  # kubectl apply -f k8s/stackgres_cluster.yaml

  # Move to helm directory
  cd helm

  # Set version and appVersion in Chart.yaml
  sed -i '' "s/version: .*/version: $TAG/g" Chart.yaml
  sed -i '' "s/appVersion: .*/appVersion: $TAG/g" Chart.yaml
  
  helm package .
  helm push vinyl-manager-$TAG.tgz oci://ghcr.io/timosur
  rm vinyl-manager-$TAG.tgz

  # Create pull secret for private images, using the GitHub token
  # Check if the secret already exists in namespace vinyl-manager
  if ! kubectl get secret ghcr -n vinyl-manager > /dev/null 2>&1; then
    kubectl create secret docker-registry ghcr \
      --docker-server=ghcr.io \
      --docker-username=timosur \
      --docker-password=$GITHUB_TOKEN \
      --namespace vinyl-manager
  fi

  # Update the deployment
  helm upgrade vinyl-manager oci://ghcr.io/timosur/vinyl-manager \
    --install \
    --namespace vinyl-manager \
    --create-namespace \
    --version $TAG \
    --set image.tag=$TAG \
    --set image.repository=ghcr.io/timosur/vinyl-manager \
    --set image.pullSecret=ghcr \
    --set backend.secretKey=$SECRET_KEY \
    --set backend.discogsUserToken=$DISCOGS_USER_TOKEN \
    --set postgres.user=$POSTGRES_USER \
    --set postgres.password=$POSTGRES_PASSWORD \
    --set postgres.database=$POSTGRES_DATABASE
fi