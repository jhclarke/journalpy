#!/usr/bin/env bash

if [ `id -u` -ne 0 ]; then
	echo "This script can be executed only as root, Exiting.."
# 	exit 1
fi

# Vars
CRON_FILE="/var/spool/cron/root"
SCRAPE_FILE="scraping_link.py"
EMAIL_FILE="scraping_email.py"
DEPEND_FILE="ps_setup.sh"
DIR_PATH="/usr/local/.scripts/"

if [ ! -f $DIR_PATH ]; then
	mkdir -p $DIR_PATH
fi

chmod +x $SCRAPE_FILE && chmod +x $EMAIL_FILE
cp $SCRAPE_FILE $DIR_PATH && cp $EMAIL_FILE $DIR_PATH && cp $DEPEND_FILE $DIR_PATH
echo "Files moved..."
echo "Loading crontab jobs..."

case "$1" in
   install|update)

	if [ ! -f $CRON_FILE ]; then
	   echo "cron file for root does not exist, creating.."
	   touch $CRON_FILE
	   /usr/bin/crontab $CRON_FILE
	fi

	# Method 1
	grep -qi $SCRAPE_FILE $CRON_FILE
	if [ $? != 0 ]; then
	   echo "Updating cron job for scraping journal data"
           /bin/echo "0 7 * * * python $DIR_PATH$SCRAPE_FILE" >> $CRON_FILE
	   /bin/echo "0 7 * * 1 python $DIR_PATH$EMAIL_FILE" >> $CRON_FILE
	fi

	;;
	
	*)
	
	echo "Usage: $0 {install|update}"
    ;;

esac

cd $DIR_PATH && . $DEPEND_FILE

