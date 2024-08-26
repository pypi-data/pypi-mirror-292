ps1_addr() {
    addr="\u"
    if [ "$SSH_CONNECTION" != "" ]; then
        ip=$(echo $SSH_CONNECTION | awk '{print $3}')
        port=$(echo $SSH_CONNECTION | awk '{print $4}')
        if [ "$port" != "22" ]; then
            addr="-p $port $addr"
        fi
        if [ "$ip" != "127.0.0.1" ]; then
            addr="$addr@$ip"
        fi
        echo $addr
    else
        echo "$addr@\h"
    fi
}

export PS1="\[\e[1;32m\]${BARWEX_BASHRC_PS1_HOST}($(ps1_addr))\[\e[0m\]\[\e[1;34m\] \w\[\e[0m\]\n\$ "