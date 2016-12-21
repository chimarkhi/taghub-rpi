sudo crontab /home/pi/tagbox/startup_config/crontab_code.txt
sudo cp /home/pi/tagbox/startup_config/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf

#tzdata
#sudo dpkg-reconfigure tzdata


#sudo reboot
cd bluez-5.37
./configure

make
sudo make install

