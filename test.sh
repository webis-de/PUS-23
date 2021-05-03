for FILE in tests/test*.py;
do
echo $'\033[01;33mRunning tests in' $FILE $'\033[01;37m';
echo ''
python3 -m unittest -v $FILE;
done
