for FILE in tests/test*.py;
do
echo 'Running tests in' $FILE;
echo ''
python3 -m unittest -v $FILE;
done
