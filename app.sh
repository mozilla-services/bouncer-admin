# Import data to mysql
mysql $@ < data.sql
status=$?
if [ $status -ne 0 ]; then
    echo "Failed to import data.sql into MySQL database. Check that you have mysql and user 'root' is given access without a password\n"
    exit $status
fi

# Remove any old Nazgul docker image or containers
docker image rm --force nazgul
docker container rm --force local-nazgul

# Build new Nazgul image
docker image build -t=nazgul .
status=$?
if [ $status -ne 0 ]; then
    exit $status
fi

# Run nazgul in new container
docker run --name local-nazgul --rm -p 5000:5000 nazgul
status=$?
if [ $status -ne 0 ]; then
    exit $status
fi
