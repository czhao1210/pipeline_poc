#/bin/bash
script=$(readlink -f "$0")
echo "script:"$script
dscript=`dirname $script`
cd $dscript
which python 1>/dev/null 2>&1
if [ $? != 0 ]; then
    echo "Fatal Error: can't find python"
fi
pid=`ps -ef|grep 'sut_agent'|grep -v 'grep'|awk {'print $2'}`
if [ "$pid" != "" ]
then
	echo "kill $pid"
	kill -9 $pid
fi
declare -x PYTHONPATH=$dscript/..
echo "python path" $PYTHONPATH
gnome-terminal --geometry=120x25+200+10 -x bash -c "python3 $dscript/sut_agent.py; exec bash" &
