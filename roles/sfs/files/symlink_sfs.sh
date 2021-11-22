die ()
{
  echo $1
  exit 1
}

echo "Symlinking /ddi/services/sfs-bundles/1.0.25 to /ddi/services/sfs-bundles/current "
ln -nsf /ddi/services/sfs-bundles/1.0.25 /ddi/services/sfs-bundles/current || die "Symlinking to current failed, Exiting"


echo "Cleaning /home/SFS_PRO_1.6.6/Server/felix-cache"
rm -rf /home/SFS_PRO_1.6.6/Server/felix-cache/*

echo "Building config symlinks"
cd /home/SFS_PRO_1.6.6/Server || die "/home/SFS_PRO_1.6.6/Server does not exist, Exiting. "

fileList=(
  'conf/wrapper.conf'
  'config.xml'
  'felix.config'
  'lib/com.doubledowninteractive.smartfox.osgi.jar'
  'lib/org.apache.felix.main.jar'
  'bundle'
  'app.config'
  'xDomainPolicy.xml'
  'log4j.properties'
  'logging.properties'
  'roomsMap.json'
  'webserver/cfg/jetty.xml'
  'webserver/webapps/BlueBox.war'
  'webserver/webapps/ddcroot'
)

for path in "${fileList[@]}"
do
  if [ ! -L "$path" ]; then
    mv -v "$path" "$path.save";
    ln -nsvf "/ddi/services/sfs-bundles/current/$path" "$path";
  else
    ln -nsf "/ddi/services/sfs-bundles/current/$path" "$path";
  fi
done
