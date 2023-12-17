#!/bin/sh

# Push dthe k8s config
# We assume that the target k8s namespace is the name of the target branch, 
# so we can have multiple versions running simultaneously.
TARGET_NAMESPACE=${GITHUB_BASE_REF:-temp-test}

 kubectl get namespace ${TARGET_NAMESPACE} || kubectl create namespace ${TARGET_NAMESPACE}
 kubectl apply -n ${TARGET_NAMESPACE} -f config.yaml
 # Give some time for pod to start
 sleep 90
 
