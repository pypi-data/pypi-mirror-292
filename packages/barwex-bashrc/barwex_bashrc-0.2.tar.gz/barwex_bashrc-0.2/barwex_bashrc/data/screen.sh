# 在后台启动 screen 会话
xx-screen-start-backend(){
    name=$1
    command=$2
    screen -dmS $name bash -c "$command"
}

alias sl='screen -ls'
alias sr='screen -R'
alias sd='screen -d'