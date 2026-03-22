

\# Development process

feat/.. (opcionális) 

fejelsztés develop-ba

PR masterre, merge masterre utána

Master deployoljuk prodra







\# Deploying to PROD

Ha van új master verzió

SSH:

&#x20;80.211.194.137

&#x20;root



cd /var/www/smartbox\_nbiot/

(masteren áll)

git pull



Apache2 futtatja

systemctl restart apache2 





\# Apache2

(ez vezérli:

sudo nano /etc/apache2/sites-available/smartbox\_nbiot\_monitor.conf)

