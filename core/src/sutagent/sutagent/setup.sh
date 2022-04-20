#/bin/bash

read -p "[SUTAgent Serial Port Configuration] port_linux:" port_linux

if [ ! -n "$port_linux" ]; then
  echo "pass"
else
  python3 change_linux_setting.py --port_linux $port_linux
fi


script=$(readlink -f "$0")
echo "script:"$script
dscript=`dirname $script`

#clean up original startup in case exist
sed -i '/run.sh/d' /etc/profile

#register auto startup
[ ! -d /root/.config/autostart ] && mkdir -p /root/.config/autostart
echo -e "[Desktop Entry]\nType=Application\nExec=$dscript/run.sh\nX-GNOME-Autostart-enabled=true" > /root/.config/autostart/run.sh.desktop
echo >$dscript/../common2/lib/__init__.py

#launch script
pid=`ps -ef|grep 'sut_agent'|grep -v 'grep'|awk {'print $2'}`
if [ "$pid" != "" ]
then
	echo "kill $pid"
	kill -9 $pid
fi
declare -x PYTHONPATH=$dscript/..
gnome-terminal --geometry=120x25+200+10 -x bash -c "python3 $dscript/sut_agent.py; exec bash" &

chmod +x run.sh
