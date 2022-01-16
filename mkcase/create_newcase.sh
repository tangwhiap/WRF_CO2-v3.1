#!/bin/bash
# Used to create new case in cases folder.
# Authors:
#  Wenhan Tang - 12/2020 (Original Version)
#  ...
# ------------------------------------------
# Main steps:
# Step 1: Checking if the case user created have already been exits.
# Step 2: Creating directory for the case and folders within it.
# Step 3: Replacing the undefined setting with default setting.
# Step 4: Creating the configure.sh.
# Step 5: Creating inner links.
# Step 6: Copying namelist files demo.
# Step 7: Creating run.sh, nohuprun.sh and clear_casework.sh etc.
# Step 8: Removing the *.set in setting files folder.
# -----------------------------------------


if [[ ! -f .model_def_dir.sh ]]; then
    echo "Please execute \$ROOTDIR/ini/init.sh first!"
    exit
fi
source .model_def_dir.sh
source $Trashrc $ROOTDIR

cd $MKCASEDIR
if [ -f $MKCASEDIR/.case_*_created_successfully ]; then
    rm $MKCASEDIR/.case_*_created_successfully
fi

CASENAME=$1
RUNTYPE=$2
RestartRun=$3
OtherDir=$4
CASEDIR=$CASESDIR/$CASENAME

if [[ $CASENAME == '' ]]; then
    echo "Please enter the name of new case."
    exit
fi

if [[ $RUNTYPE == '' ]]; then
    RUNTYPE=normal
fi

if [[ $RestartRun == '' ]]; then
    RestartRun=false
fi

if [[ ! $RUNTYPE == "normal" ]] && [[ ! $RUNTYPE == "cronjob" ]]; then
    echo "Error! \"RUNTYPE\" must be one of \"normal\" or \"cronjob\"."
    exit
fi

if [[ ! $RestartRun == "true" ]] && [[ ! $RestartRun == "false" ]]; then
    echo "Error! \"RestartRun\" must be one of \"true\" or \"false\"."
    exit
fi

if [[ ! $OtherDir == '' ]]; then
    if [[ ! -d $OtherDir ]]; then
        echo "Error! directory: $OtherDir doesn't exit."
        exit
    fi
    #if [[ -a $OtherDir/$CASENAME ]]; then
#echo "Creating new case ${CASENAME} on ${OtherDir}"
#cd $CASESDIR
#ln -sf $OtherDir/$CASENAME ./$CASENAME
fi
echo "==================="
echo "CASE OPTIONS:"
echo "CASE NAME: $CASENAME"
echo "RUN TYPE: $RUNTYPE"
echo "RESTART: $RestartRun"
echo ""

Me=$( readlink -m $( type -p $0 ))
MKCASEDIRCheck=`dirname $Me`
if [[ "$MKCASEDIRCheck" != "$MKCASEDIR" ]]; then
    echo "Fatal Error!"
    echo "Maybe running ini/init.sh can help"
    exit
fi

# Loading CASE relative directory
source $MKCASEDIR/case_def_dir.sh

exert_case_exits()
{
    OtherDir=$1
    if [[ ! $OtherDir == '' ]]; then
        CASEDIR=$OtherDir/$CASENAME
    fi
    echo "=== CASE: $CASENAME already exits ==="
    echo "* If you want to change configure of this case,"
    echo "Please edit the configure file \$CASECONFIG/configure.sh."
    echo "* If you want to recreate this case,"
    echo "Please remove $CASEDIR first."
    exit

}

if [[ $OtherDir == '' ]]; then
    if [ -a $CASEDIR ]; then
        exert_case_exits
    fi
else
    if [ -a $OtherDir/$CASENAME ]; then
        exert_case_exits $OtherDir
    elif [ -h $CASEDIR ]; then
        if [ ! -d $CASEDIR ]; then
            echo "Find the old, invalid link of case: ${CASENAME}, unlink it."
            unlink $CASEDIR
        else
            exert_case_exits
        fi
    elif [ -a $CASEDIR ]; then
        exert_case_exits
    fi
fi

if [[ ! $OtherDir == '' ]]; then
    mkdir -p $OtherDir/$CASENAME
    cd $CASESDIR

    ln -sf $OtherDir/$CASENAME ./$CASENAME
else
    mkdir -p $CASEDIR
fi

mkdir -p $CASECONFIG
mkdir -p $CASERUN
mkdir -p $CASEWORK
mkdir -p $CASEOUT
mkdir -p $CASELOG
mkdir -p $CASELOG/nohup_log
mkdir -p $CASELOG/nohup_mksrc_log

if [[ $RUNTYPE == "cronjob" ]]; then
    mkdir -p $CASELOG/cronjob_log
fi
mkdir -p $CASEPLOT
mkdir -p $CASERES
mkdir -p $WebCaseDir

# Variables only in this script.
DefaultDir=$MKCASEDIR/default_config
SetDir=$MKCASEDIR/set_config
ToolsDir=$MKCASEDIR/tools
###

if [[ ! -f $SetDir/select_input.set ]]; then
    cp -p $DefaultDir/select_input.dft $SetDir/select_input.set
fi
if [[ ! -f $SetDir/set_domain.set ]]; then
    cp -p $DefaultDir/set_domain.dft $SetDir/set_domain.set
else
    cat $DefaultDir/set_domain.dft >> $SetDir/set_domain.set
fi
if [[ ! -f $SetDir/set_run.set ]]; then
    cp -p $DefaultDir/set_run.dft $SetDir/set_run.set
fi
if [[ ! -f $SetDir/var_output.set ]]; then
    cp -p $DefaultDir/var_output.dft $SetDir/var_output.set
fi
if [[ ! -f $SetDir/file_output.set ]]; then
    cp -p $DefaultDir/file_output.dft $SetDir/file_output.set
fi
if [[ ! -f $SetDir/tracers_input.set ]]; then
    cp -p $DefaultDir/tracers_input.dft $SetDir/tracers_input.set
fi

mkdir -p $CASEWORK/nml
cp -p $DefaultDir/nml-wps.dft $CASEWORK/nml/nml-wps_demo
cp -p $DefaultDir/nml-wrf.dft $CASEWORK/nml/nml-wrf_demo
cat $MKCASEDIR/.model_env_set.sh > $CASERUN/.model_env_set.sh

alias logt='date +"%Y/%m/%d %H:%M:%S"'
shopt -s expand_aliases
echo `logt` >> .mkcase.err

# Creating configure.sh
echo "#!/bin/bash" >> $CASECONFIG/configure.sh 2>> .mkcase.err
echo "### This scripts is generated automatically by MAKE CASE module (create_newcase.sh) ##" >> $CASECONFIG/configure.sh 2>/dev/null
echo "### The script is protected, you can edit it.###" >> $CASECONFIG/configure.sh 2>/dev/null

echo "CASENAME=$CASENAME" >> $CASECONFIG/configure.sh 2>> .mkcase.err
echo "RUNTYPE=$RUNTYPE" >> $CASECONFIG/configure.sh 2>> .mkcase.err
echo "RestartRun=$RestartRun" >> $CASECONFIG/configure.sh 2>> .mkcase.err

cat $SetDir/set_run.set >> $CASECONFIG/configure.sh 2>> .mkcase.err
echo "" >> $CASECONFIG/configure.sh
cat $SetDir/select_input.set >> $CASECONFIG/configure.sh 2>> .mkcase.err
echo "" >> $CASECONFIG/configure.sh

cat $SetDir/file_output.set >> $CASECONFIG/configure.sh 2>> .mkcase.err
echo "" >> $CASECONFIG/configure.sh

echo "case configure:"
echo `cat ${CASECONFIG}/configure.sh`
echo ""

cat $MKCASEDIR/.model_def_dir.sh >> $CASECONFIG/configure.sh 2>> .mkcase.err
echo "" >> $CASECONFIG/configure.sh
echo "CASEDIR=\$CASESDIR/\$CASENAME" >> $CASECONFIG/configure.sh 2>> .mkcase.err
cat $MKCASEDIR/case_def_dir.sh >> $CASECONFIG/configure.sh 2>> .mkcase.err
cat >> $CASECONFIG/configure.sh << EOF
alias logt='date +"%Y/%m/%d %H:%M:%S"'
shopt -s expand_aliases
EOF

# Creating setdom.nml
cat $SetDir/set_domain.set >> $CASECONFIG/setdom.nml 2>> .mkcase.err
echo "" >> $CASECONFIG/configure.sh

# Creating var_output.set
cat $SetDir/var_output.set >> $CASECONFIG/var_output.set 2>> .mkcase.err

# Creating tracers_input.py
echo "#!/usr/bin/env python" >> $CASECONFIG/tracers_input.py 2>> .mkcase.err
echo "# tracers input data setting" >> $CASECONFIG/tracers_input.py 2>> .mkcase.err
cat $SetDir/tracers_input.set >> $CASECONFIG/tracers_input.py 2>> .mkcase.err

# Link tracers_input.py to $InputProcConfigDir  
if [ -h $InputProcConfigDir/tracers_input_${CASENAME}.py ];then
    unlink $InputProcConfigDir/tracers_input_${CASENAME}.py
fi
ln -sf $CASECONFIG/tracers_input.py $InputProcConfigDir/tracers_input_${CASENAME}.py

if [ -h $BckgProcConfigDir/tracers_input_${CASENAME}.py ];then
    unlink $BckgProcConfigDir/tracers_input_${CASENAME}.py
fi
ln -sf $CASECONFIG/tracers_input.py $BckgProcConfigDir/tracers_input_${CASENAME}.py

if [ -h $XCO2ConfigDir/tracers_input_${CASENAME}.py ];then
    unlink $XCO2ConfigDir/tracers_input_${CASENAME}.py
fi
ln -sf $CASECONFIG/tracers_input.py $XCO2ConfigDir/tracers_input_${CASENAME}.py

source $CASECONFIG/configure.sh
cd $ToolsDir
$ToolsDir/get_maxdom.sh $CASECONFIG setdom.nml $Region 2>> .mkcase.err


cd $CASEDIR
ln -sf ./config/configure.sh ./configure

cd $CASEWORK
#ln -sf $CASECONFIG config
ln -sf ../config config # Using relative path instead.


cd $CASERUN
ln -sf ../config config
cat > $CASERUN/run.sh << EOF
#!/bin/bash
# Used to run the top level script in case folder.
### This script is generated automatically by create_newcase.sh ###
### The scripts in case folder is protected, you can edit it. ###
EOF
cat $MKCASEDIR/case_scripts/run.sh.demo >> $CASERUN/run.sh

#source config/configure.sh
#cd \$CASEWORK
#\$RunScriptsDir/Main_run.sh
#EOF
chmod +x $CASERUN/run.sh

cat > $CASERUN/nohuprun.sh << EOF
#!/bin/bash
# Used to run the top level script in case folder.
### This script is generated automatically by create_newcase.sh ###
### The scripts in case folder is protected, you can edit it. ###
EOF
cat $MKCASEDIR/case_scripts/nohuprun.sh.demo >> $CASERUN/nohuprun.sh
#source config/configure.sh

#date=\`date +%Y-%m-%d_%H:%M:%S\`
#nohup ./run.sh &> \${CASELOG}/runlog_\${date}.txt &
#EOF
chmod +x $CASERUN/nohuprun.sh

cat > $CASERUN/mkbnd.sh << EOF
#!/bin/bash
# Used to run the boundary data before running WRF-CO2 (offline)
### This script is generated automatically by create_newcase.sh ###
### The scripts in case folder is protected, you can edit it. ###
EOF
cat $MKCASEDIR/case_scripts/mkbnd.sh.demo >> $CASERUN/mkbnd.sh
chmod +x $CASERUN/mkbnd.sh

cat > $CASERUN/nohup_mkbnd.sh << EOF
#!/bin/bash
### This script is generated automatically by create_newcase.sh ###
### The scripts in case folder is protected, you can edit it. ###
EOF
cat $MKCASEDIR/case_scripts/nohup_mkbnd.sh.demo >> $CASERUN/nohup_mkbnd.sh
chmod +x $CASERUN/nohup_mkbnd.sh


if [[ $RUNTYPE == "cronjob" ]]; then
    cat > $CASERUN/cronjobrun.sh << EOF
#!/bin/bash
### This script is generated automatically by create_newcase.sh ###
EOF
    cat $MKCASEDIR/case_scripts/cronjobrun.sh.demo >> $CASERUN/cronjobrun.sh
    chmod +x $CASERUN/cronjobrun.sh

    cat > $CASERUN/start_cronjob.sh << EOF
#!/bin/bash
### This script is generated automatically by create_newcase.sh ###
EOF
    cat $MKCASEDIR/case_scripts/start_cronjob.sh.demo >> $CASERUN/start_cronjob.sh
    chmod +x $CASERUN/start_cronjob.sh
fi

cd $CASEDIR
cat > $CASEDIR/clear_casework.sh << EOF
#!/bin/bash
# Used to clear the work folder before rerun the simulation in this case.
### This script is generated automatically by create_newcase.sh ###
### The scripts in case foler is protected, you can edit it. ###
EOF
cat $MKCASEDIR/case_scripts/clear_casework.sh.demo >> $CASEDIR/clear_casework.sh


#source ./config/configure.sh
#source \$Trashrc \$ROOTDIR
#cd work
#shopt -s extglob
#rm !(config|nml) 2> /dev/null
#cd nml
#rm !(nml-wps_demo|nml-wrf_demo) 2> /dev/null
#cd ../../config
#rm wps_input.sh 2> /dev/null
#EOF
chmod +x $CASEDIR/clear_casework.sh

cat > $CASEDIR/reinit.sh << EOF
#!/bin/bash
# reset this case
### This script is generated automatically by create_newcase.sh ###
### The scripts in case foler is protected, you can edit it. ###
EOF
cat $MKCASEDIR/case_scripts/reinit.sh.demo >> $CASEDIR/reinit.sh
chmod +x $CASEDIR/reinit.sh

cat > $CASEDIR/config/domain_show.sh << EOF
#!/bin/bash
# showing domain configure
### This script is generated automatically by create_newcase.sh ###
### The scripts in case foler is protected, you can edit it. ###
EOF
cat $MKCASEDIR/case_scripts/domain_show.sh.demo >> $CASEDIR/config/domain_show.sh
chmod +x $CASEDIR/config/domain_show.sh
cp -p $MKCASEDIR/case_scripts/stalist.txt $CASEDIR/config/

cd $SetDir
rm $SetDir/*.set

echo "==========================="
echo "!!!   MAKE CASE module  !!!"
echo "!!! Successful Complete !!!"
echo "==========================="
echo "New case is created in $CASEDIR"
echo "case: $CASENAME created successfully!" > $MKCASEDIR/.case_${CASENAME}_created_successfully 2> /dev/null
echo ""
