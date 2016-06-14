function check_virtualenv_is_active() {
    echo "${green}[virtualenv] Checking if virtualenv is active.${reset}"
    if [[ ! "$VIRTUAL_ENV" ]]; then
        echo "${red}Oop! no virtualenv is active, please make sure to create and activate a virtualenv before proceeding.${reset}"
        exit 1
    fi
}

function check_mysql_server_is_running(){
    echo "${green}[mysql] Checking if mysql is installed.${reset}"
    if [[ ! $(which mysql) ]]; then
        echo "${red}Oop! no mysql executable found, please make sure mysql server is installed and running before proceeding.${reset}"
        exit 1
    fi
}

function install_python_requirements(){
    echo "[pip] Ensure requirements are installed and are upto date..."
    pip install -r requirements-dev.txt > /dev/null
}
