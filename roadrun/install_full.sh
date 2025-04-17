#!/bin/bash
# This file is part of the jetson_stats package (https://github.com/rbonghi/jetson_stats or http://rnext.it).
# Copyright (c) 2020 Raffaello Bonghi.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


JETSON_TYPE=$(cat /sys/firmware/devicetree/base/model)
echo $JETSON_TYPE

content=$(dpkg-query --showformat='${Version}' --show nvidia-l4t-kernel)
CONFIG_FILE_NAME=modules.txt
CONFIG_FILE_DOWNLOAD_LINK=https://github.com/ArduCAM/MIPI_Camera/releases/download/v0.0.3/modules.txt
RED='\033[0;31m'
NC='\033[0m' # No Color

updateModules()
{
    rm -f $CONFIG_FILE_NAME
    wget -O $CONFIG_FILE_NAME $CONFIG_FILE_DOWNLOAD_LINK
    source $CONFIG_FILE_NAME
}

listModules()
{
    if [ ! -f $CONFIG_FILE_NAME ]; then
        updateModules
    fi
    source $CONFIG_FILE_NAME
    echo "Supported modules:"
    for key in ${!module_cfg_names[*]};do
    echo -e "\t$key"
    done
    echo ""
}

helpFunction()
{
    if [ ! -f $CONFIG_FILE_NAME ]; then
        updateModules
    fi
    echo ""
    echo "Usage: $0 [option]... -m <moduel name>"
    echo -e "Options:"
    echo -e "\t-m <module name>\tSpecify the module name."
    echo -e "\t-h \t\t\tShow this information."
    echo -e "\t-l \t\t\tUpdate and list available modules."
    echo ""
    listModules
    exit 1
}

while getopts hlm: flag
do
    case "${flag}" in
        m)  module=${OPTARG};;
        l)  updateModules
            listModules
            exit 1
            ;;
        ?)  helpFunction;;
    esac
done

if [ ! -f $CONFIG_FILE_NAME ]; then
    updateModules
fi

source $CONFIG_FILE_NAME

if [ -z $module ]; then
    helpFunction
fi

module_cfg_name=${module_cfg_names[$module]}
module_cfg_download_link=${module_cfg_download_links[$module]}

if [[ (-z $module_cfg_name) || (-z $module_cfg_download_link) ]]; then
    echo -e "${RED}Unsupported modules.${NC}"
    echo ""
    listModules
    exit -1
fi

# echo "module_cfg_name: $module_cfg_name"
# echo "module_cfg_download_link: $module_cfg_download_link"

rm -f $module_cfg_name
wget -O $module_cfg_name $module_cfg_download_link
source $module_cfg_name

download_link=
pkg_name=
if [[ $JETSON_TYPE == *"Xavier NX"* ]]; then
	download_link=${nx_download_links[$content]}
	pkg_name=${nx_names[$content]}
fi

if [[ $JETSON_TYPE == *"Nano"* ]]; then
	download_link=${nano_download_links[$content]}
	pkg_name=${nano_names[$content]}
fi

if [[ $JETSON_TYPE == *"Orin NX"* ]]; then
	download_link=${orin_nx_download_links[$content]}
	pkg_name=${orin_nx_names[$content]}
fi

if [[ $JETSON_TYPE == *"Orin Nano"* ]]; then
	download_link=${orin_nano_download_links[$content]}
	pkg_name=${orin_nano_names[$content]}
fi

if [[ $JETSON_TYPE == *"AGX Orin"* ]]; then
	download_link=${agx_orin_download_links[$content]}
	pkg_name=${agx_orin_names[$content]}
fi

if [[ (-z $pkg_name) || (-z $download_link) ]]; then
    echo -e "${RED}"
	echo -e "Cannot find the corresponding deb package, please send the following information to support@arducam.com"
	echo -e "Kernel version: " $content
	echo -e "Jetson type: " $JETSON_TYPE
    echo -e "${NC}"
	exit -1
fi

rm -rf $pkg_name
 
wget $download_link

if [[ ( $? -ne 0) || (! -f "${pkg_name}") ]]; then
	echo -e "${RED}download failed${NC}"
	exit -1
fi

if [ $content == "4.9.140-tegra-32.4.3-20200924161919" ]; then
	if [[ $JETSON_TYPE == *"Xavier NX"* ]]; then
		unzip 20200924161919.zip && sudo dpkg -i 20200924161919/XavierNx/arducam-nvidia-l4t-kernel_4.9.140-32.4.3-20201021145043_arm64.deb
	fi

	if [[ $JETSON_TYPE == *"Nano"* ]]; then
		unzip 20200924161919.zip && sudo dpkg -i 20200924161919/Nano/arducam-nvidia-l4t-kernel_4.9.140-32.4.3-20201021145043_arm64.deb
	fi
else
	sudo dpkg -i $pkg_name
fi

if [ $? -ne 0 ]; then
    echo ""
	echo -e "${RED}Unknown error, please send the error message to support@arducam.com${NC}"
	exit -1
fi

echo ""
echo "reboot now?(y/n):"
read USER_INPUT
case $USER_INPUT in
'y'|'Y')
    echo "reboot"
    sudo reboot
;;
*)
    echo "cancel"
;;
esac
