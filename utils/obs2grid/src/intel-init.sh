#!/bin/bash
source /home/opt/intel/bin/compilervars.sh intel64
source /home/opt/intel/bin/iccvars.sh intel64
source /home/opt/intel/impi/4.1.0.024/bin64/mpivars.sh
export PATH=/home/opt/intel/bin:$PATH
export LD_LIBRARY_PATH=/home/opt/intel/lib/intel64:$LD_LIBRARY_PATH
