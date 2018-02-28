if [[ "$OSTYPE" == "linux-gnu" ]]; then
        sudo service mongod stop
        sudo service mongod start
elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew services stop mongodb
        brew services start mongodb
fi
echo "MongoDB RE-started..."
output=$(ps aux | grep "manage.py runserver" | awk '{print$2}')
for line in $output
do
        echo "Going to kill process: $line"  
        kill -9 $line
done
echo "Starting the server.."
python manage.py runserver &
exit 0

