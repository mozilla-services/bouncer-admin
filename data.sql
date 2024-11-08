-- This file is used in tests, and each line gets executed...
SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS bouncer;
USE bouncer;
--
DROP TABLE IF EXISTS `mirror_aliases`;
SET character_set_client = utf8mb4 ;
CREATE TABLE `mirror_aliases` (`id` int(11) NOT NULL AUTO_INCREMENT,`alias` varchar(255) NOT NULL,`related_product` varchar(255) NOT NULL,PRIMARY KEY (`id`),UNIQUE KEY `alias` (`alias`),UNIQUE KEY `uniq_alias` (`alias`)) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
LOCK TABLES `mirror_aliases` WRITE;
INSERT INTO `mirror_aliases` VALUES (1,'firefox-latest','Firefox'),(2,'firefox-sha1','Firefox-43.0.1-SSL');
UNLOCK TABLES;
--
DROP TABLE IF EXISTS `mirror_locations`;
SET character_set_client = utf8mb4 ;
CREATE TABLE `mirror_locations` (`id` int(11) NOT NULL AUTO_INCREMENT,`product_id` int(11) NOT NULL DEFAULT '0',`os_id` int(11) NOT NULL DEFAULT '0',`path` varchar(255) NOT NULL DEFAULT '',PRIMARY KEY (`id`,`product_id`,`os_id`),KEY `product_os_idx` (`product_id`,`os_id`)) ENGINE=InnoDB AUTO_INCREMENT=23260 DEFAULT CHARSET=utf8;
LOCK TABLES `mirror_locations` WRITE;
INSERT INTO `mirror_locations` VALUES (1,1,1,'/firefox/releases/39.0/win64/:lang/Firefox%20Setup%2039.0.exe'),(2,1,2,'/firefox/releases/39.0/mac/:lang/Firefox%2039.0.dmg'),(3,1,3,'/firefox/releases/39.0/win32/:lang/Firefox%20Setup%2039.0.exe'),(4,2,1,'/firefox/releases/39.0/win64/:lang/Firefox%20Setup%2039.0.exe'),(5,2,2,'/firefox/releases/39.0/mac/:lang/Firefox%2039.0.dmg'),(6,2,3,'/firefox/releases/39.0/win32/:lang/Firefox%20Setup%2039.0.exe'),(7,3,1,'/firefox/releases/43.0.1/win64/:lang/Firefox%20Setup%2043.0.1.exe'),(8,3,2,'/firefox/releases/43.0.1/mac/:lang/Firefox%2043.0.1.dmg'),(9,3,3,'/firefox/releases/43.0.1/win32/:lang/Firefox%20Setup%2043.0.1.exe'),(23194,4556,2,'/test');
UNLOCK TABLES;
--
DROP TABLE IF EXISTS `mirror_os`;
SET character_set_client = utf8mb4 ;
CREATE TABLE `mirror_os` (`id` int(10) unsigned NOT NULL AUTO_INCREMENT,`name` varchar(32) NOT NULL DEFAULT '',`priority` int(11) NOT NULL DEFAULT '0',PRIMARY KEY (`id`,`name`)) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;
LOCK TABLES `mirror_os` WRITE;
INSERT INTO `mirror_os` VALUES (1,'win64',0),(2,'osx',0),(3,'win',0),(4,'linux',0),(5,'linux64', 0),(6,'win64-aarch64',0);
UNLOCK TABLES;
--
DROP TABLE IF EXISTS `mirror_product_langs`;
SET character_set_client = utf8mb4 ;
CREATE TABLE `mirror_product_langs` (`id` int(11) NOT NULL AUTO_INCREMENT,`product_id` int(11) NOT NULL,`language` varchar(30) NOT NULL,PRIMARY KEY (`id`),UNIQUE KEY `product_id` (`product_id`,`language`)) ENGINE=InnoDB AUTO_INCREMENT=222156 DEFAULT CHARSET=utf8;
LOCK TABLES `mirror_product_langs` WRITE;
INSERT INTO `mirror_product_langs` VALUES (1,1,'en-GB'),(2,1,'en-US'),(4,2,'en-GB'),(3,2,'en-US'),(5,3,'en-GB'),(6,3,'en-US'),(222155,4556,'en-CA'),(222137,4556,'en-GB'),(222138,4556,'en-US');
UNLOCK TABLES;
--
DROP TABLE IF EXISTS `mirror_products`;
SET character_set_client = utf8mb4 ;
CREATE TABLE `mirror_products` (`id` int(11) NOT NULL AUTO_INCREMENT,`name` varchar(255) NOT NULL DEFAULT '',`priority` int(11) NOT NULL DEFAULT '0',`count` bigint(20) unsigned NOT NULL DEFAULT '0',`active` tinyint(4) NOT NULL DEFAULT '1',`checknow` tinyint(1) unsigned NOT NULL DEFAULT '1',`ssl_only` tinyint(1) NOT NULL DEFAULT '0',PRIMARY KEY (`id`),UNIQUE KEY `product_name` (`name`),KEY `product_count` (`count`),KEY `product_active` (`active`),KEY `product_checknow` (`checknow`)) ENGINE=InnoDB AUTO_INCREMENT=4563 DEFAULT CHARSET=utf8;
LOCK TABLES `mirror_products` WRITE;
INSERT INTO `mirror_products` VALUES (1,'Firefox',1,0,1,1,0),(2,'Firefox-SSL',1,0,1,1,1),(3,'Firefox-43.0.1-SSL',1,0,1,1,1),(4556,'AaronProduct',1,0,1,1,1);
UNLOCK TABLES;
