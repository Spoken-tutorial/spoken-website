#!/bin/bash
set -e
red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`

echo "${green}>> Checking if virtualenv is active.${reset}"
if [[ ! "$VIRTUAL_ENV" ]]; then
    echo "${red}Oop! no virtualenv is active, please make sure to create and activate a virtualenv before proceeding.${reset}"
    exit 1
fi
echo "${green}>> Checking if mysql is installed.${reset}"
if [[ ! $(which mysql) ]]; then
    echo "${red}Oop! no mysql executable found, please make sure mysql server is installed and running before proceeding.${reset}"
    exit 1
fi

echo "${green}>> Install python requirements from 'requirements-dev.txt'. This might take a while to complete!${reset}"
pip install -r requirements-dev.txt > /dev/null

if [ ! -f config.py ]; then
    echo "${green}>> Copying 'config.sample.py -> config.py'${reset}"
    cp config.sample.py config.py
fi

echo "${green}>> Provide MySql credentials of root user:${reset}"
read -p "MySQL User: " db_user
read -sp "MySQL Password (Your typing will be hidden): " db_pass
echo ""
echo "${green}>> Provide the database name where sqldump need to be imported:${reset}"
read -p "MySQL Database name: " db_name
read -p "MySQL sqldump path: " db_dump_path

echo "${green}>> Creating mysql database $db_name and import the mysql db dump into it. This might take a while!${reset}"
if [[ $db_pass ]]; then
    mysql -u$db_user -p$db_pass -e "CREATE DATABASE $db_name;"
    cat "$db_dump_path" | mysql -u$db_user -p$db_pass $db_name
else
    # Continue without password
    mysql -u$db_user -e "CREATE DATABASE $db_name;"
    cat "$db_dump_path" | mysql -u$db_user $db_name
fi

echo "${green}>> Replacing provided MySQL creds in config.py.${reset}"
sed -i "s/your_database_name_here/$db_name/g" config.py
sed -i "s/your_database_user_here/$db_user/g" config.py
sed -i "s/your_database_password_here/$db_pass/g" config.py

echo "${green}Done! Use './bin/devserver.sh' to start your development server."
