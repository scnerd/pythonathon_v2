set -ex

(HERE=`pwd` ; cd / ; cp -r "/d/SSD VMs/Shared/pythonathon" "${HERE}/code")

cd pythonathon
#if [ -d code ]; then
#    (cd code && git pull)
#else
#    git clone https://github.com/scnerd/pythonathon_v2.git code
#fi


docker build . -t pythonathon-server