#!/bin/bash

################################################################################
#                                    Docker                                    #
################################################################################

xx-docker-exec() {
    if [[ $# -eq 0 ]]; then
        echo "Usage: de <container> [<command>]=bash"
    else
        container="$1"
        shift
        if [[ $# -eq 0 ]]; then
            echo "[INFO] You are in container bash!"
            docker exec -it $container bash
        else
            docker exec $container $@
        fi
    fi
}
xx-docker-stop-rm() {
    docker stop $1
    docker rm $1
}
xx-show-container-ports() { docker inspect $1 -f "{{json .NetworkSettings.Ports}}" | python -m json.tool; }
xx-show-container-volumes() { docker inspect $1 -f "{{json .Mounts}}" | python -m json.tool; }
xx-show-container-networks() { docker inspect $1 -f "{{json .NetworkSettings}}" | python -m json.tool; }
alias de="xx-docker-exec"
alias dl='docker ps --all --format "table {{.ID}}\t{{.Names}}\t{{.RunningFor}}\t{{.Status}}"'
alias drm="xx-docker-stop-rm"

################################################################################
#                                DockerCompose                                 #
################################################################################

xx-docker-compose() {
    if [[ $# -eq 0 ]]; then
        echo "dc rmf <service>: stop and remove service"
        echo "dc exec <service>: enter service bash"
        return
    fi
    action=$1
    if [ $action == "rmf" ]; then
        service=$2
        docker-compose stop $service
        docker-compose rm $service
        return
    fi
    if [ $action == "exec" ]; then
        if [[ $# -eq 2 ]]; then
            service=$2
            echo "[INFO] You are in container bash!"
            docker-compose exec $service bash
            return
        fi
    fi
    docker-compose $@
}
alias dc="xx-docker-compose"

################################################################################
#                                 Docker Image                                 #
################################################################################

DOCKER_REGISTRY=$BARWEX_BASHRC_DOCKER_REGISTRY
xx-login-byoryn-registry() {
    docker login registry.byoryn.com
    docker login $DOCKER_REGISTRY
}
xx-pull-image-from-byoryn-registry() {
    image=$1
    docker pull $DOCKER_REGISTRY/$image
    docker tag $DOCKER_REGISTRY/$image registry.byoryn.com/$image
    docker image rm $DOCKER_REGISTRY/$image
}
xx-push-image-to-byoryn-registry() {
    localimage=$1
    remoteimage=$2
    docker tag $localimage $DOCKER_REGISTRY/$remoteimage
    docker tag $localimage registry.byoryn.com/$remoteimage
    docker push $DOCKER_REGISTRY/$remoteimage
    docker push registry.byoryn.com/$remoteimage
    docker image rm $localimage $DOCKER_REGISTRY/$remoteimage
}
xx-remove-all-none-images() {
    docker images | tail -n +2 | grep '<none>' | sed -n 's/.* \([0-9a-f]\{12\}\) .*/\1/p' | xargs -I {} docker image rm {}
}
alias dis='docker images | tail -n +2 | sort'
alias disg='dis | grep'
alias dirm='docker image rm'

################################################################################
#                                    Others                                    #
################################################################################

# 临时增加 /run 挂载点的容量，重启时失效
xx-increase-runsize-for-docker() {
    sudo mount -o remount,size=${1:-12G} /run
}