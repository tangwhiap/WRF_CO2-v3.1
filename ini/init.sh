#!/bin/bash
# Authors:
#    Wenhan TANG - 12/2020
#    ...

ROOTReletiveDir=..
Me=$( readlink -m $( type -p $0 ))

INIDIR=`dirname $Me`
cd $INIDIR/$ROOTReletiveDir
ROOTDIR=`pwd`
#TrashDir=$ROOTDIR/.trash
#TrashrcDir=$ROOTDIR
#MKCASEDIR=$ROOTDIR/mkcase


echo "Create model_def_dir.sh ..."
cd $INIDIR
cat > .model_def_dir.sh << EOF
#!/bin/bash
# Define directories for the frame of WRF-CO2 model
# ------ WARNING ------
# This script is generated automatically by \${ROOTDIR}/ini/init.sh
# ---------------------
ROOTDIR=$ROOTDIR
EOF
cat frame.set >> .model_def_dir.sh
source .model_def_dir.sh

cat environment.set > .model_env_set.sh

echo "Link .model_def_dir.sh ..."
link_def_dir()
{
    if [[ -h .model_def_dir.sh ]]; then
        unlink .model_def_dir.sh
    fi
    echo "Link to "`pwd`"/.model_def_dir.sh"
    ln -sf $INIDIR/.model_def_dir.sh .model_def_dir.sh 2> /dev/null
}
link_env_set()
{
    if [[ -h .model_env_set.sh ]]; then
        unlink .model_env_set.sh
    fi
    echo "Link to "`pwd`"/.model_env_set.sh"
    ln -sf $INIDIR/.model_env_set.sh .model_env_set.sh 2> /dev/null
}

cd $ROOTDIR; link_def_dir
cd $MKCASEDIR; link_def_dir
cd $APIRegDir; link_def_dir
cd $TracersDir; link_def_dir

cd $MKCASEDIR; link_env_set
cd $UtilsDir; link_env_set

echo "Check Trash ..."
cd $ROOTDIR
if [[ ! -d $TrashDir ]]; then
    echo "There isn't any trash, make one."
    mkdir -p $TrashDir
fi

echo "Register input data ..."
cd $APIRegDir
./Registry.sh
