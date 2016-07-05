#!/bin/bash
set -e

# Bootstrap
source bin/scripts/setup-vars.sh
source bin/scripts/setup-functions.sh

check_virtualenv_is_active
check_mysql_server_is_running
install_python_requirements

echo "${green}>> Provide MySql credentials of root user:${reset}"
read -p "MySQL User: " db_user
read -sp "MySQL Password (Your typing will be hidden): " db_pass
echo ""
echo "${green}>> Provide the database name:${reset}"
read -p "MySQL Database name: " db_name

echo "${green}>> Creating mysql database $db_name.${reset}"
if [[ $db_pass ]]; then
    mysql -u$db_user -p$db_pass -e "CREATE DATABASE $db_name;"
else
    # Continue without password
    mysql -u$db_user -e "CREATE DATABASE $db_name;"
fi

if [ ! -f config.py ]; then
    echo "${green}>> Copying 'config.sample.py -> config.py'${reset}"
    cp config.sample.py config.py
fi

echo "${green}>> Replacing provided MySQL creds in config.py.${reset}"
sed -i "s/your_database_name_here/$db_name/g" config.py
sed -i "s/your_database_user_here/$db_user/g" config.py
sed -i "s/your_database_password_here/$db_pass/g" config.py

echo "${green}Running database migrations.${reset}"
python manage.py migrate

echo "${green}Creating sample data.${reset}"
python manage.py sample_data

echo "${green}Done! Use './bin/devserver.sh' to start your development server."
echo "You can login to admin at http://localhost:8000/admin/ with:"
echo "username: admin"
echo "password: 123123123${reset}"
echo ""
echo "Happy Coding!!"
