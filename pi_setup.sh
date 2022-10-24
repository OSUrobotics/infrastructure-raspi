echo 'KERNEL=="spidev0.0", OWNER="root", GROUP="spi"' > /etc/udev/rules.d/90-gpio-spi.rules
echo 'KERNEL=="spidev0.1", OWNER="root", GROUP="spi"' >> /etc/udev/rules.d/90-gpio-spi.rules
echo 'KERNEL=="spidev1.0", OWNER="root", GROUP="spi"' >> /etc/udev/rules.d/90-gpio-spi.rules
echo 'KERNEL=="i2c-1", OWNER="root", GROUP="i2c"' > /etc/udev/rules.d/91-gpio-i2c.rules
echo 'KERNEL=="i2c-11", OWNER="root", GROUP="i2c"' >> /etc/udev/rules.d/91-gpio-i2c.rules
sudo groupadd -f --system spi
sudo groupadd -f --system i2c
sudo usermod -a -G spi ubuntu
sudo usermod -a -G i2c ubuntu

apt update
apt install python-pip -y
pip install spidev
pip install smbus

echo "enter a new hostname for the pi"

read new_host_name

hostname $new_host_name

echo "$new_host_name" > /etc/hostname
