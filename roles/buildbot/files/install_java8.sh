#!/bin/bash
#
# java setup
#
# check java version
# this is magical bash script
SETUP_SOURCE_DIR=$1
SETUP_INSTALL_DIR=$2
AUTOBLDR_HOME=$3

echo ""
echo "checking to see if we have java 1.8 ..."
javaVersion=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
grep -q "1.8" <<< $javaVersion

if [[ "$?" != "0" ]]; then
    echo "we don't have java 1.8. installing ..."
    # we don't have 1.8 -- need to install
    # get the tgz of the java jdk
    pushd $SETUP_SOURCE_DIR
    wget --no-cookies --no-check-certificate --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com%2F; oraclelicense=accept-securebackup-cookie" "http://download.oracle.com/otn-pub/java/jdk/8u31-b13/jdk-8u31-linux-x64.tar.gz" -O jdk-8u31-linux-x64.tar.gz
    popd

    # unpack it
    pushd $SETUP_INSTALL_DIR
    tar xvfz $SETUP_SOURCE_DIR/jdk-8u31-linux-x64.tar.gz

    jdk_dir=$SETUP_INSTALL_DIR/jdk1.8.0_31

    # install into /usr/local/<jdk-version>
    alternatives --install /usr/bin/java java ${jdk_dir}/bin/java 2
    alternatives --install /usr/bin/jar jar ${jdk_dir}/bin/jar 2
    alternatives --install /usr/bin/javac javac ${jdk_dir}/bin/javac 2
    alternatives --set jar ${jdk_dir}/bin/jar
    alternatives --set javac ${jdk_dir}/bin/javac

    # add to autobldr bashrc also
    echo "export JAVA_HOME=${jdk_dir}" >> ${AUTOBLDR_HOME}/.bashrc
    echo "export JRE_HOME=${jdk_dir}/jre" >> ${AUTOBLDR_HOME}/.bashrc
    echo "export PATH=${jdk_dir}/bin:${jdk_dir}/jre/bin:\$PATH" >> ${AUTOBLDR_HOME}/.bashrc
    # end of java version test
else
  echo "great - we already have java 1.8!"
fi

