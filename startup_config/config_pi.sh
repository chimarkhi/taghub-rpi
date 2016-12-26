sudo crontab /home/pi/tagbox/startup_config/crontab_code.txt
sudo cp /home/pi/tagbox/startup_config/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf

#tzdata
#sudo dpkg-reconfigure tzdata


#sudo reboot
cd /home/pi/tagbox/bluez-5.40
./configure

make
sudo make install

