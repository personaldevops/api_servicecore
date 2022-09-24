SCRIPTDIR=$(dirname "$0")
BASEDIR=$(cd "$SCRIPTDIR" && pwd)
HOMEDIR=${BASEDIR}/..
GIT_DIR=$(cd "${HOMEDIR}" && pwd)
python setup.py sdist
scp -r $GIT_DIR/dist/* pi@192.168.1.8:/naveen/srv/packages/