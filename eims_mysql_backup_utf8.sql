-- MySQL dump 10.13  Distrib 8.0.27, for Win64 (x86_64)
--
-- Host: localhost    Database: eims
-- ------------------------------------------------------
-- Server version	8.0.27

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=312 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=193 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add 文件',7,'add_filemanage'),(26,'Can change 文件',7,'change_filemanage'),(27,'Can delete 文件',7,'delete_filemanage'),(28,'Can view 文件',7,'view_filemanage'),(29,'Can add 通知公告',8,'add_notice'),(30,'Can change 通知公告',8,'change_notice'),(31,'Can delete 通知公告',8,'delete_notice'),(32,'Can view 通知公告',8,'view_notice'),(33,'Can add 合同信息',9,'add_contract'),(34,'Can change 合同信息',9,'change_contract'),(35,'Can delete 合同信息',9,'delete_contract'),(36,'Can view 合同信息',9,'view_contract'),(37,'Can add 项目',10,'add_project'),(38,'Can change 项目',10,'change_project'),(39,'Can delete 项目',10,'delete_project'),(40,'Can view 项目',10,'view_project'),(41,'Can add 项目人员',11,'add_personnel'),(42,'Can change 项目人员',11,'change_personnel'),(43,'Can delete 项目人员',11,'delete_personnel'),(44,'Can view 项目人员',11,'view_personnel'),(45,'Can add 项目动态',12,'add_projectdynamic'),(46,'Can change 项目动态',12,'change_projectdynamic'),(47,'Can delete 项目动态',12,'delete_projectdynamic'),(48,'Can view 项目动态',12,'view_projectdynamic'),(49,'Can add 用户资料',13,'add_userprofile'),(50,'Can change 用户资料',13,'change_userprofile'),(51,'Can delete 用户资料',13,'delete_userprofile'),(52,'Can view 用户资料',13,'view_userprofile'),(53,'Can add 产值回款',14,'add_outputpayment'),(54,'Can change 产值回款',14,'change_outputpayment'),(55,'Can delete 产值回款',14,'delete_outputpayment'),(56,'Can view 产值回款',14,'view_outputpayment'),(57,'Can add 月度报告',15,'add_monthlyreport'),(58,'Can change 月度报告',15,'change_monthlyreport'),(59,'Can delete 月度报告',15,'delete_monthlyreport'),(60,'Can view 月度报告',15,'view_monthlyreport'),(61,'Can add 项目填报人员',16,'add_projectreporter'),(62,'Can change 项目填报人员',16,'change_projectreporter'),(63,'Can delete 项目填报人员',16,'delete_projectreporter'),(64,'Can view 项目填报人员',16,'view_projectreporter'),(65,'Can add 角色',17,'add_role'),(66,'Can change 角色',17,'change_role'),(67,'Can delete 角色',17,'delete_role'),(68,'Can view 角色',17,'view_role'),(69,'Can add 审批流程',18,'add_approvalflow'),(70,'Can change 审批流程',18,'change_approvalflow'),(71,'Can delete 审批流程',18,'delete_approvalflow'),(72,'Can view 审批流程',18,'view_approvalflow'),(73,'Can add 审批记录',19,'add_approvalrecord'),(74,'Can change 审批记录',19,'change_approvalrecord'),(75,'Can delete 审批记录',19,'delete_approvalrecord'),(76,'Can view 审批记录',19,'view_approvalrecord'),(77,'Can add 项目角色',20,'add_projectrole'),(78,'Can change 项目角色',20,'change_projectrole'),(79,'Can delete 项目角色',20,'delete_projectrole'),(80,'Can view 项目角色',20,'view_projectrole'),(81,'Can add 人员分配',21,'add_personnelallocation'),(82,'Can change 人员分配',21,'change_personnelallocation'),(83,'Can delete 人员分配',21,'delete_personnelallocation'),(84,'Can view 人员分配',21,'view_personnelallocation'),(85,'Can add 人员证书',22,'add_personnelcertificate'),(86,'Can change 人员证书',22,'change_personnelcertificate'),(87,'Can delete 人员证书',22,'delete_personnelcertificate'),(88,'Can view 人员证书',22,'view_personnelcertificate'),(89,'Can add 部门',23,'add_department'),(90,'Can change 部门',23,'change_department'),(91,'Can delete 部门',23,'delete_department'),(92,'Can view 部门',23,'view_department'),(93,'Can add 审批链配置',24,'add_approvalchain'),(94,'Can change 审批链配置',24,'change_approvalchain'),(95,'Can delete 审批链配置',24,'delete_approvalchain'),(96,'Can view 审批链配置',24,'view_approvalchain'),(97,'Can add 部门角色',25,'add_departmentrole'),(98,'Can change 部门角色',25,'change_departmentrole'),(99,'Can delete 部门角色',25,'delete_departmentrole'),(100,'Can view 部门角色',25,'view_departmentrole'),(101,'Can add 文件访问权限',26,'add_fileaccesspermission'),(102,'Can change 文件访问权限',26,'change_fileaccesspermission'),(103,'Can delete 文件访问权限',26,'delete_fileaccesspermission'),(104,'Can view 文件访问权限',26,'view_fileaccesspermission'),(105,'Can add 文件版本',27,'add_filemanageversion'),(106,'Can change 文件版本',27,'change_filemanageversion'),(107,'Can delete 文件版本',27,'delete_filemanageversion'),(108,'Can view 文件版本',27,'view_filemanageversion'),(109,'Can add 通知附件',28,'add_noticeattachment'),(110,'Can change 通知附件',28,'change_noticeattachment'),(111,'Can delete 通知附件',28,'delete_noticeattachment'),(112,'Can view 通知附件',28,'view_noticeattachment'),(113,'Can add 员工信息',29,'add_employee'),(114,'Can change 员工信息',29,'change_employee'),(115,'Can delete 员工信息',29,'delete_employee'),(116,'Can view 员工信息',29,'view_employee'),(117,'Can add 监理项目信息',30,'add_projectdetail'),(118,'Can change 监理项目信息',30,'change_projectdetail'),(119,'Can delete 监理项目信息',30,'delete_projectdetail'),(120,'Can view 监理项目信息',30,'view_projectdetail'),(121,'Can add 合同审批',31,'add_contractapproval'),(122,'Can change 合同审批',31,'change_contractapproval'),(123,'Can delete 合同审批',31,'delete_contractapproval'),(124,'Can view 合同审批',31,'view_contractapproval'),(125,'Can add 合同审批记录',32,'add_contractapprovalrecord'),(126,'Can change 合同审批记录',32,'change_contractapprovalrecord'),(127,'Can delete 合同审批记录',32,'delete_contractapprovalrecord'),(128,'Can view 合同审批记录',32,'view_contractapprovalrecord'),(129,'Can add 合同附件',33,'add_contractattachment'),(130,'Can change 合同附件',33,'change_contractattachment'),(131,'Can delete 合同附件',33,'delete_contractattachment'),(132,'Can view 合同附件',33,'view_contractattachment'),(133,'Can add 审批流程配置',34,'add_approvalflowconfig'),(134,'Can change 审批流程配置',34,'change_approvalflowconfig'),(135,'Can delete 审批流程配置',34,'delete_approvalflowconfig'),(136,'Can view 审批流程配置',34,'view_approvalflowconfig'),(137,'Can add 部门主管',35,'add_departmentmanager'),(138,'Can change 部门主管',35,'change_departmentmanager'),(139,'Can delete 部门主管',35,'delete_departmentmanager'),(140,'Can view 部门主管',35,'view_departmentmanager'),(141,'Can add 动态选项',36,'add_dynamicchoice'),(142,'Can change 动态选项',36,'change_dynamicchoice'),(143,'Can delete 动态选项',36,'delete_dynamicchoice'),(144,'Can view 动态选项',36,'view_dynamicchoice'),(145,'Can add 短信验证记录',37,'add_smsverificationrecord'),(146,'Can change 短信验证记录',37,'change_smsverificationrecord'),(147,'Can delete 短信验证记录',37,'delete_smsverificationrecord'),(148,'Can view 短信验证记录',37,'view_smsverificationrecord'),(149,'Can add 二维码登录会话',38,'add_qrcodeloginsession'),(150,'Can change 二维码登录会话',38,'change_qrcodeloginsession'),(151,'Can delete 二维码登录会话',38,'delete_qrcodeloginsession'),(152,'Can view 二维码登录会话',38,'view_qrcodeloginsession'),(153,'Can add 微信用户绑定',39,'add_wechatuserbinding'),(154,'Can change 微信用户绑定',39,'change_wechatuserbinding'),(155,'Can delete 微信用户绑定',39,'delete_wechatuserbinding'),(156,'Can view 微信用户绑定',39,'view_wechatuserbinding'),(157,'Can add 微信扫码登录会话',40,'add_wechatqrcodesession'),(158,'Can change 微信扫码登录会话',40,'change_wechatqrcodesession'),(159,'Can delete 微信扫码登录会话',40,'delete_wechatqrcodesession'),(160,'Can view 微信扫码登录会话',40,'view_wechatqrcodesession'),(161,'Can add 归档审批',41,'add_archiveapproval'),(162,'Can change 归档审批',41,'change_archiveapproval'),(163,'Can delete 归档审批',41,'delete_archiveapproval'),(164,'Can view 归档审批',41,'view_archiveapproval'),(165,'Can add 归档附件',42,'add_archiveattachment'),(166,'Can change 归档附件',42,'change_archiveattachment'),(167,'Can delete 归档附件',42,'delete_archiveattachment'),(168,'Can view 归档附件',42,'view_archiveattachment'),(169,'Can add 归档审批记录',43,'add_archiveapprovalrecord'),(170,'Can change 归档审批记录',43,'change_archiveapprovalrecord'),(171,'Can delete 归档审批记录',43,'delete_archiveapprovalrecord'),(172,'Can view 归档审批记录',43,'view_archiveapprovalrecord'),(173,'Can add 用印审批',44,'add_sealapproval'),(174,'Can change 用印审批',44,'change_sealapproval'),(175,'Can delete 用印审批',44,'delete_sealapproval'),(176,'Can view 用印审批',44,'view_sealapproval'),(177,'Can add 用印附件',45,'add_sealattachment'),(178,'Can change 用印附件',45,'change_sealattachment'),(179,'Can delete 用印附件',45,'delete_sealattachment'),(180,'Can view 用印附件',45,'view_sealattachment'),(181,'Can add 用印审批记录',46,'add_sealapprovalrecord'),(182,'Can change 用印审批记录',46,'change_sealapprovalrecord'),(183,'Can delete 用印审批记录',46,'delete_sealapprovalrecord'),(184,'Can view 用印审批记录',46,'view_sealapprovalrecord');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$600000$ctjSu8soHhBtXtrMALyU2f$tC8NWNtjMsM56vAEbKybAPvkBnCGvByYZ+d6q4wW6fo=','2026-04-08 02:15:03.435512',1,'admin','黎绍昆','','51610143@qq.com',1,1,'2026-03-20 18:27:00.000000'),(2,'pbkdf2_sha256$600000$MjIdObVXzZM53EByxVy4wa$Kt1kNYEzIBR2SpqT9PfkH+AM22FLlwDN25UA42xoYmI=','2026-04-05 06:01:41.661915',0,'秦方玉','秦方玉','','zhangsan@example.com',0,1,'2026-03-20 20:55:00.000000'),(3,'pbkdf2_sha256$600000$RZ539Hc485X84ZL9KKCGwK$kU3xbahRPsWhJCFyNyqvQqptYgENFJSSRmnjKotTIfY=','2026-04-07 14:49:22.110861',0,'王璐','王璐','','lisi@example.com',0,1,'2026-03-20 20:55:00.000000'),(4,'pbkdf2_sha256$1000000$cbekf2eQnfHqI9T8gxNWQ5$LudS1hDBmDJ23xmhoroTF237OMTRmhHhJ3C6KHvKv84=',NULL,0,'汪勇','汪勇','','wangwu@example.com',0,1,'2026-03-20 20:55:00.000000'),(5,'pbkdf2_sha256$600000$z6v6U6nbB6GznKmybMJUL4$oqkVlkdK1cL6sEKG6PN0WiZ8YYxmQ8qAckMxSd906vk=','2026-04-07 03:12:38.898740',0,'唐昌成','唐昌成','','zhaoliu@example.com',0,1,'2026-03-20 20:55:00.000000'),(6,'pbkdf2_sha256$1000000$TYZMGRParZhH7HYN91stUt$F/c1/8l6iqYuMIJLn30aHoTTmVlkPHJQ+1Mq9pYEUwA=',NULL,0,'唐昌罗','唐昌罗','','sunqi@example.com',0,1,'2026-03-20 20:55:00.000000'),(7,'pbkdf2_sha256$600000$To7pmNau9LeHFNXrNaEWNf$ea1rw1Awl04SKxWOtvmjcfpuRkUhxsdwuwVRXqiIwQg=','2026-04-07 15:10:04.212991',0,'秦养付','秦养付','','zhouba@example.com',0,1,'2026-03-20 20:55:00.000000'),(8,'pbkdf2_sha256$1000000$StSy1qgrOcYCCDpTf34Vnx$Nwo6dco8GswaDlOT5GFf01rPjo/Rrt7xl/AH92TheAE=',NULL,0,'王立明','王立明','','wujiu@example.com',0,1,'2026-03-20 20:55:00.000000'),(9,'pbkdf2_sha256$1000000$OU4QomYokGCIHuwEBTRnsZ$/860l5ZGofSm4PmtiaLGXtpe9Abn+igoYeIWIoZA+OI=',NULL,0,'李闰','李闰','','zhengshi@example.com',0,1,'2026-03-20 20:55:00.000000'),(10,'pbkdf2_sha256$1000000$KDPPBNMsP7ivUiRu8rO7GP$/FIxT1rj+oOlGQ9m5SVwDyeXqcwswprjtZx7x3SF9BY=','2026-03-22 18:39:00.000000',0,'gxsc','','','',0,1,'2026-03-21 02:17:00.000000'),(11,'pbkdf2_sha256$600000$7ziLOF2iz1kufXmnQnShgu$7BvDWAqVEL2AzUJNU2IKMkcPptsd+khZcEai8K6sWF0=','2026-04-05 06:41:48.240243',0,'王敏志','王敏志','','',0,1,'2026-03-21 07:51:00.000000'),(12,'pbkdf2_sha256$600000$EOLdwydPAWb4zVECBwbg4D$bH4BUGDdAW2koO8bF1E6SIJ4oZPZizY4PKkvcyRNZB0=','2026-04-07 14:45:24.151045',1,'黎绍昆','黎绍昆','','',1,1,'2026-03-21 07:51:00.000000'),(13,'pbkdf2_sha256$1000000$PZsMr2hcyE5roxtKWwSUJx$kAIZ+kbup25/8FyZpH7AACORhO8TJgqtOHiLEkTkJaA=',NULL,0,'易强','易强','','',0,1,'2026-03-21 07:53:00.000000'),(14,'pbkdf2_sha256$600000$XF0JOzb57KB9tkJTqcmAUB$MhrqEoZDEjddvH9dJtIfaBQxYZj2AC5a09AoGFSNmOA=',NULL,0,'唐满东','唐满东','','',0,1,'2026-03-21 08:04:00.000000'),(15,'pbkdf2_sha256$600000$u7adFpkRIuays60BfOVmJ7$fqKiuV1KV8HVQn/oUVmBvwk1A5wBg1ExG87++redpJg=','2026-04-07 14:02:47.487136',0,'秦林','秦林','','',0,1,'2026-03-21 08:05:00.000000'),(16,'pbkdf2_sha256$1000000$Q7XC6ncYHdL5GO1D6hrZ7A$oaeQIwgKsP94e4N0SLFsWF63E9G59bxG3VkPSaQUpZo=',NULL,0,'银雪','银雪','','',0,1,'2026-03-21 23:30:00.000000'),(17,'pbkdf2_sha256$1000000$DmHRik1PSJ9SqVwhxNmzQ9$r43chjv6gX0RTEMwCc1Btz0P0nh7tMxSGBq2C++31z8=',NULL,0,'testuser','','','test@example.com',0,1,'2026-03-25 02:24:52.668514'),(18,'pbkdf2_sha256$1000000$YzOPqDKONJB28QlkG04ZJH$GzjdtNULh0tmG0svG/I/Pmj+NfSMAtkS+7BbpaJccqE=',NULL,0,'唐薇薇','','','',0,1,'2026-03-25 05:00:00.000000'),(19,'pbkdf2_sha256$1000000$puiCDqTBGAbjl8m2aW2Rl5$OFhU3ITe88A/yrDgApyUJSeR3pAtHy6PADPxPz1dP4Q=',NULL,0,'方永明','','','',0,1,'2026-03-25 05:01:00.000000'),(20,'pbkdf2_sha256$1000000$WyTPvDvFkEH5INaN2uNz4n$gCJV1+dRD41GnmonsYo/WhT4Hy8vygUKdt1rDhdEio8=',NULL,0,'宋弦弦','','','',0,1,'2026-03-25 05:02:00.000000'),(21,'pbkdf2_sha256$1000000$sBYOTgZiDgSrAdcmR5uRNr$x7qUAQgDU3C+9fWyLwngk5O2qryfMlqfJjZ5LnJf/g4=',NULL,0,'秦隆刚','','','',0,1,'2026-03-25 05:03:00.000000'),(22,'pbkdf2_sha256$1000000$BnVYqmyubL319zoSdCUWLS$DO7IGbwsT7WzYNjXaFT599MBoxB7n8Anp2kYqbvV4dA=',NULL,0,'黄建波','','','',0,1,'2026-03-25 06:05:00.000000'),(23,'pbkdf2_sha256$1000000$1B3pG01NzHdQmGFDBLOOtR$QLzZy4947YNMaeMRIcHuIDkiUQHABPSAl9GMs6qtgw8=',NULL,0,'廖志红','','','',0,1,'2026-03-25 06:06:00.000000'),(24,'pbkdf2_sha256$1000000$J7B19CqxFNIitKFjp76gnj$h3/Y2WPKdPbYBn4HOzC9sqU24jxyHUEFGsSJOnq90hM=',NULL,0,'程慧慧','','','',0,1,'2026-03-25 06:07:00.000000'),(25,'pbkdf2_sha256$1000000$jYfeWPIgspHF50VaVJCUPs$d37bt9CuM7szw/ODrWIq2Z0WWD71C2aSzdKTrshYKgQ=',NULL,0,'甘丽春','','','',0,1,'2026-03-29 18:16:00.000000'),(26,'pbkdf2_sha256$600000$soT0WNCmlpYXyVsryoxnwN$Ej76vnydFAcyOhGKetTAKypwJLezpir9QXK3pXcDqFo=',NULL,0,'桂华','桂华','','',0,1,'2026-04-01 04:46:03.761922'),(27,'pbkdf2_sha256$600000$9bsZMe2dJQwPmTpbvDWwBn$8ftqdcuv6UuYAJ4LCmQE220a7LJdGRRwBccXOi5KD9k=',NULL,0,'林漓','林漓','','',0,1,'2026-04-01 04:46:23.246973'),(28,'pbkdf2_sha256$600000$OfV3x0nE9zjZuwQQ3pqBy6$3d6VQRV/9o+ZR3KuAsQM+OSRmsv+WKdRCqjscm5d42A=',NULL,0,'庞黎明','庞黎明','','',0,1,'2026-04-01 04:47:10.317572'),(33,'pbkdf2_sha256$600000$YRHU9hqqI1spOq8SBFDwPf$Ek/c+8ocOUHlEPhgLAhnZazXPv9/H20lbHZeJvAhkjs=',NULL,0,'龙欢','龙欢','','',0,1,'2026-04-01 04:47:33.140274'),(36,'pbkdf2_sha256$600000$w5wG77burHM1TRMs4Qkl7d$MstzNl9rYSMhtmnWkImHEE6DytbOHUP3xC2R1/TP/7M=',NULL,0,'周林松','周林松','','',0,1,'2026-04-01 04:48:44.397523'),(44,'pbkdf2_sha256$600000$mrtZXjyV7RZg6ZXd3cPtFv$WgzOvFoY1A+eoXQ+GWnpdfD9mcxNywM4ULl+58QR/Gc=',NULL,0,'唐鹏','唐鹏','','',0,1,'2026-04-04 06:38:01.132000'),(45,'pbkdf2_sha256$600000$wCqJkzLBpkPhBG0QZnYJMQ$u/7iAR2LsYMn7MlSn92cbWH4bamyASJwDon5j7hHyl8=',NULL,0,'谢荣明','谢荣明','','',0,1,'2026-04-04 06:38:04.870000'),(47,'pbkdf2_sha256$600000$bBNpRIHeRdq081TsP7W3o2$pDkARApwJZ+e+p9VOA5UIwyETkfOO7jspoTtv8HluRs=',NULL,0,'吴向南','吴向南','','',0,1,'2026-04-04 06:38:13.590000'),(50,'pbkdf2_sha256$600000$ht0S3gUXCd24EgdSxuADha$MGKOw4NpfBcG8l6jcAVjxDWYGmiaS0XpDjCU2mp2I44=',NULL,0,'阳著平','阳著平','','',0,1,'2026-04-04 06:38:27.848000'),(52,'pbkdf2_sha256$600000$3kxCmciulndtxjzeQSKDdf$wO7mXepsvXH3K8b6HZzNOX/q4WLgSVZFyU37TtqzCTI=','2026-04-04 15:49:36.709000',0,'陈连华','','','',0,1,'2026-04-04 15:45:46.594000');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=413 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(24,'eims_app','approvalchain'),(18,'eims_app','approvalflow'),(34,'eims_app','approvalflowconfig'),(19,'eims_app','approvalrecord'),(41,'eims_app','archiveapproval'),(43,'eims_app','archiveapprovalrecord'),(42,'eims_app','archiveattachment'),(9,'eims_app','contract'),(31,'eims_app','contractapproval'),(32,'eims_app','contractapprovalrecord'),(33,'eims_app','contractattachment'),(23,'eims_app','department'),(35,'eims_app','departmentmanager'),(25,'eims_app','departmentrole'),(36,'eims_app','dynamicchoice'),(29,'eims_app','employee'),(26,'eims_app','fileaccesspermission'),(7,'eims_app','filemanage'),(27,'eims_app','filemanageversion'),(15,'eims_app','monthlyreport'),(8,'eims_app','notice'),(28,'eims_app','noticeattachment'),(14,'eims_app','outputpayment'),(11,'eims_app','personnel'),(21,'eims_app','personnelallocation'),(22,'eims_app','personnelcertificate'),(10,'eims_app','project'),(30,'eims_app','projectdetail'),(12,'eims_app','projectdynamic'),(16,'eims_app','projectreporter'),(20,'eims_app','projectrole'),(38,'eims_app','qrcodeloginsession'),(17,'eims_app','role'),(44,'eims_app','sealapproval'),(46,'eims_app','sealapprovalrecord'),(45,'eims_app','sealattachment'),(37,'eims_app','smsverificationrecord'),(13,'eims_app','userprofile'),(40,'eims_app','wechatqrcodesession'),(39,'eims_app','wechatuserbinding'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-04-08 02:00:47.642185'),(2,'auth','0001_initial','2026-04-08 02:00:48.158075'),(3,'admin','0001_initial','2026-04-08 02:00:48.307139'),(4,'admin','0002_logentry_remove_auto_add','2026-04-08 02:00:48.315270'),(5,'admin','0003_logentry_add_action_flag_choices','2026-04-08 02:00:48.323916'),(6,'contenttypes','0002_remove_content_type_name','2026-04-08 02:00:48.430737'),(7,'auth','0002_alter_permission_name_max_length','2026-04-08 02:00:48.484806'),(8,'auth','0003_alter_user_email_max_length','2026-04-08 02:00:48.501848'),(9,'auth','0004_alter_user_username_opts','2026-04-08 02:00:48.508136'),(10,'auth','0005_alter_user_last_login_null','2026-04-08 02:00:48.558997'),(11,'auth','0006_require_contenttypes_0002','2026-04-08 02:00:48.562643'),(12,'auth','0007_alter_validators_add_error_messages','2026-04-08 02:00:48.568534'),(13,'auth','0008_alter_user_username_max_length','2026-04-08 02:00:48.624405'),(14,'auth','0009_alter_user_last_name_max_length','2026-04-08 02:00:48.678464'),(15,'auth','0010_alter_group_name_max_length','2026-04-08 02:00:48.691900'),(16,'auth','0011_update_proxy_permissions','2026-04-08 02:00:48.697931'),(17,'auth','0012_alter_user_first_name_max_length','2026-04-08 02:00:48.755454'),(18,'eims_app','0001_initial','2026-04-08 02:00:49.875366'),(19,'eims_app','0002_outputpayment_is_deleted_personnel_is_deleted_and_more','2026-04-08 02:00:49.949572'),(20,'eims_app','0003_role_approvalflow_approvalrecord_projectrole','2026-04-08 02:00:50.553263'),(21,'eims_app','0004_personnel_address_personnel_admin_position_and_more','2026-04-08 02:00:51.317758'),(22,'eims_app','0005_department_approvalchain_departmentrole_and_more','2026-04-08 02:00:52.017692'),(23,'eims_app','0006_alter_department_options_alter_filemanage_options_and_more','2026-04-08 02:00:52.192394'),(24,'eims_app','0007_alter_filemanage_publish_time_and_more','2026-04-08 02:00:52.229005'),(25,'eims_app','0008_notice_file_name_notice_file_size_notice_file_type','2026-04-08 02:00:52.285954'),(26,'eims_app','0009_fileaccesspermission_filemanageversion_and_more','2026-04-08 02:00:52.604585'),(27,'eims_app','0010_employee_remove_personnel_address_and_more','2026-04-08 02:00:53.616478'),(28,'eims_app','0011_personnelallocation_allocation_department_and_more','2026-04-08 02:00:53.659379'),(29,'eims_app','0012_remove_monthlyreport_next_month_plan_and_more','2026-04-08 02:00:54.277684'),(30,'eims_app','0013_alter_monthlyreport_report_month','2026-04-08 02:00:54.361316'),(31,'eims_app','0014_alter_project_project_manager_projectdetail','2026-04-08 02:00:54.518216'),(32,'eims_app','0015_alter_inspection_project_alter_monthlyreport_project_and_more','2026-04-08 02:00:55.419928'),(33,'eims_app','0016_alter_projectdetail_signing_date','2026-04-08 02:00:55.505817'),(34,'eims_app','0017_contractapproval_contractapprovalrecord_and_more','2026-04-08 02:00:55.998452'),(35,'eims_app','0018_remove_contractapproval_service_period_and_more','2026-04-08 02:00:56.330888'),(36,'eims_app','0019_contractapproval_approval_flow_type_and_more','2026-04-08 02:00:57.020217'),(37,'eims_app','0020_contractapproval_initiation_time_and_more','2026-04-08 02:00:57.132671'),(38,'eims_app','0021_dynamicchoice','2026-04-08 02:00:57.219162'),(39,'eims_app','0022_projectdetail_update_field_labels','2026-04-08 02:00:57.240592'),(40,'eims_app','0023_delete_infocollect_remove_inspection_project_and_more','2026-04-08 02:00:58.552252'),(41,'eims_app','0024_employee_email','2026-04-08 02:00:58.574568'),(42,'eims_app','0025_alter_personnelallocation_to_project_and_more','2026-04-08 02:00:58.718732'),(43,'eims_app','0026_smsverificationrecord','2026-04-08 02:00:58.813773'),(44,'eims_app','0027_notice_keywords_upload_person','2026-04-08 02:00:58.878192'),(45,'eims_app','0028_add_create_time_field','2026-04-08 02:00:58.906031'),(46,'eims_app','0029_modify_publish_time_nullable','2026-04-08 02:00:58.944518'),(47,'eims_app','0030_remove_publish_time_field','2026-04-08 02:00:58.982738'),(48,'eims_app','0031_remove_upload_person_field','2026-04-08 02:00:59.016537'),(49,'eims_app','0032_alter_notice_options_filemanage_file_format','2026-04-08 02:00:59.035739'),(50,'eims_app','0033_departmentrole_supervisor','2026-04-08 02:00:59.101894'),(51,'eims_app','0034_qrcodeloginsession','2026-04-08 02:00:59.197075'),(52,'eims_app','0035_wechatuserbinding_wechatqrcodesession','2026-04-08 02:00:59.460801'),(53,'eims_app','0036_contractapprovalrecord_next_approver','2026-04-08 02:00:59.524041'),(54,'eims_app','0037_archiveapproval_alter_contract_contract_amount_and_more','2026-04-08 02:01:00.177944'),(55,'eims_app','0038_sealapproval_sealattachment_sealapprovalrecord','2026-04-08 02:01:00.922203'),(56,'sessions','0001_initial','2026-04-08 02:01:00.953839');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('x0nr832s3eon1qldtsskzwggk25oa9a6','.eJxVjEEOgyAUBe_y141REBF3tWfomnzwEUgjNYKrpndvmrhotzOZeZHlo0Z7FOw2LTRRR5df5tg_kL8CaS2Wt605UWluMWUU3Av2zCuuR43INXmu6ZnnM_y7RS6RJjLeeCGBPsi2Y9mpoLTU7SgWjNDGc9sHKC0x6F44Nxh2wiitgxeLAzt6fwCIFz3p:1wAIXT:GoPmWWitZYm4vaz0Mae9m1cJDtUvgxMuBPhliqzvi64','2026-04-22 02:21:07.529930');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_approvalchain`
--

DROP TABLE IF EXISTS `eims_app_approvalchain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_approvalchain` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `is_deleted` tinyint(1) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `business_type` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `chain_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `level_1_role` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `level_2_role` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `level_3_role` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `need_cross_department` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `level_1_department_id` bigint NOT NULL,
  `level_2_department_id` bigint DEFAULT NULL,
  `level_3_department_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_approvalcha_level_1_department_i_f1b95e03_fk_eims_app_` (`level_1_department_id`),
  KEY `eims_app_approvalcha_level_2_department_i_3db290de_fk_eims_app_` (`level_2_department_id`),
  KEY `eims_app_approvalcha_level_3_department_i_a78d693e_fk_eims_app_` (`level_3_department_id`),
  CONSTRAINT `eims_app_approvalcha_level_1_department_i_f1b95e03_fk_eims_app_` FOREIGN KEY (`level_1_department_id`) REFERENCES `eims_app_department` (`id`),
  CONSTRAINT `eims_app_approvalcha_level_2_department_i_3db290de_fk_eims_app_` FOREIGN KEY (`level_2_department_id`) REFERENCES `eims_app_department` (`id`),
  CONSTRAINT `eims_app_approvalcha_level_3_department_i_a78d693e_fk_eims_app_` FOREIGN KEY (`level_3_department_id`) REFERENCES `eims_app_department` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_approvalchain`
--

LOCK TABLES `eims_app_approvalchain` WRITE;
/*!40000 ALTER TABLE `eims_app_approvalchain` DISABLE KEYS */;
INSERT INTO `eims_app_approvalchain` VALUES (1,0,'2026-03-21 01:27:10.865827','2026-03-21 09:03:26.331562','人员分配审批流程','personnel_allocate','sequential','','部门经理','人事经理','',1,1,1,7,NULL),(2,0,'2026-03-21 01:27:33.815699','2026-03-21 09:03:02.057303','人员分配审批流程','personnel_allocate','sequential','','部门经理','人事经理','',1,1,1,7,NULL),(3,0,'2026-03-21 01:27:33.824540','2026-03-21 01:27:33.824557','人员调动审批流程','personnel_transfer','sequential','','部门经理','人事总监','',1,1,1,7,NULL);
/*!40000 ALTER TABLE `eims_app_approvalchain` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_approvalchain_cross_departments`
--

DROP TABLE IF EXISTS `eims_app_approvalchain_cross_departments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_approvalchain_cross_departments` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `approvalchain_id` bigint NOT NULL,
  `department_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `eims_app_approvalchain_c_approvalchain_id_departm_2db2f4fe_uniq` (`approvalchain_id`,`department_id`),
  KEY `eims_app_approvalcha_department_id_4ef3564d_fk_eims_app_` (`department_id`),
  CONSTRAINT `eims_app_approvalcha_approvalchain_id_a2729e4b_fk_eims_app_` FOREIGN KEY (`approvalchain_id`) REFERENCES `eims_app_approvalchain` (`id`),
  CONSTRAINT `eims_app_approvalcha_department_id_4ef3564d_fk_eims_app_` FOREIGN KEY (`department_id`) REFERENCES `eims_app_department` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_approvalchain_cross_departments`
--

LOCK TABLES `eims_app_approvalchain_cross_departments` WRITE;
/*!40000 ALTER TABLE `eims_app_approvalchain_cross_departments` DISABLE KEYS */;
INSERT INTO `eims_app_approvalchain_cross_departments` VALUES (7,1,1),(8,1,2),(9,1,3),(10,1,4),(11,1,5),(12,1,6),(13,1,7),(14,1,8),(3,2,2),(4,2,3),(5,2,4),(6,2,5),(1,2,6),(2,3,6);
/*!40000 ALTER TABLE `eims_app_approvalchain_cross_departments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_approvalflow`
--

DROP TABLE IF EXISTS `eims_app_approvalflow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_approvalflow` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `current_step` int NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `initiate_time` datetime(6) NOT NULL,
  `director_review_time` datetime(6) DEFAULT NULL,
  `director_opinion` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `director_passed` tinyint(1) DEFAULT NULL,
  `approval_time` datetime(6) DEFAULT NULL,
  `approval_opinion` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `approval_passed` tinyint(1) DEFAULT NULL,
  `approver_id` int DEFAULT NULL,
  `director_id` int DEFAULT NULL,
  `initiator_id` int DEFAULT NULL,
  `report_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `report_id` (`report_id`),
  KEY `eims_app_approvalflow_approver_id_b71a18ea_fk_auth_user_id` (`approver_id`),
  KEY `eims_app_approvalflow_director_id_1ce183c6_fk_auth_user_id` (`director_id`),
  KEY `eims_app_approvalflow_initiator_id_541f18e5_fk_auth_user_id` (`initiator_id`),
  CONSTRAINT `eims_app_approvalflo_report_id_98a696fe_fk_eims_app_` FOREIGN KEY (`report_id`) REFERENCES `eims_app_monthlyreport` (`id`),
  CONSTRAINT `eims_app_approvalflow_approver_id_b71a18ea_fk_auth_user_id` FOREIGN KEY (`approver_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_approvalflow_director_id_1ce183c6_fk_auth_user_id` FOREIGN KEY (`director_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_approvalflow_initiator_id_541f18e5_fk_auth_user_id` FOREIGN KEY (`initiator_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_approvalflow`
--

LOCK TABLES `eims_app_approvalflow` WRITE;
/*!40000 ALTER TABLE `eims_app_approvalflow` DISABLE KEYS */;
/*!40000 ALTER TABLE `eims_app_approvalflow` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_approvalflowconfig`
--

DROP TABLE IF EXISTS `eims_app_approvalflowconfig`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_approvalflowconfig` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `flow_type` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `approval_level` int NOT NULL,
  `approver_role` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `priority` int NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `department_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `eims_app_approvalflowcon_flow_type_department_id__b8f862fe_uniq` (`flow_type`,`department_id`,`approval_level`),
  KEY `eims_app_approvalflo_department_id_d9ebd24f_fk_eims_app_` (`department_id`),
  CONSTRAINT `eims_app_approvalflo_department_id_d9ebd24f_fk_eims_app_` FOREIGN KEY (`department_id`) REFERENCES `eims_app_department` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_approvalflowconfig`
--

LOCK TABLES `eims_app_approvalflowconfig` WRITE;
/*!40000 ALTER TABLE `eims_app_approvalflowconfig` DISABLE KEYS */;
/*!40000 ALTER TABLE `eims_app_approvalflowconfig` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_approvalrecord`
--

DROP TABLE IF EXISTS `eims_app_approvalrecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_approvalrecord` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `opinion` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `flow_id` bigint NOT NULL,
  `operator_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_approvalrec_flow_id_e45d7a75_fk_eims_app_` (`flow_id`),
  KEY `eims_app_approvalrecord_operator_id_a78052db_fk_auth_user_id` (`operator_id`),
  CONSTRAINT `eims_app_approvalrec_flow_id_e45d7a75_fk_eims_app_` FOREIGN KEY (`flow_id`) REFERENCES `eims_app_approvalflow` (`id`),
  CONSTRAINT `eims_app_approvalrecord_operator_id_a78052db_fk_auth_user_id` FOREIGN KEY (`operator_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_approvalrecord`
--

LOCK TABLES `eims_app_approvalrecord` WRITE;
/*!40000 ALTER TABLE `eims_app_approvalrecord` DISABLE KEYS */;
/*!40000 ALTER TABLE `eims_app_approvalrecord` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_archiveapproval`
--

DROP TABLE IF EXISTS `eims_app_archiveapproval`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_archiveapproval` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `initiation_time` datetime(6) DEFAULT NULL,
  `archive_date` date DEFAULT NULL,
  `archive_location` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `archive_period` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_files` int NOT NULL,
  `total_pages` int NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `approval_flow_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `approval_level` int NOT NULL,
  `max_approval_level` int NOT NULL,
  `approval_result` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `submitted_at` datetime(6) DEFAULT NULL,
  `approved_at` datetime(6) DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  `deleted_at` datetime(6) DEFAULT NULL,
  `applicant_id` int DEFAULT NULL,
  `auto_assigned_approver_id` int DEFAULT NULL,
  `current_approver_id` int DEFAULT NULL,
  `department_id` bigint DEFAULT NULL,
  `initiator_id` int DEFAULT NULL,
  `selected_approver_id` int DEFAULT NULL,
  `selected_department_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_archiveapproval_applicant_id_85ed01c4_fk_auth_user_id` (`applicant_id`),
  KEY `eims_app_archiveappr_auto_assigned_approv_3fd0a9c3_fk_auth_user` (`auto_assigned_approver_id`),
  KEY `eims_app_archiveappr_current_approver_id_dc8deba4_fk_auth_user` (`current_approver_id`),
  KEY `eims_app_archiveappr_department_id_1330f0f4_fk_eims_app_` (`department_id`),
  KEY `eims_app_archiveapproval_initiator_id_e86eef14_fk_auth_user_id` (`initiator_id`),
  KEY `eims_app_archiveappr_selected_approver_id_feb72c3a_fk_auth_user` (`selected_approver_id`),
  KEY `eims_app_archiveappr_selected_department__5122fa09_fk_eims_app_` (`selected_department_id`),
  CONSTRAINT `eims_app_archiveappr_auto_assigned_approv_3fd0a9c3_fk_auth_user` FOREIGN KEY (`auto_assigned_approver_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_archiveappr_current_approver_id_dc8deba4_fk_auth_user` FOREIGN KEY (`current_approver_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_archiveappr_department_id_1330f0f4_fk_eims_app_` FOREIGN KEY (`department_id`) REFERENCES `eims_app_department` (`id`),
  CONSTRAINT `eims_app_archiveappr_selected_approver_id_feb72c3a_fk_auth_user` FOREIGN KEY (`selected_approver_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_archiveappr_selected_department__5122fa09_fk_eims_app_` FOREIGN KEY (`selected_department_id`) REFERENCES `eims_app_department` (`id`),
  CONSTRAINT `eims_app_archiveapproval_applicant_id_85ed01c4_fk_auth_user_id` FOREIGN KEY (`applicant_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_archiveapproval_initiator_id_e86eef14_fk_auth_user_id` FOREIGN KEY (`initiator_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_archiveapproval`
--

LOCK TABLES `eims_app_archiveapproval` WRITE;
/*!40000 ALTER TABLE `eims_app_archiveapproval` DISABLE KEYS */;
INSERT INTO `eims_app_archiveapproval` VALUES (1,'灌阳项目归档','灌阳县财政局2023年农村综合改革转移支付资金项目','','2026-04-07 07:14:05.279608',NULL,'','long_term',2,1,'reviewing','user_selected',3,2,NULL,'','2026-04-07 06:58:02.534380','2026-04-07 13:36:43.456692','2026-04-07 07:14:05.279591',NULL,0,NULL,3,NULL,11,1,3,12,1);
/*!40000 ALTER TABLE `eims_app_archiveapproval` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_archiveapprovalrecord`
--

DROP TABLE IF EXISTS `eims_app_archiveapprovalrecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_archiveapprovalrecord` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `comment` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `approval_id` bigint NOT NULL,
  `next_approver_id` int DEFAULT NULL,
  `operator_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_archiveappr_approval_id_cdb2896c_fk_eims_app_` (`approval_id`),
  KEY `eims_app_archiveappr_next_approver_id_cd2426e5_fk_auth_user` (`next_approver_id`),
  KEY `eims_app_archiveappr_operator_id_3c5abd60_fk_auth_user` (`operator_id`),
  CONSTRAINT `eims_app_archiveappr_approval_id_cdb2896c_fk_eims_app_` FOREIGN KEY (`approval_id`) REFERENCES `eims_app_archiveapproval` (`id`),
  CONSTRAINT `eims_app_archiveappr_next_approver_id_cd2426e5_fk_auth_user` FOREIGN KEY (`next_approver_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_archiveappr_operator_id_3c5abd60_fk_auth_user` FOREIGN KEY (`operator_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_archiveapprovalrecord`
--

LOCK TABLES `eims_app_archiveapprovalrecord` WRITE;
/*!40000 ALTER TABLE `eims_app_archiveapprovalrecord` DISABLE KEYS */;
INSERT INTO `eims_app_archiveapprovalrecord` VALUES (1,'submit','提交审批','2026-04-07 07:14:05.286275',1,NULL,3),(2,'approve','同意归档','2026-04-07 07:15:37.975616',1,NULL,12),(3,'approve','请王总审批','2026-04-07 13:36:43.460762',1,NULL,12);
/*!40000 ALTER TABLE `eims_app_archiveapprovalrecord` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_archiveattachment`
--

DROP TABLE IF EXISTS `eims_app_archiveattachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_archiveattachment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_size` int NOT NULL,
  `pages` int NOT NULL,
  `document_date` date DEFAULT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  `approval_id` bigint NOT NULL,
  `uploaded_by_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_archiveatta_approval_id_80c7d9c4_fk_eims_app_` (`approval_id`),
  KEY `eims_app_archiveatta_uploaded_by_id_38db46b2_fk_auth_user` (`uploaded_by_id`),
  CONSTRAINT `eims_app_archiveatta_approval_id_80c7d9c4_fk_eims_app_` FOREIGN KEY (`approval_id`) REFERENCES `eims_app_archiveapproval` (`id`),
  CONSTRAINT `eims_app_archiveatta_uploaded_by_id_38db46b2_fk_auth_user` FOREIGN KEY (`uploaded_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_archiveattachment`
--

LOCK TABLES `eims_app_archiveattachment` WRITE;
/*!40000 ALTER TABLE `eims_app_archiveattachment` DISABLE KEYS */;
INSERT INTO `eims_app_archiveattachment` VALUES (1,'archive_approvals/2026/04/文件结构.png','contract','文件结构.png',35925,0,NULL,'','2026-04-07 06:58:02.540891',0,1,NULL),(2,'archive_approvals/2026/04/260306九马画山徒步团建.jpg','contract','260306九马画山徒步团建.jpg',293435,1,NULL,'','2026-04-07 07:13:52.840780',0,1,NULL);
/*!40000 ALTER TABLE `eims_app_archiveattachment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_contract`
--

DROP TABLE IF EXISTS `eims_app_contract`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_contract` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `is_deleted` tinyint(1) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contract_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contract_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contract_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contract_amount` decimal(12,2) NOT NULL,
  `signing_time` date DEFAULT NULL,
  `project_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `party_a` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_address` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_scale` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_investment` decimal(15,2) NOT NULL,
  `contract_party_a` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contract_party_b` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contract_text` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `payment_agreement` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `agreed_staffing` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `service_period` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `service_deadline` date DEFAULT NULL,
  `planned_start_time` date DEFAULT NULL,
  `estimated_completion_time` date DEFAULT NULL,
  `extension_agreement` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `contract_code` (`contract_code`),
  KEY `eims_app_Contract_status_79e7acc2` (`status`),
  KEY `eims_app_Contract_contract_type_a5029d67` (`contract_type`),
  KEY `eims_app_Contract_contract_name_6a8b8444` (`contract_name`),
  KEY `eims_app_Contract_signing_time_4bcfbe19` (`signing_time`),
  KEY `eims_app_Contract_project_code_51d1af91` (`project_code`),
  KEY `eims_app_Co_status_cc4add_idx` (`status`,`signing_time` DESC),
  KEY `eims_app_Co_contrac_c25797_idx` (`contract_type`,`signing_time` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_contract`
--

LOCK TABLES `eims_app_contract` WRITE;
/*!40000 ALTER TABLE `eims_app_contract` DISABLE KEYS */;
/*!40000 ALTER TABLE `eims_app_contract` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_contractapproval`
--

DROP TABLE IF EXISTS `eims_app_contractapproval`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_contractapproval` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contract_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contract_category` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contract_amount` decimal(15,2) DEFAULT NULL,
  `party_a` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `party_b` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `service_deadline` date DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `approval_result` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `submitted_at` datetime(6) DEFAULT NULL,
  `approved_at` datetime(6) DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  `deleted_at` datetime(6) DEFAULT NULL,
  `applicant_id` int DEFAULT NULL,
  `current_approver_id` int DEFAULT NULL,
  `department_id` bigint DEFAULT NULL,
  `generated_contract_id` bigint DEFAULT NULL,
  `service_period_months` int NOT NULL,
  `service_start_date` date DEFAULT NULL,
  `approval_flow_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `approval_level` int NOT NULL,
  `auto_assigned_approver_id` int DEFAULT NULL,
  `max_approval_level` int NOT NULL,
  `selected_approver_id` int DEFAULT NULL,
  `selected_department_id` bigint DEFAULT NULL,
  `initiation_time` datetime(6) DEFAULT NULL,
  `initiator_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_contractapproval_applicant_id_e2b28db8_fk_auth_user_id` (`applicant_id`),
  KEY `eims_app_contractapp_current_approver_id_1881f433_fk_auth_user` (`current_approver_id`),
  KEY `eims_app_contractapp_department_id_f609315a_fk_eims_app_` (`department_id`),
  KEY `eims_app_contractapp_generated_contract_i_2cc4a0c6_fk_eims_app_` (`generated_contract_id`),
  KEY `eims_app_contractapp_auto_assigned_approv_782cca90_fk_auth_user` (`auto_assigned_approver_id`),
  KEY `eims_app_contractapp_selected_approver_id_f50f81e4_fk_auth_user` (`selected_approver_id`),
  KEY `eims_app_contractapp_selected_department__1fbd73cb_fk_eims_app_` (`selected_department_id`),
  KEY `eims_app_contractapproval_initiator_id_d99cc0bf_fk_auth_user_id` (`initiator_id`),
  CONSTRAINT `eims_app_contractapp_auto_assigned_approv_782cca90_fk_auth_user` FOREIGN KEY (`auto_assigned_approver_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_contractapp_current_approver_id_1881f433_fk_auth_user` FOREIGN KEY (`current_approver_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_contractapp_department_id_f609315a_fk_eims_app_` FOREIGN KEY (`department_id`) REFERENCES `eims_app_department` (`id`),
  CONSTRAINT `eims_app_contractapp_generated_contract_i_2cc4a0c6_fk_eims_app_` FOREIGN KEY (`generated_contract_id`) REFERENCES `eims_app_projectdetail` (`id`),
  CONSTRAINT `eims_app_contractapp_selected_approver_id_f50f81e4_fk_auth_user` FOREIGN KEY (`selected_approver_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_contractapp_selected_department__1fbd73cb_fk_eims_app_` FOREIGN KEY (`selected_department_id`) REFERENCES `eims_app_department` (`id`),
  CONSTRAINT `eims_app_contractapproval_applicant_id_e2b28db8_fk_auth_user_id` FOREIGN KEY (`applicant_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_contractapproval_initiator_id_d99cc0bf_fk_auth_user_id` FOREIGN KEY (`initiator_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_contractapproval`
--

LOCK TABLES `eims_app_contractapproval` WRITE;
/*!40000 ALTER TABLE `eims_app_contractapproval` DISABLE KEYS */;
INSERT INTO `eims_app_contractapproval` VALUES (1,'1','1','engineering_supervision',1.00,'2','2','2026-04-06','reviewing',NULL,'请黎总审批!','2026-03-25 01:12:10.005294','2026-04-05 06:26:05.419959','2026-03-28 02:23:30.240681',NULL,0,NULL,1,11,1,NULL,1,'2026-03-06','user_selected',2,NULL,2,12,1,'2026-03-28 02:23:30.234434',2),(2,'桂林五环电器制造有限公司特高压电抗器生产线建设项目工程监理','特高压电抗器生产线建设项目工程监理','engineering_supervision',155900.00,'桂林五环电器制造有限公司','华建嘉质建设有限公司',NULL,'approved','pending','请王总审批','2026-03-25 01:21:58.148022','2026-04-05 15:28:07.136545','2026-03-25 02:35:26.801431','2026-04-05 15:28:07.125025',0,NULL,1,12,1,97,10,NULL,'user_selected',3,NULL,2,11,1,'2026-03-25 02:35:26.794346',12),(3,'2','2','engineering_supervision',2.00,'3','3','2026-06-13','cancelled',NULL,'','2026-03-28 02:32:55.319149','2026-04-05 05:31:18.205880','2026-03-28 02:33:21.714517',NULL,0,NULL,2,12,1,NULL,3,'2026-03-13','user_selected',1,NULL,2,12,1,'2026-03-28 02:33:21.709704',2),(4,'333','3333','engineering_supervision',3.00,'3','3',NULL,'cancelled',NULL,'','2026-03-28 02:41:10.455240','2026-04-05 05:08:14.978826','2026-04-05 05:08:07.371026',NULL,0,NULL,2,12,1,NULL,3,NULL,'user_selected',1,NULL,2,12,1,'2026-03-28 02:41:55.215496',2),(5,'4','4','engineering_supervision',4.00,'4','4',NULL,'approved','pending','','2026-03-28 03:10:03.713762','2026-04-04 16:22:12.242561','2026-03-28 03:10:23.332800','2026-04-04 16:22:12.228724',0,NULL,2,12,1,95,4,NULL,'user_selected',1,NULL,2,12,1,'2026-03-28 03:10:23.325325',2),(6,'55','55','engineering_supervision',55.00,'55','55',NULL,'approved','pending','','2026-04-05 05:48:00.721931','2026-04-05 06:07:22.873071','2026-04-05 06:04:09.506224','2026-04-05 06:07:22.864178',0,NULL,2,12,1,96,5,NULL,'user_selected',1,NULL,2,12,NULL,'2026-04-05 05:48:47.526743',2);
/*!40000 ALTER TABLE `eims_app_contractapproval` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_contractapprovalrecord`
--

DROP TABLE IF EXISTS `eims_app_contractapprovalrecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_contractapprovalrecord` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `comment` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `approval_id` bigint NOT NULL,
  `operator_id` int DEFAULT NULL,
  `next_approver_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_contractapp_approval_id_25370695_fk_eims_app_` (`approval_id`),
  KEY `eims_app_contractapp_operator_id_993b53ee_fk_auth_user` (`operator_id`),
  KEY `eims_app_contractapp_next_approver_id_b0a72b13_fk_auth_user` (`next_approver_id`),
  CONSTRAINT `eims_app_contractapp_approval_id_25370695_fk_eims_app_` FOREIGN KEY (`approval_id`) REFERENCES `eims_app_contractapproval` (`id`),
  CONSTRAINT `eims_app_contractapp_next_approver_id_b0a72b13_fk_auth_user` FOREIGN KEY (`next_approver_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_contractapp_operator_id_993b53ee_fk_auth_user` FOREIGN KEY (`operator_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_contractapprovalrecord`
--

LOCK TABLES `eims_app_contractapprovalrecord` WRITE;
/*!40000 ALTER TABLE `eims_app_contractapprovalrecord` DISABLE KEYS */;
INSERT INTO `eims_app_contractapprovalrecord` VALUES (1,'submit','提交审批','2026-03-25 02:35:26.805088',2,12,NULL),(2,'submit','提交审批','2026-03-28 02:23:30.244743',1,2,NULL),(3,'submit','提交审批','2026-03-28 02:33:21.719229',3,2,NULL),(4,'submit','提交审批','2026-03-28 02:41:55.226473',4,2,NULL),(5,'submit','提交审批','2026-03-28 03:10:23.337325',5,2,NULL),(6,'approve','同意','2026-04-04 16:22:12.247368',5,12,NULL),(7,'reject','上传附件','2026-04-04 21:47:59.699153',4,12,NULL),(8,'submit','提交审批','2026-04-04 21:48:16.543844',4,12,NULL),(9,'reject','附件没上传','2026-04-05 04:30:17.918013',4,12,NULL),(10,'submit','提交审批','2026-04-05 05:08:07.375609',4,2,NULL),(11,'cancel','撤销审批','2026-04-05 05:08:14.985472',4,2,NULL),(12,'cancel','撤销审批','2026-04-05 05:31:18.209793',3,2,NULL),(13,'submit','提交审批','2026-04-05 05:48:47.540048',6,2,NULL),(14,'cancel','撤销审批','2026-04-05 05:50:05.549848',6,2,NULL),(15,'submit','提交审批','2026-04-05 06:04:09.510983',6,2,NULL),(16,'approve','同意','2026-04-05 06:07:22.876989',6,12,NULL),(17,'approve','同意','2026-04-05 06:26:05.410699',1,12,NULL),(18,'approve','同意','2026-04-05 06:42:30.573630',2,11,NULL),(19,'approve','同意','2026-04-05 06:42:30.581588',2,11,15),(20,'approve','同意','2026-04-05 15:26:44.538540',2,15,NULL),(21,'approve','同意并转发','2026-04-05 15:26:44.547919',2,15,12),(22,'approve','同意','2026-04-05 15:28:07.121560',2,12,NULL),(23,'approve','同意','2026-04-05 15:28:07.129070',2,12,NULL);
/*!40000 ALTER TABLE `eims_app_contractapprovalrecord` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_contractattachment`
--

DROP TABLE IF EXISTS `eims_app_contractattachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_contractattachment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_size` int NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  `approval_id` bigint NOT NULL,
  `uploaded_by_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_contractatt_approval_id_d7ef7032_fk_eims_app_` (`approval_id`),
  KEY `eims_app_contractatt_uploaded_by_id_c64e1dc5_fk_auth_user` (`uploaded_by_id`),
  CONSTRAINT `eims_app_contractatt_approval_id_d7ef7032_fk_eims_app_` FOREIGN KEY (`approval_id`) REFERENCES `eims_app_contractapproval` (`id`),
  CONSTRAINT `eims_app_contractatt_uploaded_by_id_c64e1dc5_fk_auth_user` FOREIGN KEY (`uploaded_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_contractattachment`
--

LOCK TABLES `eims_app_contractattachment` WRITE;
/*!40000 ALTER TABLE `eims_app_contractattachment` DISABLE KEYS */;
INSERT INTO `eims_app_contractattachment` VALUES (3,'contract_approvals/2026/03/桂林院子全过程补充协议书六关于服务期调整1.doc','contract','桂林院子全过程补充协议书(六)（关于服务期)调整(1).doc',20480,'2026-03-28 03:10:03.719750',0,5,NULL),(4,'contract_approvals/2026/04/工程信息管理系统-检查管理模块完整落地包2023-10-01.docx','contract','工程信息管理系统-检查管理模块完整落地包（2023-10-01）.docx',21036,'2026-04-05 05:48:00.730711',0,6,NULL),(5,'contract_approvals/2026/04/文件结构.png','contract','文件结构.png',35925,'2026-04-05 05:48:39.704097',1,6,2),(6,'contract_approvals/2026/04/260306九马画山徒步团建.jpg','contract','260306九马画山徒步团建.jpg',293435,'2026-04-05 05:54:23.370460',1,6,2);
/*!40000 ALTER TABLE `eims_app_contractattachment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_department`
--

DROP TABLE IF EXISTS `eims_app_department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_department` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `is_deleted` tinyint(1) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `department_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `department_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `department_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `manager_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact_phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact_email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `responsibilities` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `established_date` date DEFAULT NULL,
  `order` int NOT NULL,
  `manager_id` int DEFAULT NULL,
  `parent_department_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `department_code` (`department_code`),
  KEY `eims_app_de_departm_fa6d34_idx` (`department_code`),
  KEY `eims_app_de_status_8615d5_idx` (`status`),
  KEY `eims_app_department_manager_id_967c33d3_fk_auth_user_id` (`manager_id`),
  KEY `eims_app_department_parent_department_id_ddf11e26_fk_eims_app_` (`parent_department_id`),
  CONSTRAINT `eims_app_department_manager_id_967c33d3_fk_auth_user_id` FOREIGN KEY (`manager_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_department_parent_department_id_ddf11e26_fk_eims_app_` FOREIGN KEY (`parent_department_id`) REFERENCES `eims_app_department` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_department`
--

LOCK TABLES `eims_app_department` WRITE;
/*!40000 ALTER TABLE `eims_app_department` DISABLE KEYS */;
INSERT INTO `eims_app_department` VALUES (1,0,'2026-03-21 01:27:10.826381','2026-03-21 02:47:45.618522','DEPT001','监理部','functional','王敏志','','','负责公司工程项目的管理和实施','负责工程部相关工作','active',NULL,1,NULL,NULL),(2,0,'2026-03-21 01:27:10.833055','2026-03-21 02:49:01.959302','DEPT002','检测部','functional','宋弦弦','','','负责技术支持和研发工作','负责技术部相关工作','active',NULL,2,NULL,NULL),(3,0,'2026-03-21 01:27:10.836925','2026-03-21 02:49:58.420251','DEPT003','造价部','functional','黄建波','','','负责质量管理和监督','负责质量部相关工作','active',NULL,3,NULL,NULL),(4,0,'2026-03-21 01:27:10.841511','2026-03-21 02:50:39.865131','DEPT004','经营部','functional','唐薇薇','','','负责安全生产管理','负责安全部相关工作','active',NULL,4,NULL,NULL),(5,0,'2026-03-21 01:27:10.846310','2026-03-21 02:51:08.450670','DEPT005','财务部','functional','廖志红','','','负责物资采购和管理','负责物资部相关工作','active',NULL,5,NULL,NULL),(6,0,'2026-03-21 01:27:10.851590','2026-03-21 02:51:31.333891','DEPT006','总经办','functional','银雪','','','负责财务管理和会计核算','负责财务部相关工作','active',NULL,6,NULL,NULL),(7,1,'2026-03-21 01:27:10.856165','2026-03-21 01:27:10.856193','DEPT007','综合办','functional','吴九','','','负责行政和人力资源工作','负责综合办相关工作','active',NULL,7,NULL,NULL),(8,1,'2026-03-21 01:27:10.860890','2026-03-21 01:27:10.860907','DEPT008','市场部','functional','郑十','','','负责市场开拓和客户关系','负责市场部相关工作','active',NULL,8,NULL,NULL),(9,0,'2026-03-25 06:11:21.645002','2026-03-25 06:11:21.645016','DEPT009','前期部','functional','程慧慧','','','','','active',NULL,0,24,NULL);
/*!40000 ALTER TABLE `eims_app_department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_departmentmanager`
--

DROP TABLE IF EXISTS `eims_app_departmentmanager`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_departmentmanager` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `role` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `approval_level` int NOT NULL,
  `is_primary` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `department_id` bigint NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `eims_app_departmentmanag_department_id_user_id_ro_63cb5b85_uniq` (`department_id`,`user_id`,`role`),
  KEY `eims_app_departmentmanager_user_id_1631ee4d_fk_auth_user_id` (`user_id`),
  CONSTRAINT `eims_app_departmentm_department_id_cf98d503_fk_eims_app_` FOREIGN KEY (`department_id`) REFERENCES `eims_app_department` (`id`),
  CONSTRAINT `eims_app_departmentmanager_user_id_1631ee4d_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_departmentmanager`
--

LOCK TABLES `eims_app_departmentmanager` WRITE;
/*!40000 ALTER TABLE `eims_app_departmentmanager` DISABLE KEYS */;
/*!40000 ALTER TABLE `eims_app_departmentmanager` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_departmentrole`
--

DROP TABLE IF EXISTS `eims_app_departmentrole`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_departmentrole` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `is_deleted` tinyint(1) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `role_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_primary` tinyint(1) NOT NULL,
  `permissions` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `department_id` bigint NOT NULL,
  `user_id` int NOT NULL,
  `supervisor_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `eims_app_departmentrole_department_id_user_id_ro_1a811895_uniq` (`department_id`,`user_id`,`role_type`),
  KEY `eims_app_de_departm_9a6de7_idx` (`department_id`,`role_type`),
  KEY `eims_app_departmentrole_user_id_ccf0a499_fk_auth_user_id` (`user_id`),
  KEY `eims_app_departmentrole_supervisor_id_13570540_fk_auth_user_id` (`supervisor_id`),
  CONSTRAINT `eims_app_departmentr_department_id_8cf56ef8_fk_eims_app_` FOREIGN KEY (`department_id`) REFERENCES `eims_app_department` (`id`),
  CONSTRAINT `eims_app_departmentrole_supervisor_id_13570540_fk_auth_user_id` FOREIGN KEY (`supervisor_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_departmentrole_user_id_ccf0a499_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_departmentrole`
--

LOCK TABLES `eims_app_departmentrole` WRITE;
/*!40000 ALTER TABLE `eims_app_departmentrole` DISABLE KEYS */;
INSERT INTO `eims_app_departmentrole` VALUES (1,0,'2026-03-21 09:01:45.583448','2026-03-31 05:57:30.192516','manager','主任',0,'view,edit,submit',1,11,15),(2,0,'2026-03-25 05:47:50.732315','2026-03-31 05:57:09.338886','deputy','副主任',0,'',1,12,11),(3,0,'2026-03-25 05:51:44.729520','2026-03-25 05:51:44.729532','supervisor','总监',0,'',1,8,NULL),(4,0,'2026-03-25 05:52:22.966893','2026-03-31 05:46:02.164817','assistant','总监代表',0,'',1,3,12),(5,0,'2026-03-25 05:52:47.586655','2026-03-31 05:58:11.694683','member','监理员',0,'',1,9,11),(6,0,'2026-03-25 05:53:29.120952','2026-03-25 05:53:29.120966','manager','主任',0,'',2,20,NULL),(7,0,'2026-03-25 05:54:31.996961','2026-03-25 05:54:31.996973','manager','主任',0,'',4,18,NULL),(8,0,'2026-03-25 05:54:49.361659','2026-03-25 05:54:49.361673','manager','主任',0,'',6,16,NULL),(9,0,'2026-03-25 05:55:13.183461','2026-03-25 05:55:13.183474','manager','主任',0,'',4,19,NULL),(10,0,'2026-03-25 06:12:59.274105','2026-03-25 06:12:59.274121','manager','总经理',0,'',6,15,NULL),(11,0,'2026-03-31 03:05:19.042809','2026-03-31 03:05:19.042822','supervisor','总监',0,'',1,5,NULL),(12,0,'2026-03-31 03:06:29.293056','2026-03-31 03:06:29.293069','member','员工',0,'',1,6,NULL),(13,0,'2026-03-31 03:07:32.486126','2026-03-31 03:07:32.486138','supervisor','总监',0,'',1,14,NULL),(14,0,'2026-03-31 03:07:49.947737','2026-03-31 03:07:49.947751','manager','主任',0,'',5,23,NULL),(15,0,'2026-03-31 03:08:24.935776','2026-03-31 03:08:24.935799','member','员工',0,'',3,25,NULL),(16,0,'2026-03-31 03:08:38.096959','2026-03-31 03:08:38.096975','supervisor','总监',0,'',1,13,NULL),(17,0,'2026-03-31 03:09:00.595897','2026-03-31 03:09:00.595911','member','员工',0,'',1,4,NULL),(18,0,'2026-03-31 03:09:11.880877','2026-03-31 03:09:11.880891','supervisor','总监',0,'',1,7,NULL),(19,0,'2026-03-31 03:09:25.131501','2026-03-31 03:09:25.131516','member','员工',0,'',1,2,NULL),(20,0,'2026-03-31 03:09:41.947218','2026-03-31 03:09:41.947254','member','员工',0,'',2,21,NULL),(21,0,'2026-03-31 03:09:59.961736','2026-03-31 05:56:37.011849','deputy','副主任',0,'',9,24,11),(22,0,'2026-03-31 03:10:35.869668','2026-03-31 03:10:35.869684','manager','主任',0,'',3,22,NULL);
/*!40000 ALTER TABLE `eims_app_departmentrole` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_dynamicchoice`
--

DROP TABLE IF EXISTS `eims_app_dynamicchoice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_dynamicchoice` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `category` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `order` int NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `eims_app_dynamicchoice_category_code_02c4338a_uniq` (`category`,`code`),
  KEY `eims_app_dynamicchoice_created_by_id_9a8f2a51_fk_auth_user_id` (`created_by_id`),
  CONSTRAINT `eims_app_dynamicchoice_created_by_id_9a8f2a51_fk_auth_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_dynamicchoice`
--

LOCK TABLES `eims_app_dynamicchoice` WRITE;
/*!40000 ALTER TABLE `eims_app_dynamicchoice` DISABLE KEYS */;
/*!40000 ALTER TABLE `eims_app_dynamicchoice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_employee`
--

DROP TABLE IF EXISTS `eims_app_employee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_employee` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `employee_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `gender` smallint NOT NULL,
  `id_card` varchar(18) COLLATE utf8mb4_unicode_ci NOT NULL,
  `native_place` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ethnic` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `education` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `address` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `home_phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mobile` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `emergency_contact` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `emergency_phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `wechat` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `admin_position` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tech_position` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `professional_qualification` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `professional_title` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `job_qualification` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `entry_time` date DEFAULT NULL,
  `leave_time` date DEFAULT NULL,
  `operator` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `employee_code` (`employee_code`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_employee`
--

LOCK TABLES `eims_app_employee` WRITE;
/*!40000 ALTER TABLE `eims_app_employee` DISABLE KEYS */;
INSERT INTO `eims_app_employee` VALUES (1,'RY001','秦林',0,'','','han','bachelor','','','','','','','总经理','','','高工','',NULL,NULL,'','2026-03-28 15:40:56.770575','2026-03-28 15:48:16.164333',0,'',''),(2,'RY002','桂华',0,'','','han','bachelor','','','','','','','副总','','','','',NULL,NULL,'','2026-03-28 15:40:56.778024','2026-03-28 15:48:16.176775',0,'',''),(3,'RY003','王敏志',0,'','','han','bachelor','','','13800740000','','','','副总/主任','总监','注册监理工程师','高工','',NULL,NULL,'','2026-03-28 15:40:56.782286','2026-03-28 15:48:16.185643',0,'',''),(4,'RY004','林漓',0,'','','han','bachelor','','','','','','','副总','','','','',NULL,NULL,'','2026-03-28 15:40:56.786390','2026-03-28 15:48:16.194147',0,'',''),(5,'RY005','方永明',0,'','','han','bachelor','','','','','','','主任','','','','',NULL,NULL,'','2026-03-28 15:40:56.790279','2026-03-28 15:48:16.203399',0,'',''),(6,'RY006','唐薇薇',0,'','','han','bachelor','','','','','','','主任','','','','',NULL,NULL,'','2026-03-28 15:40:56.794565','2026-03-28 15:48:16.211722',0,'',''),(7,'RY007','宋弦弦',0,'','','han','bachelor','','','','','','','','','','','',NULL,NULL,'','2026-03-28 15:40:56.799221','2026-03-28 15:48:16.222582',0,'',''),(8,'RY008','黄建波',0,'','','han','bachelor','','','','','','','','','','','',NULL,NULL,'','2026-03-28 15:40:56.803045','2026-03-28 15:48:16.231546',0,'',''),(9,'RY009','廖志红',0,'','','han','bachelor','','','','','','','','','','','',NULL,NULL,'','2026-03-28 15:40:56.807343','2026-03-28 15:48:16.240263',0,'',''),(10,'RY010','银雪',0,'','','han','bachelor','','','','','','','','','','','',NULL,NULL,'','2026-03-28 15:40:56.811208','2026-03-28 15:48:16.248687',0,'',''),(11,'RY011','黎绍昆',0,'','','han','bachelor','','','13800740001','','','','副主任','总监','注册监理工程师、一级建造师','高工','',NULL,NULL,'','2026-03-28 15:40:56.814997','2026-03-28 15:48:16.258198',0,'',''),(12,'RY012','程慧慧',0,'','','han','bachelor','','','','','','','','','','','',NULL,NULL,'','2026-03-28 15:40:56.818920','2026-03-28 15:48:16.266825',0,'',''),(13,'RY013','庞黎明',0,'','','han','bachelor','','','','','','','','','','','',NULL,NULL,'','2026-03-28 15:40:56.822735','2026-03-28 15:48:16.275455',0,'',''),(14,'RY014','龙欢',0,'','','han','bachelor','','','','','','','','','','','',NULL,NULL,'','2026-03-28 15:40:56.826426','2026-03-28 15:48:16.283898',0,'',''),(15,'RY015','周林松',0,'','','han','bachelor','','','','','','','','','','','',NULL,NULL,'','2026-03-28 15:40:56.830700','2026-03-28 15:48:16.293685',0,'',''),(16,'RY016','甘丽春',0,'','','han','bachelor','','','','','','','','','','','',NULL,NULL,'','2026-03-28 15:40:56.834833','2026-03-28 15:48:16.302705',0,'',''),(17,'RY017','柏翔',0,'','','han','bachelor','','','13800740002','','','','','总监','','','',NULL,NULL,'','2026-03-28 15:40:56.838794','2026-03-28 15:48:16.311926',0,'',''),(18,'RY018','吉定斌',0,'','','han','bachelor','','','13800740003','','','','','总代','','','',NULL,NULL,'','2026-03-28 15:40:56.843396','2026-03-28 15:48:16.320524',0,'',''),(19,'RY019','李闰',0,'','','han','bachelor','','','13800740004','','','','','监理员','','','',NULL,NULL,'','2026-03-28 15:40:56.847380','2026-03-28 15:48:16.330804',0,'',''),(20,'RY020','廖成刚',0,'','','han','bachelor','','','13800740005','','','','','监理员','','','',NULL,NULL,'','2026-03-28 15:40:56.851230','2026-03-28 15:48:16.339688',0,'',''),(21,'RY021','龙庆香',1,'','','han','bachelor','','','13800740006','','','','','资料员','注册监理工程师','工程师','',NULL,NULL,'','2026-03-28 15:40:56.855594','2026-03-28 15:48:16.348060',0,'',''),(22,'RY022','罗龙辉',0,'','','han','bachelor','','','13800740007','','','','','总代','','','',NULL,NULL,'','2026-03-28 15:40:56.859327','2026-03-28 15:48:16.356252',0,'',''),(23,'RY023','秦方玉',0,'','','han','bachelor','','','13800740008','','','','','专监','','','',NULL,NULL,'','2026-03-28 15:40:56.863160','2026-03-28 15:48:16.364199',0,'',''),(24,'RY024','秦养付',0,'','','han','bachelor','','','13800740009','','','','','总监','注册监理工程师、注册造价师','高工','',NULL,NULL,'','2026-03-28 15:40:56.867811','2026-03-28 15:48:16.372594',0,'',''),(25,'RY025','谭军',0,'','','han','bachelor','','','13800740010','','','','','专监','','','',NULL,NULL,'','2026-03-28 15:40:56.872094','2026-03-28 15:48:16.380739',0,'',''),(26,'RY026','唐昌成',0,'','','han','bachelor','','','13800740011','','','','','总监','注册监理工程师','高工','',NULL,NULL,'','2026-03-28 15:40:56.875939','2026-03-28 15:48:16.388634',0,'',''),(27,'RY027','唐昌罗',0,'','','han','bachelor','','','13800740012','','','','','总代','','','',NULL,NULL,'','2026-03-28 15:40:56.879970','2026-03-28 15:48:16.396428',0,'',''),(28,'RY028','唐满东',0,'','','han','bachelor','','','13800740013','','','','','总监','注册监理工程师、一级建造师','高工','',NULL,NULL,'','2026-03-28 15:40:56.883853','2026-03-28 15:48:16.403994',0,'',''),(29,'RY029','唐鹏',0,'','','han','bachelor','','','13800740014','','','','','监理员','','','',NULL,NULL,'','2026-03-28 15:40:56.887741','2026-03-28 15:48:16.412154',0,'',''),(30,'RY030','汪勇',0,'','','han','bachelor','','','13800740015','','','','','总代','','','',NULL,NULL,'','2026-03-28 15:40:56.892127','2026-03-28 15:48:16.420069',0,'',''),(31,'RY031','王立明',0,'','','han','bachelor','','','13800740016','','','','','总监','注册监理工程师','','',NULL,NULL,'','2026-03-28 15:40:56.896226','2026-03-28 15:48:16.427779',0,'',''),(32,'RY032','王璐',0,'','','han','bachelor','','','13800740017','','','','','总代','','','',NULL,NULL,'','2026-03-28 15:40:56.899846','2026-03-28 15:48:16.435721',0,'',''),(33,'RY033','吴向南',0,'','','han','bachelor','','','13800740018','','','','','总代','','','',NULL,NULL,'','2026-03-28 15:40:56.903993','2026-03-28 15:48:16.444386',0,'',''),(34,'RY034','谢荣明',0,'','','han','bachelor','','','13800740019','','','','','专监','','','',NULL,NULL,'','2026-03-28 15:40:56.907833','2026-03-28 15:48:16.452602',0,'',''),(35,'RY035','阳著平',0,'','','han','bachelor','','','13800740020','','','','','监理员','','','',NULL,NULL,'','2026-03-28 15:40:56.913722','2026-03-28 15:48:16.460586',0,'',''),(36,'RY036','易强',0,'','','han','bachelor','','','13800740021','','','','','总监','注册监理工程师','','',NULL,NULL,'','2026-03-28 15:40:56.918050','2026-03-28 15:48:16.468452',0,'',''),(37,'RY037','张中立',0,'','','han','bachelor','','','13800740022','','','','','专监','','','',NULL,NULL,'','2026-03-28 15:40:56.922095','2026-03-28 15:48:16.479784',0,'','');
/*!40000 ALTER TABLE `eims_app_employee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_fileaccesspermission`
--

DROP TABLE IF EXISTS `eims_app_fileaccesspermission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_fileaccesspermission` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `permission_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `can_preview_office` tinyint(1) NOT NULL,
  `can_batch_upload` tinyint(1) NOT NULL,
  `can_manage_versions` tinyint(1) NOT NULL,
  `apply_to_notices` tinyint(1) NOT NULL,
  `apply_to_file_manage` tinyint(1) NOT NULL,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `eims_app_fileaccesspermission_user_id_73372a8c_uniq` (`user_id`),
  CONSTRAINT `eims_app_fileaccesspermission_user_id_73372a8c_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_fileaccesspermission`
--

LOCK TABLES `eims_app_fileaccesspermission` WRITE;
/*!40000 ALTER TABLE `eims_app_fileaccesspermission` DISABLE KEYS */;
/*!40000 ALTER TABLE `eims_app_fileaccesspermission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_filemanage`
--

DROP TABLE IF EXISTS `eims_app_filemanage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_filemanage` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_path` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `uploader` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `file_size` bigint NOT NULL,
  `file_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `content_summary` longtext COLLATE utf8mb4_unicode_ci,
  `file_category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `file_number` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  `publish_time` datetime(6) DEFAULT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci,
  `update_time` datetime(6) DEFAULT NULL,
  `file_format` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_filemanage`
--

LOCK TABLES `eims_app_filemanage` WRITE;
/*!40000 ALTER TABLE `eims_app_filemanage` DISABLE KEYS */;
INSERT INTO `eims_app_filemanage` VALUES (1,'GB50974-2014消防给水与消火栓系统技术规范','file_manage/20260331/GB50974-2014消防给水与消火栓系统技术规范_jvv2RSu.doc','admin',8261833,'.doc','消防给水与消火栓系统技术规范','技术规范','GB50974-2014',0,'2026-03-21 07:22:40.703996','','2026-03-31 02:52:40.309719','DOC'),(2,'GB50016-2014建筑设计防火规范(2018年版)','file_manage/20260331/GB50016-2014建筑设计防火规范2018年版_WTvaN6S.doc','admin',1801137,'.doc','','技术规范','GB50016-2014',0,'2026-03-21 07:23:28.200381','','2026-03-31 02:51:39.191413','DOC'),(3,'《危险性较大的分部分项工程安全管理规定》住建部37号令','file_manage/20260331/危险性较大的分部分项工程安全管理规定住建部37号令.docx','黎绍昆',22239,'.docx','住建部 号令 危大工程 管理规定','部门规章','住建部37号令',0,'2026-03-31 02:50:39.800871','','2026-03-31 02:50:39.800899','DOCX');
/*!40000 ALTER TABLE `eims_app_filemanage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_filemanageversion`
--

DROP TABLE IF EXISTS `eims_app_filemanageversion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_filemanageversion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_size` bigint NOT NULL,
  `file_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `version` int NOT NULL,
  `is_latest` tinyint(1) NOT NULL,
  `uploader` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `upload_time` datetime(6) NOT NULL,
  `change_log` longtext COLLATE utf8mb4_unicode_ci,
  `is_deleted` tinyint(1) NOT NULL,
  `file_manage_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_fi_file_ma_f7111a_idx` (`file_manage_id`,`version` DESC),
  KEY `eims_app_fi_file_ma_3098a0_idx` (`file_manage_id`,`is_latest`),
  CONSTRAINT `eims_app_filemanagev_file_manage_id_d4e737ca_fk_eims_app_` FOREIGN KEY (`file_manage_id`) REFERENCES `eims_app_filemanage` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_filemanageversion`
--

LOCK TABLES `eims_app_filemanageversion` WRITE;
/*!40000 ALTER TABLE `eims_app_filemanageversion` DISABLE KEYS */;
/*!40000 ALTER TABLE `eims_app_filemanageversion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_monthlyreport`
--

DROP TABLE IF EXISTS `eims_app_monthlyreport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_monthlyreport` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `project_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `report_year` int NOT NULL,
  `report_month` varchar(7) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_progress` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `current_status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `monthly_output_value` decimal(15,2) NOT NULL,
  `monthly_payment` decimal(15,2) NOT NULL,
  `payment_description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `personnel_changes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_personnel` int NOT NULL,
  `should_submit_date` date DEFAULT NULL,
  `actual_submit_date` date DEFAULT NULL,
  `submit_time` datetime(6) DEFAULT NULL,
  `approve_time` datetime(6) DEFAULT NULL,
  `reject_reason` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `approver_id` int DEFAULT NULL,
  `reporter_id` int NOT NULL,
  `project_id` bigint NOT NULL,
  `current_cumulative_output` decimal(15,2) NOT NULL,
  `current_cumulative_payment` decimal(15,2) NOT NULL,
  `current_payment_request` decimal(15,2) NOT NULL,
  `last_month_cumulative_output` decimal(15,2) NOT NULL,
  `last_month_cumulative_payment` decimal(15,2) NOT NULL,
  `next_month_assistance` longtext COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT (_utf8mb4''),
  `next_month_plan_amount` decimal(15,2) NOT NULL,
  `next_month_plan_detail` longtext COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT (_utf8mb4''),
  `payment_issues` longtext COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT (_utf8mb4''),
  `payment_progress` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `eims_app_monthlyreport_project_id_report_year_r_4c31d625_uniq` (`project_id`,`report_year`,`report_month`),
  KEY `eims_app_monthlyreport_approver_id_f230288e_fk_auth_user_id` (`approver_id`),
  KEY `eims_app_monthlyreport_reporter_id_95f89416_fk_auth_user_id` (`reporter_id`),
  KEY `eims_app_monthlyreport_project_code_fc9eea9d` (`project_code`),
  KEY `eims_app_mo_report__71dc42_idx` (`report_year`,`report_month`),
  KEY `eims_app_mo_status_0a8abe_idx` (`status`),
  CONSTRAINT `eims_app_monthlyrepo_project_id_ba9548fc_fk_eims_app_` FOREIGN KEY (`project_id`) REFERENCES `eims_app_projectdetail` (`id`),
  CONSTRAINT `eims_app_monthlyreport_approver_id_f230288e_fk_auth_user_id` FOREIGN KEY (`approver_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_monthlyreport_reporter_id_95f89416_fk_auth_user_id` FOREIGN KEY (`reporter_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_monthlyreport`
--

LOCK TABLES `eims_app_monthlyreport` WRITE;
/*!40000 ALTER TABLE `eims_app_monthlyreport` DISABLE KEYS */;
INSERT INTO `eims_app_monthlyreport` VALUES (2,'2063',2026,'2026-03','submitted','项目正常推进中','normal_construction',100.00,80.00,'','',0,'2026-03-25','2026-03-20',NULL,NULL,'','2026-03-28 06:55:58.167264','2026-03-28 06:55:58.167278',NULL,1,66,500.00,400.00,0.00,0.00,0.00,'',0.00,'','','');
/*!40000 ALTER TABLE `eims_app_monthlyreport` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_notice`
--

DROP TABLE IF EXISTS `eims_app_notice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_notice` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `notice_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notice_title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notice_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notice_scope` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notice_content` longtext COLLATE utf8mb4_unicode_ci,
  `attach_file` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `publish_person` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `effective_date` date DEFAULT NULL,
  `invalid_date` date DEFAULT NULL,
  `notice_status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `read_count` int DEFAULT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci,
  `update_time` datetime(6) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `file_size` bigint DEFAULT NULL,
  `file_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `keywords` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `create_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_notice`
--

LOCK TABLES `eims_app_notice` WRITE;
/*!40000 ALTER TABLE `eims_app_notice` DISABLE KEYS */;
INSERT INTO `eims_app_notice` VALUES (1,NULL,'2026年元旦放假通知','通知',NULL,'','','admin',NULL,NULL,'已发布',0,'','2026-03-30 19:08:12.242314',0,NULL,0,NULL,'元旦 放假 通知','2026-03-30 05:05:15.065435'),(2,NULL,'2026春节放假通知','通知',NULL,'','','admin',NULL,NULL,NULL,0,'','2026-03-30 19:17:37.107839',0,NULL,0,NULL,'春节 放假 通知','2026-03-30 19:16:36.667953'),(3,NULL,'260306九马画山徒步团建',NULL,NULL,'','','admin',NULL,NULL,NULL,0,'','2026-03-30 19:19:36.143197',0,NULL,0,NULL,'徒步 团建 通知','2026-03-30 19:19:20.890880'),(4,NULL,'260305经营人员内部招聘','公告',NULL,'','','admin',NULL,NULL,NULL,0,'','2026-03-30 19:29:29.409532',1,NULL,0,NULL,'经营 人员 招聘','2026-03-30 19:22:27.443402'),(5,NULL,'260305经营人员内部招聘',NULL,NULL,'','','admin',NULL,NULL,NULL,0,'','2026-03-30 19:45:28.263369',1,NULL,0,NULL,NULL,'2026-03-30 19:29:52.205291'),(6,NULL,'260305经营人员内部招聘',NULL,NULL,'','','admin',NULL,NULL,NULL,0,'','2026-03-30 19:31:48.530795',1,NULL,0,NULL,NULL,'2026-03-30 19:31:42.010325'),(7,NULL,'260305经营人员内部招聘',NULL,NULL,'','notices/260305经营人员内部招聘_bBU0O3x.jpg','admin',NULL,NULL,NULL,0,'','2026-03-30 20:38:20.902300',1,'260305经营人员内部招聘_bBU0O3x.jpg',165577,'.jpg','经营 人员 招聘','2026-03-30 19:46:38.666706'),(8,NULL,'260305经营人员内部招聘',NULL,NULL,'','','admin',NULL,NULL,NULL,0,'','2026-03-30 20:39:31.672370',0,NULL,0,NULL,'经营 人员 招聘','2026-03-30 20:38:58.546629'),(9,NULL,'260305经营人员内部招聘',NULL,NULL,'','','admin',NULL,NULL,NULL,0,'','2026-03-30 22:28:06.355073',1,NULL,0,NULL,NULL,'2026-03-30 20:47:10.445000'),(10,NULL,'260305经营人员内部招聘',NULL,NULL,'','','admin',NULL,NULL,NULL,0,'','2026-03-30 22:28:01.308832',1,NULL,0,NULL,'经营 人员 招聘','2026-03-30 20:53:07.250400'),(11,NULL,'260305经营人员内部招聘',NULL,NULL,'','','admin',NULL,NULL,NULL,0,'','2026-03-30 22:27:57.754813',1,NULL,0,NULL,'经营 人员 招聘','2026-03-30 22:18:49.410892'),(12,NULL,'260305经营人员内部招聘',NULL,NULL,'','','admin',NULL,NULL,NULL,0,'','2026-03-30 23:36:27.150124',0,NULL,0,NULL,'经营 人员 招聘','2026-03-30 23:36:27.150075'),(13,NULL,'2026年元旦放假通知',NULL,NULL,'','','admin',NULL,NULL,NULL,0,'','2026-04-01 06:54:37.961056',1,NULL,0,NULL,NULL,'2026-03-31 01:45:43.997971');
/*!40000 ALTER TABLE `eims_app_notice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_noticeattachment`
--

DROP TABLE IF EXISTS `eims_app_noticeattachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_noticeattachment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_size` bigint NOT NULL,
  `file_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `version` int NOT NULL,
  `is_latest` tinyint(1) NOT NULL,
  `upload_person` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `upload_time` datetime(6) NOT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci,
  `is_deleted` tinyint(1) NOT NULL,
  `notice_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_no_notice__6d5dde_idx` (`notice_id`,`version` DESC),
  KEY `eims_app_no_notice__492aac_idx` (`notice_id`,`is_latest`),
  CONSTRAINT `eims_app_noticeattac_notice_id_7c7b2188_fk_eims_app_` FOREIGN KEY (`notice_id`) REFERENCES `eims_app_notice` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_noticeattachment`
--

LOCK TABLES `eims_app_noticeattachment` WRITE;
/*!40000 ALTER TABLE `eims_app_noticeattachment` DISABLE KEYS */;
INSERT INTO `eims_app_noticeattachment` VALUES (3,'notices/attachments/元旦放假通知_tkPWEnj.jpg','元旦放假通知_tkPWEnj.jpg',220605,'.jpg',1,1,'admin','2026-03-30 18:51:49.986555','',0,1),(4,'notices/attachments/260209春节放假通知.jpg','260209春节放假通知.jpg',213403,'.jpg',1,1,'admin','2026-03-30 19:17:49.129046','',0,2),(5,'notices/attachments/260306九马画山徒步团建.jpg','260306九马画山徒步团建.jpg',293435,'.jpg',1,1,'admin','2026-03-30 19:20:34.074781','',0,3),(6,'notices/attachments/260305经营人员内部招聘.jpg','260305经营人员内部招聘.jpg',165577,'.jpg',1,1,'admin','2026-03-30 19:23:33.773610','',0,4),(7,'notices/attachments/260305经营人员内部招聘_fWD8kW5.jpg','260305经营人员内部招聘_fWD8kW5.jpg',165577,'.jpg',1,1,'admin','2026-03-30 19:37:48.405501','',0,5),(8,'notices/attachments/260305经营人员内部招聘_1PGZTyC.jpg','260305经营人员内部招聘_1PGZTyC.jpg',165577,'.jpg',1,1,'admin','2026-03-30 20:25:16.930175','',0,7),(9,'notices/attachments/260305经营人员内部招聘_krxZ7Ce.jpg','260305经营人员内部招聘_krxZ7Ce.jpg',165577,'.jpg',1,1,'admin','2026-03-30 20:39:44.625778','',0,8),(10,'notices/attachments/260305经营人员内部招聘_YXE0xBy.jpg','260305经营人员内部招聘_YXE0xBy.jpg',165577,'.jpg',1,1,'admin','2026-03-30 20:47:28.397924','',0,9),(11,'notices/attachments/260305经营人员内部招聘_hGY7TKg.jpg','260305经营人员内部招聘_hGY7TKg.jpg',165577,'.jpg',1,1,'admin','2026-03-30 20:53:35.510187','',0,10),(12,'notices/attachments/260209春节放假通知_MjSo9K4.jpg','260209春节放假通知_MjSo9K4.jpg',213403,'.jpg',1,1,'admin','2026-03-30 22:27:23.127736','',0,11),(13,'notices/attachments/251230元旦放假通知.jpg','251230元旦放假通知.jpg',220605,'.jpg',1,1,'admin','2026-03-31 01:48:22.981582','',0,13),(14,'notices/attachments/BC笔记.docx','BC笔记.docx',27481,'.docx',1,1,'admin','2026-03-31 01:48:59.931295','',0,13);
/*!40000 ALTER TABLE `eims_app_noticeattachment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_outputpayment`
--

DROP TABLE IF EXISTS `eims_app_outputpayment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_outputpayment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `project_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `month` varchar(7) COLLATE utf8mb4_unicode_ci NOT NULL,
  `monthly_output` decimal(10,2) NOT NULL,
  `cumulative_output` decimal(10,2) NOT NULL,
  `contract_total` decimal(15,2) NOT NULL,
  `cumulative_received` decimal(15,2) NOT NULL,
  `contract_receivable` decimal(15,2) NOT NULL,
  `near_term_receivable` decimal(15,2) NOT NULL,
  `payment_basis` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_payment_situation` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `recent_payment_request` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `actual_payment` decimal(15,2) NOT NULL,
  `next_month_request` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `next_month_plan` decimal(15,2) NOT NULL,
  `payment_measures` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `need_assistance` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `payment_date` date DEFAULT NULL,
  `payment_method` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `output_amount` decimal(10,2) NOT NULL,
  `payment_amount` decimal(15,2) NOT NULL,
  `operator` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `project_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_outputpayment_project_code_86d8241a` (`project_code`),
  KEY `eims_app_outputpayment_project_id_7cd92153` (`project_id`),
  KEY `eims_app_ou_project_54df90_idx` (`project_code`,`month`),
  KEY `eims_app_ou_project_997523_idx` (`project_id`,`month`),
  CONSTRAINT `eims_app_outputpayme_project_id_7cd92153_fk_eims_app_` FOREIGN KEY (`project_id`) REFERENCES `eims_app_projectdetail` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_outputpayment`
--

LOCK TABLES `eims_app_outputpayment` WRITE;
/*!40000 ALTER TABLE `eims_app_outputpayment` DISABLE KEYS */;
INSERT INTO `eims_app_outputpayment` VALUES (1,'2068','2026-03',2.00,2.00,88000.00,4.00,88000.00,87996.00,'','','',2.00,'',0.00,'','','',NULL,'',0.00,0.00,'admin','2026-03-27 22:05:59.872929','2026-03-27 22:05:59.872942',92),(2,'2067','2026-03',1.00,2.00,0.00,2.00,0.00,-2.00,'','','1',1.00,'',0.00,'','','',NULL,'',0.00,0.00,'黎绍昆','2026-03-28 01:52:32.314155','2026-03-28 01:52:32.314167',91),(3,'2063','2026-03',50000.00,450000.00,508819.91,330019.34,508819.91,178800.57,'','','',0.00,'20000',0.00,'','','',NULL,'',0.00,0.00,'黎绍昆','2026-03-28 05:31:44.437726','2026-03-28 05:31:44.437748',66),(4,'HT20260405140722','2026-04',10000.00,80000.00,55.00,350000.00,55.00,-349945.00,'','','',70000.00,'',0.00,'','','',NULL,'',0.00,0.00,'王璐','2026-04-07 03:04:05.721695','2026-04-07 06:00:14.353277',96),(5,'HT20260405232807','2026-04',5000.00,15000.00,155900.00,0.00,155900.00,155900.00,'','','',0.00,'',0.00,'','','',NULL,'',0.00,0.00,'黎绍昆','2026-04-07 05:06:55.969862','2026-04-07 05:06:55.969880',97),(6,'HT20260405232807','2026-03',5000.00,20000.00,155900.00,0.00,155900.00,155900.00,'','','',0.00,'',0.00,'','','',NULL,'',0.00,0.00,'黎绍昆','2026-04-07 05:07:11.564515','2026-04-07 05:08:09.591524',97),(7,'HT20260405232807','2026-05',5000.00,20000.00,155900.00,0.00,155900.00,155900.00,'','','',0.00,'',0.00,'','','',NULL,'',0.00,0.00,'黎绍昆','2026-04-07 05:08:30.823135','2026-04-07 05:08:30.823156',97),(8,'2019','2026-04',0.00,0.00,3348700.00,2800000.00,3348700.00,548700.00,'','','',0.00,'',0.00,'','','',NULL,'',0.00,0.00,'黎绍昆','2026-04-07 05:27:07.423268','2026-04-07 05:27:07.423287',77),(9,'HT20260405140722','2026-05',6660.00,86660.00,55.00,360000.00,55.00,-359945.00,'','','',10000.00,'',0.00,'','','',NULL,'',0.00,0.00,'王璐','2026-04-07 06:45:08.667133','2026-04-07 06:45:08.667148',96),(10,'HT20260405140722','2026-04',0.00,86660.00,55.00,360000.00,55.00,-359945.00,'','','',0.00,'',0.00,'','','',NULL,'',0.00,0.00,'秦养付','2026-04-07 14:42:38.248350','2026-04-07 14:42:38.248372',96),(11,'HT20260405140722','2026-04',0.00,86660.00,55.00,360000.00,55.00,-359945.00,'','','',0.00,'',0.00,'','','',NULL,'',0.00,0.00,'秦养付','2026-04-07 14:43:09.054011','2026-04-07 14:43:09.054024',96),(12,'HT20260405140722','2026-04',0.00,86660.00,55.00,360000.00,55.00,-359945.00,'','','',0.00,'',0.00,'','','',NULL,'',0.00,0.00,'秦养付','2026-04-07 15:11:56.753856','2026-04-07 15:11:56.753867',96),(13,'HT20260405140722','2026-04',0.00,86660.00,55.00,360000.00,55.00,-359945.00,'','','',0.00,'',0.00,'','','',NULL,'',0.00,0.00,'秦养付','2026-04-07 15:12:18.534712','2026-04-07 15:12:18.534724',96);
/*!40000 ALTER TABLE `eims_app_outputpayment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_personnel`
--

DROP TABLE IF EXISTS `eims_app_personnel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_personnel` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `personnel_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `gender` smallint NOT NULL,
  `position` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `department` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `entry_time` date DEFAULT NULL,
  `leave_time` date DEFAULT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `operator` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci,
  `project_id` bigint DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  `employee_id` bigint DEFAULT NULL,
  `project2_id` bigint DEFAULT NULL,
  `project3_id` bigint DEFAULT NULL,
  `project4_id` bigint DEFAULT NULL,
  `project5_id` bigint DEFAULT NULL,
  `project_code2` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_code3` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_code4` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_code5` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_personnel_project_code_5a80d8da` (`project_code`),
  KEY `eims_app_personnel_personnel_code_cc509285` (`personnel_code`),
  KEY `eims_app_personnel_employee_id_5cd3c134_fk_eims_app_employee_id` (`employee_id`),
  KEY `eims_app_personnel_project_id_220cebcf_fk_eims_app_` (`project_id`),
  KEY `eims_app_personnel_project2_id_28782f04_fk_eims_app_` (`project2_id`),
  KEY `eims_app_personnel_project3_id_455822e9_fk_eims_app_` (`project3_id`),
  KEY `eims_app_personnel_project4_id_7eb37b5e_fk_eims_app_` (`project4_id`),
  KEY `eims_app_personnel_project5_id_3f1dd0f9_fk_eims_app_` (`project5_id`),
  KEY `eims_app_personnel_department_3b36066b` (`department`),
  KEY `eims_app_personnel_project_code2_81ec7447` (`project_code2`),
  KEY `eims_app_personnel_project_code3_860f53f1` (`project_code3`),
  KEY `eims_app_personnel_project_code4_8f99e991` (`project_code4`),
  KEY `eims_app_personnel_project_code5_e6b26555` (`project_code5`),
  CONSTRAINT `eims_app_personnel_employee_id_5cd3c134_fk_eims_app_employee_id` FOREIGN KEY (`employee_id`) REFERENCES `eims_app_employee` (`id`),
  CONSTRAINT `eims_app_personnel_project2_id_28782f04_fk_eims_app_` FOREIGN KEY (`project2_id`) REFERENCES `eims_app_projectdetail` (`id`),
  CONSTRAINT `eims_app_personnel_project3_id_455822e9_fk_eims_app_` FOREIGN KEY (`project3_id`) REFERENCES `eims_app_projectdetail` (`id`),
  CONSTRAINT `eims_app_personnel_project4_id_7eb37b5e_fk_eims_app_` FOREIGN KEY (`project4_id`) REFERENCES `eims_app_projectdetail` (`id`),
  CONSTRAINT `eims_app_personnel_project5_id_3f1dd0f9_fk_eims_app_` FOREIGN KEY (`project5_id`) REFERENCES `eims_app_projectdetail` (`id`),
  CONSTRAINT `eims_app_personnel_project_id_220cebcf_fk_eims_app_` FOREIGN KEY (`project_id`) REFERENCES `eims_app_projectdetail` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_personnel`
--

LOCK TABLES `eims_app_personnel` WRITE;
/*!40000 ALTER TABLE `eims_app_personnel` DISABLE KEYS */;
INSERT INTO `eims_app_personnel` VALUES (1,'1001','','吉定斌',0,'总代','13800740003','监理部','2016-01-20',NULL,'-','','2026-03-20 18:32:05.406224','2026-03-22 06:47:49.092883','None',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(2,'1002','','李闰',0,'总代','13800740004','监理部','2016-01-20',NULL,'-','','2026-03-20 18:32:05.423757','2026-03-22 06:47:49.100124','None',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(3,'1003','','龙庆香',0,'资料员','13800740006','监理部','2016-01-20',NULL,'-','','2026-03-20 18:32:05.438172','2026-03-22 06:47:49.104623','None',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(4,'1008','','王立明',0,'总代','13800740016','监理部','2016-01-20',NULL,'-','','2026-03-20 18:32:05.445237','2026-03-22 06:47:49.127423','鼎策',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(5,'1010','','A',0,'专监','','',NULL,NULL,'','','2026-03-20 18:32:05.451922','2026-03-22 06:47:49.135868','',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(6,'1011','','B',0,'专监','','',NULL,NULL,'','','2026-03-20 18:32:05.467560','2026-03-22 06:47:49.140173','',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(7,'1013','','D',0,'专监','','',NULL,NULL,'','','2026-03-20 18:32:05.486071','2026-03-22 06:47:49.147835','',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(8,'1015','','F',0,'专监','','',NULL,NULL,'','','2026-03-20 18:32:05.502077','2026-03-22 06:47:49.156685','',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(9,'1017','','H',0,'专监','','',NULL,NULL,'','','2026-03-20 18:32:05.517713','2026-03-22 06:47:49.164639','',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(10,'1018','','I',0,'专监','','',NULL,NULL,'','','2026-03-20 18:32:05.524560','2026-03-22 06:47:49.169271','',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(11,'1020','','K',0,'专监','','',NULL,NULL,'','','2026-03-20 18:32:05.531792','2026-03-22 06:47:49.177351','',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(12,'1021','','L',0,'专监','','',NULL,NULL,'','','2026-03-20 18:32:05.539456','2026-03-22 06:47:49.181589','',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(13,'1022','','M',0,'专监','','',NULL,NULL,'','','2026-03-20 18:32:05.554756','2026-03-22 06:47:49.185054','',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(14,'1023','','N',0,'专监','','',NULL,NULL,'','','2026-03-20 18:32:05.576307','2026-03-22 06:47:49.189169','',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(15,'1024','','O',0,'专监','','',NULL,NULL,'','','2026-03-20 18:32:05.593010','2026-03-22 06:47:49.193566','',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(16,'1025','','汪勇',0,'总代','13800740015','监理部','2016-01-20',NULL,'','','2026-03-20 18:32:05.600895','2026-03-22 01:19:44.876119','None',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(17,'1027','','王立明',0,'总代','13800740016','监理部','2016-01-20',NULL,'','','2026-03-20 18:32:05.608442','2026-03-22 01:19:44.875936','鼎策',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(18,'1028','','王璐',0,'None','13800740017','监理部','2016-01-20',NULL,'','','2026-03-20 18:32:05.622653','2026-03-22 01:19:44.875742','None',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(19,'1030','','吴向南',0,'总代','13800740018','监理部','2016-01-20',NULL,'','','2026-03-20 18:32:05.629741','2026-03-22 01:19:44.875479','鼎策',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(20,'1031','','谢荣明',0,'None','13800740019','监理部','2016-01-20',NULL,'','','2026-03-20 18:32:05.637536','2026-03-22 01:19:44.874642','None',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(21,'1033','','阳著平',0,'专监','13800740020','监理部','2016-01-20',NULL,'','','2026-03-20 18:32:05.645345','2026-03-22 01:19:55.154029','None',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(22,'1034','','易强',0,'总代','13800740021','监理部','2016-01-20',NULL,'','','2026-03-20 18:32:05.652516','2026-03-22 01:19:55.153530','鼎策',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(23,'1038','','张中立',0,'None','13800740022','监理部','2016-01-20',NULL,'','','2026-03-20 18:32:05.659587','2026-03-22 01:19:55.150010','None',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(24,'PER001','','张三',0,'项目经理','13800138001','监理部','2026-01-01',NULL,'zhangsan@example.com','test_user','2026-03-20 18:39:59.901339','2026-03-22 01:14:19.569956','测试人员',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(25,'PER002','','李四',1,'技术负责人','13800138002','监理部','2026-01-05',NULL,'lisi@example.com','test_user','2026-03-20 18:39:59.904920','2026-03-22 01:14:19.569609','None',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(26,'PER003','','王五',0,'监理员','13800138003','监理部',NULL,NULL,'wangwu@example.com','','2026-03-20 22:05:13.744353','2026-03-22 01:14:19.565649','',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(27,'1004','','罗龙辉',0,'总代','13800740007','监理部','2016-01-20',NULL,'-','','2026-03-22 01:20:29.120482','2026-03-28 15:30:52.367824','鼎策',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(28,'1005','2004','秦养付',0,'总监','13800740009','监理部','2016-01-20',NULL,'-','','2026-03-22 01:20:29.124852','2026-03-28 15:30:52.367527','None',58,1,NULL,30,NULL,NULL,NULL,'2003','','',''),(29,'1006','','唐昌罗',0,'总代','13800740012','监理部','2016-01-20',NULL,'-','','2026-03-22 01:20:29.129024','2026-03-28 15:30:52.367308','None',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(30,'1007','2002','唐鹏',0,'监理员','13800740014','监理部','2016-01-20',NULL,'-','','2026-03-22 01:20:29.133882','2026-03-28 15:30:52.367060','None',71,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(31,'1009','','谢荣明',0,'专监','13800740019','监理部','2016-01-20',NULL,'-','','2026-03-22 01:20:29.143291','2026-03-28 15:30:52.366742','None',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(33,'1014','','E',0,'专监','','',NULL,NULL,'','','2026-03-22 01:20:29.166489','2026-03-28 13:56:21.479139','',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(34,'1016','','G',0,'专监','','',NULL,NULL,'','','2026-03-22 01:20:29.175249','2026-03-28 13:56:21.478626','',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(35,'1019','','J',0,'专监','','',NULL,NULL,'','','2026-03-22 01:20:29.190173','2026-03-28 13:56:21.477895','',NULL,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(36,'RY2068_001','2068','4',0,'总代','13800920000','',NULL,NULL,'','admin','2026-03-27 22:18:02.156585','2026-03-28 13:56:21.475046','',92,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(37,'RY2068_001','2068','张中立',0,'水电专监','13800920000','',NULL,NULL,'','admin','2026-03-27 22:18:02.163305','2026-03-28 15:30:52.366243','',92,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(38,'RY2063_001','2063','唐昌罗',0,'总代','13800660000','','2026-03-28',NULL,'','黎绍昆','2026-03-28 06:46:59.656635','2026-03-28 15:30:52.362248','',66,1,NULL,NULL,NULL,NULL,NULL,'','','',''),(39,'RY001','','秦林',0,'','','总经办',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.172063','2026-03-28 15:48:16.172087','',NULL,0,1,NULL,NULL,NULL,NULL,'','','',''),(40,'RY002','','桂华',0,'','','总经办',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.180946','2026-03-28 15:48:16.180961','',NULL,0,2,NULL,NULL,NULL,NULL,'','','',''),(41,'RY003','','王敏志',0,'','13800740000','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.189793','2026-03-28 15:48:16.189807','',NULL,0,3,NULL,NULL,NULL,NULL,'','','',''),(42,'RY004','','林漓',0,'','','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.198587','2026-03-28 15:48:16.198599','',NULL,0,4,NULL,NULL,NULL,NULL,'','','',''),(43,'RY005','','方永明',0,'','','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.207308','2026-03-28 15:48:16.207320','',NULL,0,5,NULL,NULL,NULL,NULL,'','','',''),(44,'RY006','','唐薇薇',0,'','','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.216449','2026-03-28 15:48:16.216464','',NULL,0,6,NULL,NULL,NULL,NULL,'','','',''),(45,'RY007','','宋弦弦',0,'','','检测部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.226692','2026-03-28 15:48:16.226709','',NULL,0,7,NULL,NULL,NULL,NULL,'','','',''),(46,'RY008','','黄建波',0,'','','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.235562','2026-03-28 15:48:16.235574','',NULL,0,8,NULL,NULL,NULL,NULL,'','','',''),(47,'RY009','','廖志红',0,'','','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.244273','2026-03-28 15:48:16.244286','',NULL,0,9,NULL,NULL,NULL,NULL,'','','',''),(48,'RY010','','银雪',1,'主任','','总经办',NULL,NULL,NULL,'黎绍昆','2026-03-28 15:48:16.253489','2026-03-29 07:50:36.655425','',NULL,0,NULL,NULL,NULL,NULL,NULL,'','','',''),(49,'RY011','2058','黎绍昆',0,'总监','18978383227','监理部',NULL,NULL,NULL,'黎绍昆','2026-03-28 15:48:16.262344','2026-04-07 14:48:14.506257','',65,0,NULL,62,77,NULL,NULL,'2017','2019','2057',''),(50,'RY012','','程慧慧',0,'','','前期部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.271100','2026-03-28 15:48:16.271114','',NULL,0,12,NULL,NULL,NULL,NULL,'','','',''),(51,'RY013','','庞黎明',0,'','','检测部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.279406','2026-03-28 15:48:16.279418','',NULL,0,13,NULL,NULL,NULL,NULL,'','','',''),(52,'RY014','','龙欢',0,'','','检测部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.288824','2026-03-28 15:48:16.288842','',NULL,0,14,NULL,NULL,NULL,NULL,'','','',''),(53,'RY015','','周林松',0,'','','检测部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.298233','2026-03-28 15:48:16.298249','',NULL,0,15,NULL,NULL,NULL,NULL,'','','',''),(54,'RY016','','甘丽春',0,'','','造价部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.307064','2026-03-28 15:48:16.307078','',NULL,0,16,NULL,NULL,NULL,NULL,'','','',''),(55,'RY017','','柏翔',0,'','13800740002','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.316001','2026-03-28 15:48:16.316016','',NULL,0,17,NULL,NULL,NULL,NULL,'','','',''),(56,'RY018','','吉定斌',0,'','13800740003','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.325035','2026-03-28 15:48:16.325048','',NULL,0,18,NULL,NULL,NULL,NULL,'','','',''),(57,'RY019','','李闰',0,'','13800740004','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.335258','2026-03-28 15:48:16.335271','',NULL,0,19,NULL,NULL,NULL,NULL,'','','',''),(58,'RY020','','廖成刚',0,'','13800740005','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.343732','2026-03-28 15:48:16.343745','',NULL,0,20,NULL,NULL,NULL,NULL,'','','',''),(59,'RY021','','龙庆香',1,'','13800740006','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.352042','2026-03-28 15:48:16.352054','',NULL,0,21,NULL,NULL,NULL,NULL,'','','',''),(60,'RY022','','罗龙辉',0,'','13800740007','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.359979','2026-03-28 15:48:16.359989','',NULL,0,22,NULL,NULL,NULL,NULL,'','','',''),(61,'RY023','2058','秦方玉',0,'专监','13800740008','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.368432','2026-03-28 15:48:16.368442','',65,0,23,NULL,NULL,NULL,NULL,'','','',''),(62,'RY024','2004','秦养付',0,'总监','13800740009','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.376325','2026-03-29 06:48:50.974242','',58,0,24,13,NULL,NULL,NULL,'2042','','',''),(63,'RY025','','谭军',0,'','13800740010','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.384506','2026-03-28 15:48:16.384516','',NULL,0,25,NULL,NULL,NULL,NULL,'','','',''),(64,'RY026','2007','唐昌成',0,'总监','13800740011','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.392392','2026-03-29 16:03:07.491840','',59,0,26,84,64,NULL,NULL,'2047','2021','',''),(65,'RY027','2063','唐昌罗',0,'总代','13800740012','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.400042','2026-03-29 06:44:43.614688','',66,0,27,NULL,NULL,NULL,NULL,'','','',''),(66,'RY028','2069','唐满东',0,'','13800740013','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.408216','2026-04-07 14:47:11.931005','',67,0,28,92,NULL,NULL,NULL,'2068','','',''),(67,'RY029','2004','唐鹏',0,'监理员','13800740014','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.415874','2026-03-29 06:51:40.801283','',58,0,29,NULL,NULL,NULL,NULL,'','','',''),(68,'RY030','','汪勇',0,'','13800740015','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.423728','2026-03-28 15:48:16.423737','',NULL,0,30,NULL,NULL,NULL,NULL,'','','',''),(69,'RY031','','王立明',0,'','13800740016','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.431600','2026-03-28 15:48:16.431609','',NULL,0,31,NULL,NULL,NULL,NULL,'','','',''),(70,'RY032','2019','王璐',0,'总代','13800740017','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.439643','2026-03-28 15:48:16.439654','',77,0,32,NULL,NULL,NULL,NULL,'','','',''),(71,'RY033','2067','吴向南',0,'总监','13800740018','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.448375','2026-03-28 15:48:16.448384','',91,0,33,NULL,NULL,NULL,NULL,'','','',''),(72,'RY034','','谢荣明',0,'','13800740019','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.456461','2026-03-28 15:48:16.456471','',NULL,0,34,NULL,NULL,NULL,NULL,'','','',''),(73,'RY035','','阳著平',0,'','13800740020','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.464511','2026-03-28 15:48:16.464524','',NULL,0,35,NULL,NULL,NULL,NULL,'','','',''),(74,'RY036','2063','易强',0,'专监','13800740021','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.474667','2026-03-29 05:41:24.822729','',66,0,36,NULL,NULL,NULL,NULL,'','','',''),(75,'RY037','','张中立',0,'','13800740022','监理部',NULL,NULL,'','黎绍昆','2026-03-28 15:48:16.483672','2026-03-28 15:48:16.483683','',NULL,0,37,NULL,NULL,NULL,NULL,'','','',''),(76,'RYHT20260405140722_001','HT20260405140722','吴向南',0,'总监','13800960000','','2026-04-07','2026-05-02','','黎绍昆','2026-04-07 04:56:58.786852','2026-04-07 04:56:58.786871','',96,0,NULL,NULL,NULL,NULL,NULL,'','','',''),(77,'RY038','','王军',0,'','','',NULL,NULL,NULL,'','2026-04-07 05:05:52.439979','2026-04-07 05:05:52.440006','',NULL,0,NULL,NULL,NULL,NULL,NULL,'','','',''),(78,'RY039','','刘雄慧',0,'','','',NULL,NULL,NULL,'','2026-04-07 05:05:52.445518','2026-04-07 05:05:52.445555','',NULL,0,NULL,NULL,NULL,NULL,NULL,'','','',''),(79,'RY040','','何开华',0,'','','',NULL,NULL,NULL,'','2026-04-07 05:05:52.450202','2026-04-07 05:05:52.450217','',NULL,0,NULL,NULL,NULL,NULL,NULL,'','','',''),(80,'RY041','','胡敏杰',0,'','','',NULL,NULL,NULL,'','2026-04-07 05:05:52.454639','2026-04-07 05:05:52.454655','',NULL,0,NULL,NULL,NULL,NULL,NULL,'','','',''),(81,'RY042','','林桂峰',0,'','','',NULL,NULL,NULL,'','2026-04-07 05:05:52.459349','2026-04-07 05:05:52.459364','',NULL,0,NULL,NULL,NULL,NULL,NULL,'','','',''),(82,'RYHT20260405232807_001','HT20260405232807','秦方玉',0,'总监','13800970000','','2026-03-20',NULL,'','黎绍昆','2026-04-07 05:09:14.342219','2026-04-07 05:09:14.342237','',97,0,NULL,NULL,NULL,NULL,NULL,'','','',''),(83,'RYHT20260405232807_002','HT20260405232807','吉定斌',0,'总代','13800970000','','2026-04-07',NULL,'','黎绍昆','2026-04-07 05:09:37.476125','2026-04-07 05:09:37.476142','',97,0,NULL,NULL,NULL,NULL,NULL,'','','',''),(84,'RY2019_001','2019','秦方玉',0,'见证员','13800770000','','2026-04-01',NULL,'','黎绍昆','2026-04-07 05:27:40.176539','2026-04-07 05:27:40.176556','',77,0,NULL,NULL,NULL,NULL,NULL,'','','',''),(85,'RY2019_002','2019','吉定斌',0,'监理员','13800770000','',NULL,'2026-04-01','','黎绍昆','2026-04-07 05:28:34.729280','2026-04-07 05:28:34.729298','',77,0,NULL,NULL,NULL,NULL,NULL,'','','',''),(86,'RYHT20260405140722_002','HT20260405140722','李闰',0,'总代','13800960000','',NULL,NULL,'','王璐','2026-04-07 06:45:56.175693','2026-04-07 06:45:56.175711','',96,0,NULL,NULL,NULL,NULL,NULL,'','','',''),(87,'RYHT20260405232807_003','HT20260405232807','唐昌罗',0,'土建专监','13800970000','',NULL,'2026-04-07','','王璐','2026-04-07 07:34:35.401350','2026-04-07 07:34:35.401366','',97,0,NULL,NULL,NULL,NULL,NULL,'','','',''),(88,'RYHT20260405140722_003','HT20260405140722','吉定斌',0,'总代','13800960000','',NULL,NULL,'','黎绍昆','2026-04-07 14:20:34.924441','2026-04-07 14:20:34.924461','',96,0,NULL,NULL,NULL,NULL,NULL,'','','',''),(89,'RYHT20260405140722_004','HT20260405140722','吴向南',0,'土建专监','13800960000','',NULL,NULL,'','秦养付','2026-04-07 14:43:53.689480','2026-04-07 14:43:53.689494','',96,0,NULL,NULL,NULL,NULL,NULL,'','','',''),(90,'RYHT20260405140722_005','HT20260405140722','周林松',0,'总代','13800960000','',NULL,NULL,'','秦养付','2026-04-07 15:12:50.700059','2026-04-07 15:12:50.700079','',96,0,NULL,NULL,NULL,NULL,NULL,'','','','');
/*!40000 ALTER TABLE `eims_app_personnel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_personnelallocation`
--

DROP TABLE IF EXISTS `eims_app_personnelallocation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_personnelallocation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `is_deleted` tinyint(1) NOT NULL,
  `allocation_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `personnel_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `from_project_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `to_project_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `allocation_position` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `allocation_date` date NOT NULL,
  `expected_duration` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `allocation_status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `allocation_reason` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci,
  `operator` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `from_project_id` bigint DEFAULT NULL,
  `personnel_id` bigint NOT NULL,
  `to_project_id` bigint DEFAULT NULL,
  `allocation_department` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `allocation_code` (`allocation_code`),
  KEY `eims_app_personnelal_personnel_id_a000bbf0_fk_eims_app_` (`personnel_id`),
  KEY `eims_app_personnelallocation_personnel_code_6215bb8d` (`personnel_code`),
  KEY `eims_app_personnelal_from_project_id_b61a0107_fk_eims_app_` (`from_project_id`),
  KEY `eims_app_personnelal_to_project_id_2d39b766_fk_eims_app_` (`to_project_id`),
  CONSTRAINT `eims_app_personnelal_from_project_id_b61a0107_fk_eims_app_` FOREIGN KEY (`from_project_id`) REFERENCES `eims_app_projectdetail` (`id`),
  CONSTRAINT `eims_app_personnelal_personnel_id_a000bbf0_fk_eims_app_` FOREIGN KEY (`personnel_id`) REFERENCES `eims_app_personnel` (`id`),
  CONSTRAINT `eims_app_personnelal_to_project_id_2d39b766_fk_eims_app_` FOREIGN KEY (`to_project_id`) REFERENCES `eims_app_projectdetail` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_personnelallocation`
--

LOCK TABLES `eims_app_personnelallocation` WRITE;
/*!40000 ALTER TABLE `eims_app_personnelallocation` DISABLE KEYS */;
INSERT INTO `eims_app_personnelallocation` VALUES (3,0,'ALLOC2026032802124128_0','1005','','2004','总监','2026-03-28','','allocated','','岗位：总监, 分配时间：2026-03-28, 到岗时间：2026-03-28','admin','2026-03-27 18:12:41.375229','2026-03-27 18:12:41.375249',NULL,28,58,''),(4,0,'ALLOC2026032802124128_1','1005','','2003','总监','2026-03-28','','allocated','','岗位：总监, 分配时间：2026-03-28, 到岗时间：2026-03-31','admin','2026-03-27 18:12:41.380525','2026-03-27 18:12:41.380539',NULL,28,30,''),(5,0,'ALLOC2026032803304230_0','1007','','2002','监理员','2026-03-28','','allocated','','岗位：监理员, 分配时间：2026-03-28, 到岗时间：2026-03-28','admin','2026-03-27 19:30:42.499675','2026-03-27 19:30:42.499694',NULL,30,71,''),(6,0,'RECALL2026032909212439','RY001','','','待分配','2026-03-29','','recalled','人员召回',NULL,'黎绍昆','2026-03-29 01:21:24.974998','2026-03-29 01:21:24.975021',NULL,39,NULL,''),(7,0,'RECALL2026032909213450','RY012','','','待分配','2026-03-29','','recalled','人员召回',NULL,'黎绍昆','2026-03-29 01:21:34.114756','2026-03-29 01:21:34.114766',NULL,50,NULL,''),(8,0,'ALLOC2026032909262648_0','RY010','','2063','专监','2026-03-29','','allocated','','岗位：专监, 分配时间：2026-03-29, 到岗时间：2026-03-29','黎绍昆','2026-03-29 01:26:26.776434','2026-03-29 01:26:26.776444',NULL,48,66,''),(9,0,'RECALL2026032909265350','RY012','','','待分配','2026-03-29','','recalled','人员召回',NULL,'黎绍昆','2026-03-29 01:26:53.620138','2026-03-29 01:26:53.620149',NULL,50,NULL,''),(10,0,'RECALL2026032909271148','RY010','2063','','待分配','2026-03-29','','recalled','从项目召回部门',NULL,'黎绍昆','2026-03-29 01:27:11.964243','2026-03-29 01:27:11.964251',66,48,NULL,''),(11,0,'ALLOC2026032909283374_0','RY036','','2063','专监','2026-03-29','','allocated','','岗位：专监, 分配时间：2026-03-29, 到岗时间：2026-03-29','黎绍昆','2026-03-29 01:28:33.236188','2026-03-29 07:39:51.538015',NULL,74,66,''),(12,0,'RECALL2026032909294750','RY012','','','待分配','2026-03-29','','recalled','人员召回',NULL,'黎绍昆','2026-03-29 01:29:47.738591','2026-03-29 01:29:47.738606',NULL,50,NULL,''),(13,0,'RECALL2026032909335650','RY012','','','待分配','2026-03-29','','recalled','人员召回',NULL,'黎绍昆','2026-03-29 01:33:56.678992','2026-03-29 01:33:56.679003',NULL,50,NULL,''),(14,0,'RECALL2026032913371350','RY012','','','待分配','2026-03-29','','recalled','人员召回',NULL,'黎绍昆','2026-03-29 05:37:13.363640','2026-03-29 05:37:13.363651',NULL,50,NULL,''),(15,0,'RECALL2026032913412474','RY036','2063','','待分配','2026-03-29','','recalled','从项目召回部门',NULL,'黎绍昆','2026-03-29 05:41:24.830347','2026-03-29 05:41:24.830356',66,74,NULL,''),(16,0,'RECALL2026032913434539','RY001','','','待分配','2026-03-29','','recalled','人员召回',NULL,'黎绍昆','2026-03-29 05:43:45.201593','2026-03-29 05:43:45.201607',NULL,39,NULL,''),(17,0,'RECALL2026032913465439','RY001','','','待分配','2026-03-29','','recalled','人员召回',NULL,'黎绍昆','2026-03-29 05:46:54.886955','2026-03-29 05:46:54.886965',NULL,39,NULL,''),(18,0,'RECALL2026032913531750','RY012','','','待分配','2026-03-29','','recalled','人员召回',NULL,'黎绍昆','2026-03-29 05:53:17.420826','2026-03-29 05:53:17.420833',NULL,50,NULL,''),(19,0,'RECALL2026032913531739','RY001','','','待分配','2026-03-29','','recalled','人员召回',NULL,'黎绍昆','2026-03-29 05:53:17.430294','2026-03-29 05:53:17.430303',NULL,39,NULL,''),(21,0,'RECALL2026032913553765','RY027','2063','','待分配','2026-03-29','','recalled','从项目召回部门',NULL,'黎绍昆','2026-03-29 05:55:37.702078','2026-03-29 05:55:37.702089',66,65,NULL,''),(22,0,'RECALL2026032913571839','RY001','','','待分配','2026-03-29','','recalled','人员召回',NULL,'黎绍昆','2026-03-29 05:57:18.692822','2026-03-29 05:57:18.692831',NULL,39,NULL,''),(23,0,'RECALL2026032914050850','RY012','','','待分配','2026-03-29','','recalled','人员召回',NULL,'黎绍昆','2026-03-29 06:05:08.728632','2026-03-29 06:05:08.728643',NULL,50,NULL,'前期部'),(24,0,'RECALL2026032914095165','RY027','2063','','待分配','2026-03-29','','recalled','从项目召回部门',NULL,'黎绍昆','2026-03-29 06:09:51.849676','2026-03-29 06:09:51.849685',66,65,NULL,''),(25,0,'ALLOC2026032914124149_0','RY011','','2017','总监','2026-03-29','','allocated','','岗位：总监, 分配时间：2026-03-29, 到岗时间：2026-03-29','黎绍昆','2026-03-29 06:12:41.669305','2026-04-07 14:48:14.492298',NULL,49,62,''),(26,0,'ALLOC2026032914124149_1','RY011','2017','2058','总监','2026-03-29','','allocated','','岗位：总监, 分配时间：2026-03-29, 到岗时间：2026-03-29','黎绍昆','2026-03-29 06:12:41.678412','2026-04-07 14:48:14.479811',62,49,65,''),(27,0,'ALLOC2026032914124149_2','RY011','2017','2019','总监','2026-03-29','','allocated','','岗位：总监, 分配时间：2026-03-29, 到岗时间：2026-03-29','黎绍昆','2026-03-29 06:12:41.686125','2026-04-07 14:48:14.502586',62,49,77,''),(28,0,'ALLOC2026032914124149_3','RY011','2017','2057','总监','2026-03-29','','allocated','','岗位：总监, 分配时间：2026-03-29, 到岗时间：2026-03-29','黎绍昆','2026-03-29 06:12:41.694174','2026-03-29 06:12:41.694182',62,49,17,''),(29,0,'ALLOC2026032914444365_0','RY027','','2063','总代','2026-03-29','','allocated','','岗位：总代, 分配时间：2026-03-29, 到岗时间：2026-03-29','黎绍昆','2026-03-29 06:44:43.611026','2026-03-29 06:44:43.611038',NULL,65,66,''),(30,0,'ALLOC2026032914485062_0','RY024','','2004','总监','2026-03-29','','allocated','','岗位：总监, 分配时间：2026-03-29, 到岗时间：2026-03-29','黎绍昆','2026-03-29 06:48:50.967541','2026-03-29 06:48:50.967558',NULL,62,58,''),(31,0,'ALLOC2026032914485062_1','RY024','2004','2042','总监','2026-03-29','','allocated','','岗位：总监, 分配时间：2026-03-29, 到岗时间：2026-03-29','黎绍昆','2026-03-29 06:48:50.978361','2026-03-29 06:48:50.978369',58,62,13,''),(32,0,'ALLOC2026032914485067_0','RY029','','2004','监理员','2026-03-29','','allocated','','岗位：总监, 分配时间：2026-03-29, 到岗时间：2026-03-29','黎绍昆','2026-03-29 06:48:50.985916','2026-03-29 07:04:24.955187',NULL,67,58,''),(33,0,'ALLOC2026032914485067_1','RY029','2004','2042','总监','2026-03-29','','allocated','','岗位：总监, 分配时间：2026-03-29, 到岗时间：2026-03-29','黎绍昆','2026-03-29 06:48:50.993498','2026-03-29 06:48:50.993506',58,67,13,''),(34,0,'RECALL2026032914514067','RY029','2004','','待分配','2026-03-29','','recalled','从项目召回部门',NULL,'黎绍昆','2026-03-29 06:51:40.813458','2026-03-29 06:51:40.813470',58,67,NULL,''),(35,0,'ALLOC2026033000010761_0','RY023','','2058','专监','2026-03-30','','allocated','','岗位：专监, 分配时间：2026-03-30, 到岗时间：2026-03-30','黎绍昆','2026-03-29 16:01:07.032678','2026-03-29 16:01:07.032692',NULL,61,65,''),(36,0,'ALLOC2026033000030764_0','RY026','','2007','总监','2026-03-30','','allocated','','岗位：总监, 分配时间：2026-03-30, 到岗时间：2026-03-30','黎绍昆','2026-03-29 16:03:07.478582','2026-03-29 16:03:07.478592',NULL,64,59,''),(37,0,'ALLOC2026033000030764_1','RY026','2007','2047','总监','2026-03-30','','allocated','','岗位：总监, 分配时间：2026-03-30, 到岗时间：2026-03-30','黎绍昆','2026-03-29 16:03:07.487218','2026-03-29 16:03:07.487228',59,64,84,''),(38,0,'ALLOC2026033000030764_2','RY026','2007','2021','总监','2026-03-30','','allocated','','岗位：总监, 分配时间：2026-03-30, 到岗时间：2026-03-30','黎绍昆','2026-03-29 16:03:07.495924','2026-03-29 16:03:07.495934',59,64,64,''),(39,0,'ALLOC2026040500190271_0','RY033','','2067','总监','2026-04-05','','allocated','','岗位：总监, 分配时间：2026-04-05, 到岗时间：2026-04-05','黎绍昆','2026-04-04 16:19:02.348005','2026-04-04 16:19:02.348028',NULL,71,91,''),(40,0,'RECALL2026040521231372','RY034','','','待分配','2026-04-06','','recalled','人员召回',NULL,'admin','2026-04-05 13:23:13.618031','2026-04-05 13:23:13.618041',NULL,72,NULL,'监理部'),(41,0,'RECALL2026040521241472','RY034','','','待分配','2026-04-06','','recalled','人员召回',NULL,'admin','2026-04-05 13:24:14.925924','2026-04-05 13:24:14.925934',NULL,72,NULL,'监理部'),(42,0,'RECALL2026040521243872','RY034','','','待分配','2026-04-06','','recalled','人员召回',NULL,'admin','2026-04-05 13:24:38.430368','2026-04-05 13:24:38.430377',NULL,72,NULL,'监理部'),(43,0,'ALLOC2026040722471166_0','RY028','','2069','','2026-04-07','','allocated','','','黎绍昆','2026-04-07 14:47:11.924103','2026-04-07 14:47:11.924123',NULL,66,67,''),(44,0,'ALLOC2026040722471166_1','RY028','2069','2068','','2026-04-07','','allocated','','','黎绍昆','2026-04-07 14:47:11.935693','2026-04-07 14:47:11.935709',67,66,92,''),(45,0,'ALLOC2026040722484770_0','RY032','','2019','总代','2026-04-07','','allocated','','岗位：总代, 分配时间：未指定, 到岗时间：未指定','黎绍昆','2026-04-07 14:48:47.935701','2026-04-07 14:48:47.935712',NULL,70,77,'');
/*!40000 ALTER TABLE `eims_app_personnelallocation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_personnelcertificate`
--

DROP TABLE IF EXISTS `eims_app_personnelcertificate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_personnelcertificate` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `is_deleted` tinyint(1) NOT NULL,
  `certificate_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `personnel_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `certificate_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `certificate_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `issuing_authority` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `issue_date` date NOT NULL,
  `valid_date` date DEFAULT NULL,
  `certificate_file` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci,
  `operator` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `personnel_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `certificate_code` (`certificate_code`),
  KEY `eims_app_personnelce_personnel_id_6b3929a0_fk_eims_app_` (`personnel_id`),
  KEY `eims_app_personnelcertificate_personnel_code_8f54b578` (`personnel_code`),
  CONSTRAINT `eims_app_personnelce_personnel_id_6b3929a0_fk_eims_app_` FOREIGN KEY (`personnel_id`) REFERENCES `eims_app_personnel` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_personnelcertificate`
--

LOCK TABLES `eims_app_personnelcertificate` WRITE;
/*!40000 ALTER TABLE `eims_app_personnelcertificate` DISABLE KEYS */;
/*!40000 ALTER TABLE `eims_app_personnelcertificate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_project`
--

DROP TABLE IF EXISTS `eims_app_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_project` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `project_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_category` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_address` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_scale` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_investment` decimal(15,2) DEFAULT NULL,
  `notice_date` date DEFAULT NULL,
  `entry_time` date DEFAULT NULL,
  `actual_start_time` date DEFAULT NULL,
  `planned_completion_time` date DEFAULT NULL,
  `project_status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_delayed` tinyint(1) NOT NULL,
  `delay_status` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `delay_description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_manager` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_director` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `actual_manager` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_code` (`project_code`),
  KEY `eims_app_project_project_name_3c026ceb` (`project_name`),
  KEY `eims_app_project_project_director_4b660e79` (`project_director`),
  KEY `eims_app_project_actual_manager_6ce2fe37` (`actual_manager`),
  KEY `eims_app_pr_project_fbf0c6_idx` (`project_code`,`project_name`),
  KEY `eims_app_pr_project_e60ebe_idx` (`project_category`,`project_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_project`
--

LOCK TABLES `eims_app_project` WRITE;
/*!40000 ALTER TABLE `eims_app_project` DISABLE KEYS */;
/*!40000 ALTER TABLE `eims_app_project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_projectdetail`
--

DROP TABLE IF EXISTS `eims_app_projectdetail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_projectdetail` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `contract_category` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `monthly_report_required` tinyint(1) NOT NULL,
  `project_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contract_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contract_status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `settlement_status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contract_party_a` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contract_party_b` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `signing_date` date DEFAULT NULL,
  `contract_text` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contract_amount` decimal(15,2) NOT NULL,
  `payment_agreement` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `cumulative_payment` decimal(15,2) NOT NULL,
  `contract_balance` decimal(15,2) NOT NULL,
  `project_scale` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_investment` decimal(15,2) DEFAULT NULL,
  `project_address` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `agreed_staffing` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `service_deadline` date DEFAULT NULL,
  `extension_agreement` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `actual_extension_status` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `construction_permit_status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `construction_permit` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `entry_notice` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `entry_notice_document` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `entry_time` date DEFAULT NULL,
  `planned_start_date` date DEFAULT NULL,
  `actual_start_date` date DEFAULT NULL,
  `estimated_completion_date` date DEFAULT NULL,
  `project_director` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_manager` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact_phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `service_period_months` int NOT NULL,
  `service_start_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_code` (`project_code`),
  KEY `eims_app_projectdetail_contract_code_df444070` (`contract_code`),
  KEY `eims_app_projectdetail_project_name_b64885b2` (`project_name`),
  KEY `eims_app_projectdetail_project_director_4c85f129` (`project_director`),
  KEY `eims_app_projectdetail_project_manager_e9026b26` (`project_manager`),
  KEY `eims_app_pr_project_f94850_idx` (`project_code`,`project_name`),
  KEY `eims_app_pr_contrac_195b86_idx` (`contract_code`),
  KEY `eims_app_pr_project_e19340_idx` (`project_status`,`contract_status`),
  KEY `eims_app_pr_contrac_23003e_idx` (`contract_category`)
) ENGINE=InnoDB AUTO_INCREMENT=98 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_projectdetail`
--

LOCK TABLES `eims_app_projectdetail` WRITE;
/*!40000 ALTER TABLE `eims_app_projectdetail` DISABLE KEYS */;
INSERT INTO `eims_app_projectdetail` VALUES (10,'engineering_supervision',0,'2036','JL2036','平乐县汉华三江合际小区二期11#、12#、13#楼','completed','executing','unsettled','广西汉华房地产开发需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',243000.00,'0',11956.30,231043.70,'27000㎡',NULL,'','',NULL,'--','','incomplete','','yes','','2019-06-01',NULL,'2019-08-01','2024-12-01','RY026','RY026','','','2026-03-27 06:09:01.204596','2026-03-27 08:22:55.558953',0,NULL),(11,'engineering_supervision',0,'2038','JL2038','平乐县汉华三江合际小区二期6#、7#、8#、9#、10#楼及B区地下室','completed','executing','unsettled','广西汉华房地产开发需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',459171.81,'0',11956.30,447215.51,'51019.09㎡',NULL,'','',NULL,'--','','incomplete','','yes','',NULL,NULL,'2022-03-01',NULL,'RY041','RY041','13768237946','','2026-03-27 06:09:01.213187','2026-03-27 08:22:55.569510',0,NULL),(12,'engineering_supervision',0,'2040','JL2040','全州县名门世家','completed','executing','unsettled','桂林东舜置业需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',1739000.00,'0',11956.30,1727043.70,'0',NULL,'','',NULL,'--','','incomplete','','yes','','2021-04-06',NULL,'2019-04-01','2025-10-01','RY040','RY040','13299635991','','2026-03-27 06:09:01.218817','2026-03-27 08:22:55.579375',0,NULL),(13,'engineering_supervision',0,'2042','JL2042','泰安·独秀天下','completed','executing','unsettled','广西泰安房地产开发需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',150543.72,'0',11956.30,138587.42,'50000㎡',NULL,'','',NULL,'--','','incomplete','','yes','','2019-07-03',NULL,NULL,'2024-10-31','RY011','RY011','17377333686','','2026-03-27 06:09:01.224337','2026-03-27 08:22:55.589925',0,NULL),(14,'engineering_supervision',0,'2045','JL2045','同乐d2安置小区及相关配套工程（2个合同）','completed','executing','unsettled','平乐人居环境','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',150000.00,'0',0.00,150000.00,'0',NULL,'','',NULL,'--','','incomplete','','yes','',NULL,NULL,'2019-03-27',NULL,'RY003','','15977444154','','2026-03-27 06:09:01.231111','2026-03-27 08:22:55.606594',0,NULL),(15,'engineering_supervision',0,'2046','JL2046','五福顺特色食品产业园新建厂区4#5#6#楼厂房','completed','executing','unsettled','桂林五福顺食品需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',192681.16,'0',0.00,192681.16,'27525.88㎡',NULL,'','',NULL,'--','','incomplete','','yes','',NULL,NULL,'2019-03-01',NULL,'','RY037','15977444154','','2026-03-27 06:09:01.235958','2026-03-27 08:22:55.611630',0,NULL),(16,'engineering_supervision',0,'2054','JL2054','雁山项目道路','completed','executing','unsettled','0','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',0.00,'0',0.00,0.00,'0',NULL,'','',NULL,'--','','incomplete','','yes','',NULL,NULL,NULL,NULL,'RY026','RY026','','','2026-03-27 06:09:01.243901','2026-03-27 08:22:55.653859',0,NULL),(17,'engineering_supervision',0,'2057','JL2057','长山片区安置房一期建设工程','stopped','executing','unsettled','桂林市七星区朝阳乡人民政府','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',596700.00,'0',0.00,596700.00,'20510.59㎡',4931.80,'桂林市七星区','',NULL,'--','','incomplete','','yes','',NULL,NULL,'2022-03-01',NULL,'RY041','RY041','','','2026-03-27 06:09:01.250218','2026-03-27 08:22:55.669836',0,NULL),(18,'engineering_supervision',0,'2066','JL2066','灌阳县财政局2023年农村综合改革转移支付资金项目','completed','executing','unsettled','0','0',NULL,'',0.00,'0',0.00,0.00,'0',NULL,'','',NULL,'--','','incomplete','','yes','',NULL,NULL,NULL,NULL,'RY038','RY039','','13737745570','2026-03-27 06:09:01.258471','2026-03-27 08:22:55.725667',0,NULL),(19,'engineering_supervision',1,'2070','JL2070','蓝天科技双创孵化项目规划调整','stopped','executing','unsettled','广西蓝天科技需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'',80000.00,'0',200000.00,-120000.00,'3808.19平方米(总规模：13058.96平方米，项目总投资额：28506028.59元',NULL,'','',NULL,'--','','incomplete','','yes','',NULL,NULL,'2019-03-27',NULL,'RY003','','15977444154','','2026-03-27 06:09:01.262913','2026-03-27 08:22:55.747250',0,NULL),(20,'engineering_supervision',0,'3001','JL3001','枫林·福祥里7.9.10楼','completed','executing','unsettled','桂林广厦房地产开发需要限公司','重庆财汇',NULL,'',1147418.00,'0',200000.00,947418.00,'97238㎡',NULL,'','',NULL,'--','','incomplete','','yes','',NULL,NULL,'2019-03-01',NULL,'','RY037','15977444154','','2026-03-27 06:09:01.267226','2026-03-27 08:22:55.752461',0,NULL),(21,'engineering_supervision',0,'1001','JL1001','桂林润启月扬商贸需要限公司厂区','completed','executing','settled','桂林润启月扬商贸需要限公司','广西晟昌工程科技需要限责任公司',NULL,'https://www.kdocs.cn/l/ct8befXGLIcf',60000.00,'--',11.00,59989.00,'9622.06㎡',NULL,'乐和工业园','0',NULL,'--','','incomplete','','yes','','2023-08-30',NULL,'2023-09-01','2024-08-29','RY003','RY022','13152582589','已收监理费12000元','2026-03-27 06:35:27.922012','2026-03-27 07:50:08.731393',0,NULL),(22,'engineering_supervision',0,'1003','JL1003','桂林市临桂县新兴包装制品厂建设项目1#生产车间','completed','executing','unsettled','桂林市临桂县新兴包装制品厂','广西晟昌工程科技需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',6048.00,'--',0.00,6048.00,'756㎡',200.00,'乐和工业园','','2023-08-30','--','','incomplete','','yes','','2020-02-27',NULL,'2020-02-27','2024-06-30','RY028','RY028','13737745570','已收监理费11400元','2026-03-27 06:35:27.930356','2026-03-27 08:22:55.306689',0,NULL),(23,'engineering_supervision',0,'1004','JL1004','桂林市临桂镇繁荣石笔厂建设项目1#厂房','completed','executing','unsettled','桂林市临桂镇繁荣石笔厂','广西晟昌工程科技需要限责任公司',NULL,'https://www.kdocs.cn/l/cmahvLvG8Sjx',28747.00,'--',26000.00,2747.00,'2588㎡',600.00,'乐和工业园','','2023-08-01','--','','incomplete','','yes','','2021-04-06',NULL,'2021-02-19','2024-01-22','RY040','RY040','13299635991','已收监理费11400元','2026-03-27 06:35:27.935133','2026-03-27 08:22:55.312700',0,NULL),(24,'engineering_supervision',0,'1005','JL1005','华申·武陵国际商贸城蔬菜批发市场（湖南吉首综合市场）','stopped','executing','unsettled','吉首信达地产开发需要限公司','广西晟昌工程科技需要限责任公司',NULL,'https://www.kdocs.cn/l/cvCoTDVpmRbY',262362.00,'--',0.00,0.00,'43727㎡',NULL,'吉首市仓储路','','2023-07-05','--','','incomplete','','yes','','2021-06-20',NULL,'2021-06-20','2025-07-20','RY024','RY024','15677318699','不需要','2026-03-27 06:35:27.939373','2026-03-27 08:22:55.318370',0,NULL),(25,'engineering_supervision',0,'1006','JL1006','象州象源幸福里项目3#、6#、8#楼建设工程','stopped','executing','unsettled','广西象州恒伟置业投资需要限公司','广西晟昌工程科技需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',160000.00,'--',40000.00,120000.00,'26000㎡',NULL,'来宾市象州县','','2024-03-26','--','','incomplete','','yes','','2021-08-18',NULL,'2021-08-18','2023-02-17','RY031','RY031','18978336067','不需要','2026-03-27 06:35:27.944014','2026-03-27 08:22:55.324013',0,NULL),(26,'engineering_supervision',0,'1007','JL1007','中国桂北福寿颐养园（续建）项目','completed','executing','unsettled','永福县中医医院','广西晟昌工程科技需要限责任公司',NULL,'https://www.kdocs.cn/l/chBhRvo2X87V',158280.00,'--',0.00,158280.00,'7011.35㎡',NULL,'永福县','',NULL,'--','','incomplete','','yes','','2022-12-14',NULL,'2022-12-14','2024-03-31','RY011','RY011','18978336067','','2026-03-27 06:35:27.948530','2026-03-27 08:22:55.329476',0,NULL),(27,'engineering_supervision',0,'1008','JL1008','龙胜各族自治县龙脊镇小学教师周转房项目','completed','executing','unsettled','龙胜各族自治县教育局','广西晟昌工程科技需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',76363.23,'--',0.00,76363.23,'1975㎡',664.03,'龙胜各族自治县龙脊镇小学','',NULL,'--','','incomplete','','yes','','2020-08-17',NULL,'2020-08-17','2024-07-10','RY011','RY011','18978383227','','2026-03-27 06:35:27.953243','2026-03-27 08:22:55.334854',0,NULL),(28,'engineering_supervision',0,'1009','JL1009','广西意城新能源物流配送基地项目-2#设备房','completed','executing','unsettled','广西意城新能源科技发展需要限公司','广西晟昌工程科技需要限责任公司',NULL,'https://www.kdocs.cn/l/cllMYKaSdQ2n',10000.00,'--',30000.00,-20000.00,'总建筑面积748.88m²(地上569.36m²,地下179.52m²)',NULL,'桂林市临桂区','',NULL,'--','','incomplete','','yes','','2022-07-15',NULL,'2022-07-15','2024-09-25','RY027','RY027','13768237946','','2026-03-27 06:35:27.957455','2026-03-27 08:22:55.340406',0,NULL),(29,'engineering_supervision',0,'1010','JL1010','新屋优质稻产业基地水渠配套工程','completed','executing','settled','桂林市临桂区两江镇人民镇府','广西晟昌工程科技需要限责任公司',NULL,'https://www.kdocs.cn/l/cr3Sc7kuP8xz',16434.00,'0',0.00,16434.00,'㎡',NULL,'','',NULL,'--','','incomplete','','yes','','2023-10-31',NULL,'2023-10-31','2024-06-01','RY027','RY027','15977444154','已收监理费50000元','2026-03-27 06:35:27.962130','2026-03-27 08:22:55.345825',0,NULL),(30,'engineering_supervision',0,'2003','JL2003','百亿商贸城（一期）','completed','executing','unsettled','桂林市龙胜百亿房地产投资需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',778408.96,'0',5.00,778403.96,'97301.12㎡',NULL,'','','2026-03-09','--','','incomplete','','yes','','2019-12-16',NULL,'2019-12-16','2024-12-16','RY026','RY026','15977444154','已收监理费50000元','2026-03-27 06:35:27.966779','2026-03-27 08:22:55.369051',0,NULL),(31,'engineering_supervision',0,'2005','JL2005','拆迁安置住宅及回建生产保障用房工程','completed','executing','unsettled','桂林市穿山公园管理处','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',50000.00,'0',5000.00,45000.00,'2616㎡，300万元',NULL,'桂林市漓江路与穿山小街交叉口东南面','','2024-06-01','--','','incomplete','','yes','','2023-10-10',NULL,'2023-10-01','2024-07-10','RY038','RY023','18677303129','','2026-03-27 06:35:28.022250','2026-03-27 08:22:55.380319',0,NULL),(32,'engineering_supervision',0,'2006','JL2006','大型环保特缆生产制造项目(1#宿舍楼、2#仓库、12#宿舍楼)','completed','executing','unsettled','桂林国际电线电缆集团需要限责任公司','广西鼎策工程顾问需要限责任公司',NULL,'https://www.kdocs.cn/l/cgwFsSwNMEBT',165079.84,'--',0.00,0.00,'17018.54㎡（其中，1#宿舍楼建筑面积2866.11㎡,2#仓库建筑面积1200㎡,12#宿舍楼12952.43㎡）',NULL,'桂林市临桂区四塘镇广福路1号','','2024-11-27','--','','incomplete','','yes','','2023-08-03',NULL,'2023-08-03','2024-08-02','RY011','RY027','13768237946','监理费41000元已开票，预计2024年元月到账','2026-03-27 06:35:28.027160','2026-03-27 08:22:55.386516',0,NULL),(33,'engineering_supervision',0,'2009','JL2009','翡翠·潮庭项目二期（8#、9#、10#、11#、12#、16#、18#、20#、21#楼及二期地下室）','completed','executing','unsettled','桂林市宝亨通置业需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',2019464.00,'0',1064245.50,955218.50,'118792㎡',NULL,'','','2021-09-01','--','','incomplete','','yes','','2020-02-27',NULL,'2020-02-27','2024-06-30','RY028','RY028','18777302196','已收监理费11400元.余款10000预计2024年元月到账','2026-03-27 06:35:28.038141','2026-03-27 08:22:55.403647',0,NULL),(34,'engineering_supervision',0,'2015','JL2015','桂林市临桂新区机场路以北片区湖塘水系连通周边景观绿化工程总承包EPC项目','completed','executing','unsettled','桂林新城投资开发集团需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',5289216.00,'0',831215.60,4458000.40,'57180㎡',528.90,'','','2023-02-01','--','','incomplete','','yes','','2023-08-31',NULL,'2023-09-01','2024-11-30','RY003','RY022','13152582589','','2026-03-27 06:35:28.049637','2026-03-27 08:22:55.440365',0,NULL),(35,'engineering_supervision',0,'2022','JL2022','老城片区防洪排涝综合治理工程二期-新龙路延长线排涝截污工程、秧塘片区部分道路排水管道改造工程及临政路、兴临路道路及排水管道改造工程','completed','executing','unsettled','临桂区城昇农业综合开发需要限责任公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',1167300.00,'0',290000.00,877300.00,'道路长4.88Km,管道长8.64Km',116.73,'','','2025-05-10','--','','incomplete','','yes','','2022-05-05',NULL,'2022-04-22','2024-08-22','RY011','RY027','13768237946','','2026-03-27 06:35:28.079519','2026-03-27 08:22:55.479726',0,NULL),(36,'engineering_supervision',0,'2023','JL2023','乐和工业区供水主管网工程','completed','executing','unsettled','桂林市临桂区工信和商贸局','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',67320.00,'0',1237000.00,-1169680.00,'3000㎡',400.00,'乐和工业园','',NULL,'--','','incomplete','','yes','','2022-07-15',NULL,'2022-07-15','2024-09-25','RY027','RY027','13768237946','合同监理费申请方永明哪边负责。','2026-03-27 06:35:28.084034','2026-03-27 08:22:55.484751',0,NULL),(37,'engineering_supervision',0,'2024','JL2024','乐和工业园区污水泵站至西二环截污工程','completed','executing','unsettled','桂林市临桂区工信和商贸局','广西鼎策工程顾问需要限责任公司',NULL,'https://www.kdocs.cn/l/cg0lVDWj3FAY',6336.00,'--',1237000.00,-1230664.00,'不详',320.00,'桂林市临桂区','',NULL,'--','','incomplete','','yes','','2022-08-29',NULL,'2019-04-01','2024-04-30','RY003','RY027','13768237946','本项目投资约320万元，按收费标准计费：320*3.3%=10.56万元，按60%优惠计取，\n即10.56万元*60%=6.336万元','2026-03-27 06:35:28.089451','2026-03-27 08:22:55.490380',0,NULL),(38,'engineering_supervision',0,'2025','JL2025','悦桂情歌田园沐歌小镇-展示中心及周边园林绿化工程项目（良丰农场）','completed','executing','unsettled','广西桂林光大立元生态家园开发建设需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'',220000.00,'0',1237000.00,-1017000.00,'0',1700.00,'','',NULL,'--','','incomplete','','yes','','2020-02-27',NULL,'2020-02-27','2024-06-30','RY028','RY028','18777302196','2020年完成施工，未签监理合同，2023.12.10需要双方确认函','2026-03-27 06:35:28.094056','2026-03-27 08:22:55.495997',0,NULL),(39,'engineering_supervision',0,'2026','JL2026','两江镇河沙现代高效养殖场','completed','executing','unsettled','桂林市临桂区名冠养殖专业合作社','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',764652.00,'0',1237000.00,-472348.00,'0',NULL,'','',NULL,'--','','incomplete','','yes','','2023-08-31',NULL,'2023-09-01','2024-11-30','RY027','RY027','15977444154','','2026-03-27 06:35:28.098948','2026-03-27 08:22:55.501450',0,NULL),(40,'engineering_supervision',0,'2030','JL2030','柳州彰泰滨江学府','completed','executing','unsettled','柳州彰泰建设需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',1744466.82,'0',1237000.00,507466.82,'29495.14㎡',NULL,'柳州市柳北区北雀路45号','',NULL,'--','','incomplete','','yes','','2021-06-18',NULL,'2019-03-01','2024-11-27','','RY037','15977444154','','2026-03-27 06:35:28.103000','2026-03-27 08:22:55.524889',0,NULL),(41,'engineering_supervision',0,'2031','JL2031','柳州彰泰欢乐颂','completed','executing','unsettled','柳州弘彰房地产开发需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',4545352.59,'0',1313144.26,3232208.33,'423700㎡',NULL,'','','2023-06-27','--','','incomplete','','yes','','2019-07-03',NULL,'2019-07-03','2024-10-31','RY011','RY011','17377333686','','2026-03-27 06:35:28.107178','2026-03-27 08:22:55.530624',0,NULL),(42,'engineering_supervision',0,'2032','JL2032','龙胜县中医医院整体搬迁重建','completed','executing','unsettled','龙胜县中医医院','广西鼎策工程顾问需要限责任公司',NULL,'https://www.kdocs.cn/l/cqIES5CcgmsS',724800.00,'--',11956.30,712843.70,'15350㎡',5000.00,'龙胜县','',NULL,'--','','incomplete','','yes','','2023-12-14',NULL,'2023-12-14','2024-05-31','RY011','','18978336067','本项目总投资额：约257万元，按双方协商，按建设部发改价格【2007】670号收费标准的36%计取，即：257万元×（16.5/500万元）×36%=3.0531万元.','2026-03-27 06:35:28.112551','2026-03-27 08:22:55.536469',0,NULL),(43,'engineering_supervision',0,'2033','JL2033','龙象一路道路建设项目','completed','executing','unsettled','桂林兴象投资开发需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://www.kdocs.cn/l/cpLWz0oMISIs',35200.00,'--',11956.30,23243.70,'道路全长242米，红线宽22米，城市支路',286.00,'桂林市象山区凯风路2号','',NULL,'--','','incomplete','','yes','','2020-08-17',NULL,'2024-08-17','2024-07-30','RY011','RY011','18978383227','','2026-03-27 06:35:28.117523','2026-03-27 08:22:55.542058',0,NULL),(44,'engineering_supervision',0,'2037','JL2037','平乐县汉华三江合际小区二期3#、4#、5#楼','completed','executing','unsettled','广西汉华房地产开发需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',247203.00,'0',11956.30,235246.70,'27467㎡',NULL,'','',NULL,'--','','incomplete','','yes','','2019-07-03',NULL,'2021-05-21','2024-10-31','RY011','RY011','17377333686','按建筑面积每平方米捌元(¥8元/ m²)计取监理酬金','2026-03-27 06:35:28.125860','2026-03-27 08:22:55.564397',0,NULL),(45,'engineering_supervision',0,'2039','JL2039','全州和心医院','completed','executing','unsettled','全州和心医院','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',1200000.00,'0',11956.30,1188043.70,'0',NULL,'','',NULL,'--','','incomplete','','yes','','2022-07-15',NULL,'2022-07-15','2024-09-25','RY038','RY039','13558131558','预计2024.2月30日竣工','2026-03-27 06:35:28.134741','2026-03-27 08:22:55.574676',0,NULL),(46,'engineering_supervision',0,'2041','JL2041','水系管理用房装修工程','completed','executing','unsettled','新城投资集团','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',150543.72,'0',11956.30,138587.42,'3270㎡',NULL,'','',NULL,'--','','incomplete','','yes','','2023-03-09',NULL,'2020-02-27','2026-03-09','RY031','RY042','18777302196','','2026-03-27 06:35:28.143516','2026-03-27 08:22:55.584491',0,NULL),(47,'engineering_supervision',0,'2043','JL2043','天驰桂宏达·公园悦府','completed','executing','unsettled','南宁天驰房地产需要限公司灵川分公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',2776000.00,'0',11956.30,2764043.70,'79952㎡',NULL,'','',NULL,'--','','incomplete','','yes','','2023-08-30',NULL,'2023-08-31','2024-11-28','RY038','RY039','13152582589','13737745570','2026-03-27 06:35:28.152048','2026-03-27 08:22:55.595413',0,NULL),(48,'engineering_supervision',0,'2044','JL2044','同方新建厂房','completed','executing','unsettled','桂林同方泓嘉科技需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',119563.00,'0',11956.30,107606.70,'14580.92㎡',NULL,'','','2023-03-15','--','','incomplete','','yes','','2021-05-21',NULL,'2022-08-20','2025-06-08','RY024','RY024','15677318699','12月12日项目复工，建设单位名称变更为桂林同方泓嘉科技需要限公司','2026-03-27 06:35:28.156501','2026-03-27 08:22:55.600919',0,NULL),(49,'engineering_supervision',0,'2048','JL2048','象塘路9-2-1、9-2-2 、10-2地块项目1#~3#、5#~11#楼及地下公共停车场','completed','executing','unsettled','龙光普罗旺斯','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',897000.00,'0',10000.00,887000.00,'74516.43㎡',NULL,'','',NULL,'--','','incomplete','','yes','','2019-07-03',NULL,'2019-07-03','2024-10-31','RY011','RY011','17377333686','','2026-03-27 06:35:28.169154','2026-03-27 08:22:55.622130',0,NULL),(50,'engineering_supervision',0,'2049','JL2049','临桂镇大律村委会大律村文化楼工程','completed','executing','unsettled','桂林市临桂镇大律村委会大律村','广西鼎策工程顾问需要限责任公司',NULL,'',30531.00,'--',10000.00,20531.00,'约1290㎡',257.00,'桂林市临桂区','',NULL,'--','','incomplete','','yes','','2023-12-14',NULL,'2023-12-14','2024-05-31','RY011','','18978336067','本项目总投资额：约257万元，按双方协商，按建设部发改价格【2007】670号收费标准的36%计取，即：257万元×（16.5/500万元）×36%=3.0531万元.','2026-03-27 06:35:28.173590','2026-03-27 08:22:55.627320',0,NULL),(51,'engineering_supervision',0,'2051','JL2051','兴安工业集中区标准厂房二期厂房','completed','executing','unsettled','桂林兴安盛邑工业需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',2014789.82,'0',628345.61,1386444.21,'59284.66㎡',NULL,'','','2024-01-20','--','','incomplete','','yes','','2020-08-17',NULL,'2024-08-17','2024-07-30','','RY011','18978383227','','2026-03-27 06:35:28.178163','2026-03-27 08:22:55.637936',0,NULL),(52,'engineering_supervision',0,'2053','JL2053','雁山风貌改造（共4个合同）','completed','executing','unsettled','雁山建设局','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',955554.00,'0',0.00,955554.00,'0',NULL,'','',NULL,'--','','incomplete','','yes','','2021-06-21',NULL,NULL,'2024-06-21','RY026','RY026','','','2026-03-27 06:35:28.182813','2026-03-27 08:22:55.648704',0,NULL),(53,'engineering_supervision',0,'2055','JL2055','永福卫生院综合楼','completed','executing','unsettled','永福县卫生院','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',115320.00,'0',0.00,115320.00,'3010.88㎡',NULL,'','','2022-11-19','--','','incomplete','','yes','','2019-06-01',NULL,NULL,'2024-12-01','','RY026','','','2026-03-27 06:35:28.190292','2026-03-27 08:22:55.659246',0,NULL),(54,'engineering_supervision',0,'2056','JL2056','永福县城农贸综合市场工程项目','completed','executing','unsettled','桂林市锦丰房地产开发需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://www.kdocs.cn/l/ceFPCtW1hS68',732984.00,'--',0.00,732984.00,'91623㎡',13000.00,'永福县农贸市场','',NULL,'--','','incomplete','','yes','','2019-07-03',NULL,NULL,'2024-10-31','RY011','RY011','17377333686','按建筑面积每平方米捌元(¥8元/ m²)计取监理酬金','2026-03-27 06:35:28.194417','2026-03-27 08:22:55.664537',0,NULL),(55,'engineering_supervision',0,'2059','JL2059','桂林市清风实验学校北片地块D-10-1地块一期','completed','executing','unsettled','桂林市兴进投资发展需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://www.kdocs.cn/l/cnCL7PTZUsHT',1627500.00,'--',1095394.58,532105.42,'建筑面积约 155000㎡（含地下室35000）',35000.00,'叠彩区滨江北路以西，芳华路以南，江与城小区以北，叠彩万达广场以南','',NULL,'--','','incomplete','','yes','','2021-04-06',NULL,NULL,'2025-10-01','RY040','RY040','13299635991','','2026-03-27 06:35:28.208750','2026-03-27 08:22:55.680690',0,NULL),(58,'engineering_supervision',1,'2004','JL2004','滨江郡府1#-3#楼及地下室、5#楼及地下室、6#-9#楼及地下室、11#楼及地下室','under_construction','executing','unsettled','柳州市君源房地产开发需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',1100000.00,'0',0.00,0.00,'110000㎡',NULL,'','','2024-11-27','--','','incomplete','','yes','','2019-06-01',NULL,'2019-06-01','2024-08-08','RY026','RY026','','','2026-03-27 07:49:29.141865','2026-03-27 08:22:55.374776',0,NULL),(59,'engineering_supervision',0,'2007','JL2007','东苑国际住宅小区三期','completed','executing','unsettled','桂林福龙房地产开发需要限公司 、桂林市竣为房地产需要限责任公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',570000.00,'0',0.00,0.00,'57000㎡',NULL,'','','2023-06-20','--','','incomplete','','yes','','2019-03-26',NULL,'2019-04-01','2021-08-15','RY003','RY027','13768237946','','2026-03-27 07:49:29.155402','2026-03-27 08:22:55.392122',0,NULL),(60,'engineering_supervision',0,'2014','JL2014','桂林市公安局临桂分局新城派出所及110巡警大队业务技术用房--备勤楼全过程工程咨询服务','completed','executing','unsettled','桂林市公安局临桂分局','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',2669019.30,'--',0.00,0.00,'10980㎡，总投资5097.73万元',NULL,'临桂新区经一路东侧、纬二路北侧','','2024-04-08','--','','incomplete','','yes','','2022-12-14',NULL,'2022-12-14','2024-03-31','RY011','RY011','18978336067','2020年完成施工，未签监理合同，2023.12.10需要双方确认函','2026-03-27 07:49:29.163799','2026-03-27 08:22:55.434502',0,NULL),(61,'engineering_supervision',0,'2016','JL2016','桂林市临桂新区经三路建设工程','completed','executing','unsettled','桂林新城投资开发集团需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',213000.00,'0',0.00,0.00,'0',NULL,'','',NULL,'--','','incomplete','','yes','','2021-06-18',NULL,'2021-06-18','2024-11-27','RY024','RY024','15677318699','','2026-03-27 07:49:29.172843','2026-03-27 08:22:55.446013',0,NULL),(62,'engineering_supervision',0,'2017','JL2017','桂林市文化旅游中心漓江歌剧院项目','completed','executing','unsettled','桂林市文化广电和旅游局','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',4070000.00,'0',0.00,0.00,'20000㎡',NULL,'','','2022-12-01','--','','incomplete','','yes','','2021-06-21',NULL,'2021-06-21','2024-06-20','RY026','RY026','','','2026-03-27 07:49:29.177344','2026-03-27 08:22:55.451650',0,NULL),(63,'engineering_supervision',0,'2018','JL2018','桂林市袁大头食品需要限公司新建厂房1#、2#厂房建设项目','completed','executing','unsettled','桂林市袁大头食品需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',44800.00,'--',0.00,0.00,'5600㎡',NULL,'乐和工业园','','2023-05-30','--','','incomplete','','yes','','2019-12-16',NULL,'2019-12-16','2024-12-16','RY026','RY026','18777302196','已收监理费11400元.余款10000预计2024年元月到账','2026-03-27 07:49:29.181931','2026-03-27 08:22:55.457126',0,NULL),(64,'engineering_supervision',0,'2021','JL2021','金科·集美江山','completed','executing','unsettled','桂林金科永润房地产开发需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',1279000.00,'0',0.00,0.00,'130000㎡',NULL,'','','2022-08-18','--','','incomplete','','yes','','2021-05-21',NULL,'2021-05-21','2025-10-25','RY024','RY024','15677318699','','2026-03-27 07:49:29.186531','2026-03-27 08:22:55.474342',0,NULL),(65,'engineering_supervision',0,'2058','JL2058','中南大学湘雅二医院桂林医院国家区域医疗中心建设项目（一期）','completed','executing','unsettled','中南大学湘雅二医院桂林医院','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',3080000.00,'0',0.00,0.00,'143375.36㎡',43000.00,'桂林市临桂区','','2023-12-13','--','','incomplete','','yes','',NULL,NULL,NULL,NULL,'','RY039','13558131558','预计2024.2月30日竣工','2026-03-27 07:49:29.308909','2026-03-27 08:22:55.675285',0,NULL),(66,'engineering_supervision',1,'2063','JL2063','燕林学府','under_construction','executing','unsettled','桂林市雁兴房地产开发需要限责任公司','广西鼎策工程顾问需要限责任公司',NULL,'',508819.91,'0',330019.34,178800.57,'1#-3#、5#-7#楼及地下室，总建筑面积49522.71平方米(其中总计容建\n筑面积37810平方米，不计容建筑面积：11712.71平方米),其中地下室总计建筑面积： 11576.53平方米，地下人防建筑面积约1566.49平方米。',11008.38,'桂林市雁山区雁中路以北，雁山科教园 A 片规划区域内','4',NULL,'--','','incomplete','','yes','','2023-03-09','2025-02-28','2025-02-28','2026-07-09','','RY042','','','2026-03-27 07:49:29.318775','2026-03-27 08:22:55.703418',0,NULL),(67,'engineering_supervision',0,'2069','JL2069','陆军学院象山幼儿园及北区改造项目','completed','executing','unsettled','0','0',NULL,'',0.00,'0',200000.00,-200000.00,'0',NULL,'','',NULL,'','','incomplete','','yes','','2021-05-21',NULL,NULL,'2025-06-08','RY024','RY024','15677318699','','2026-03-27 08:01:07.197586','2026-03-27 08:22:55.742228',0,NULL),(68,'engineering_supervision',0,'1002','JL1002','桂林市临桂区革命烈士纪念碑维修工程','completed','executing','unsettled','桂林市临桂区退役军人事务局','广西晟昌工程科技需要限责任公司',NULL,'https://kdocs.cn/l/cl1ItnlfMv8t',7200.00,'--',2332.00,4868.00,'工程总造价442412.00元',44.24,'桂林市临桂区','','2023-11-30','','','incomplete','','yes','','2022-05-05',NULL,'2022-04-22','2024-08-22','RY038','RY039','13558131558','已收监理费6048元','2026-03-27 08:22:55.297444','2026-03-27 08:22:55.297463',0,NULL),(69,'engineering_supervision',0,'1011','JL1011','桂林市公安局新城派出所及110巡警大队业务技术用房1#楼(综合办公楼)装修改造项目','completed','executing','unsettled','桂林市公安局临桂分局','广西晟昌工程科技需要限责任公司',NULL,'https://kdocs.cn/l/chmAAjOFyO2X',105600.00,'0',0.00,105600.00,'㎡',670.00,'桂林市临桂区','',NULL,'','','incomplete','','yes','','2021-06-21',NULL,'2021-05-01','2024-06-20','RY026','RY026','','','2026-03-27 08:22:55.352008','2026-03-27 08:22:55.352027',0,NULL),(70,'engineering_supervision',0,'2001','JL2001','2015年中国联通广西桂林通信枢纽楼新建工程','completed','executing','unsettled','中国联合网络通信需要限公司桂林市分公司','广西晟昌工程科技需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',967803.00,'--',827645.65,140157.35,'14000㎡',5410.65,'桂磨路南侧，铁山工业园Z-2-2地块','','2020-06-15','','','incomplete','','yes','','2020-02-27',NULL,'2020-02-27','2023-11-18','','RY036','17376157123','','2026-03-27 08:22:55.358129','2026-03-27 08:22:55.358148',0,NULL),(71,'engineering_supervision',0,'2002','JL2002','安厦·西宸源著2号地块16#、17#、18#、19#楼、地下室2期项目','completed','executing','unsettled','桂林临桂金地房地产开发需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',2385552.26,'0',5.00,2385547.26,'60644.75',NULL,'','','2020-06-15','','','incomplete','','yes','','2022-09-27',NULL,'2022-09-15','2024-02-29','RY003','RY033','17376157123','监理费41000元已开票，预计2024年元月到账','2026-03-27 08:22:55.363732','2026-03-27 08:22:55.363752',0,NULL),(72,'engineering_supervision',0,'2008','JL2008','防城港市彰泰观江海','completed','executing','unsettled','彰泰集团','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',6495262.80,'0',1064245.50,5431017.30,'281541.87㎡',NULL,'','',NULL,'','','incomplete','','yes','','2019-03-26',NULL,'2019-08-01','2023-11-10','RY003','RY027','','','2026-03-27 08:22:55.398030','2026-03-27 08:22:55.398048',0,NULL),(73,'engineering_supervision',0,'2010','JL2010','枫林·农贸市场','completed','executing','unsettled','桂林广厦房地产开发需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',948380.00,'0',0.00,0.00,'79000㎡',NULL,'','',NULL,'','','incomplete','','yes','','2023-10-31',NULL,'2023-10-31','2024-05-30','RY027','RY027','15977444154','','2026-03-27 08:22:55.410088','2026-03-27 08:22:55.410105',0,NULL),(74,'engineering_supervision',0,'2011','JL2011','凤鸣湖生态环境保护和修复工程——水环境综合治理项目（内源治理）','completed','executing','unsettled','桂林经开投资控股需要限责任公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',257639.00,'0',0.00,0.00,'本项目为对凤鸣湖水环境进行综合治理，需整改雨污混接2处，新增污水管53米，清理生活垃圾5吨，清理建筑垃圾4800立方米；疏浚总面积26325平方米；铺设砾石滤床28815立方米；布置生态曝气浮床40处；种植生态隔离带植物40796平方米，种植水生植物50569平方米；建设生态滞留槽2362米，投放鱼类、虾类、螺类等',2146.32,'桂林经济技术开发区苏桥园区','',NULL,'','','incomplete','','yes','','2022-05-05',NULL,'2022-04-22','2024-08-22','RY038','RY039','13558131558','','2026-03-27 08:22:55.416063','2026-03-27 08:22:55.416081',0,NULL),(75,'engineering_supervision',0,'2012','JL2012','高铁园外国语学校','completed','executing','unsettled','桂林湘楠教育投资管理咨询需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',300000.00,'0',451729.78,-151729.78,'36108.21㎡',NULL,'','',NULL,'','','incomplete','','yes','','2020-02-27',NULL,'2020-02-27','2024-06-30','RY028','RY028','18777302196','合同监理费申请方永明哪边负责。','2026-03-27 08:22:55.422336','2026-03-27 08:22:55.422355',0,NULL),(76,'engineering_supervision',0,'2013','JL2013','桂林市电子商城6#、7#楼及6#、7#楼地下室','completed','executing','unsettled','桂林极佳房地产','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',558674.86,'--',451729.78,106945.08,'63485.59㎡',11215.76,'桂林市临桂区临苏路','','2021-08-30','','','incomplete','','yes','','2022-08-29',NULL,'2022-08-20','2024-04-30','RY003','RY033','13877353395','本项目投资约320万元，按收费标准计费：320*3.3%=10.56万元，按60%优惠计取，\n即10.56万元*60%=6.336万元','2026-03-27 08:22:55.428580','2026-03-27 08:22:55.428599',0,NULL),(77,'engineering_supervision',1,'2019','JL2019','国投桂林院子全过程工程咨询服务','under_construction','executing','unsettled','桂林市朗盛置业需要限责任公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',3348700.00,'0',2800000.00,548700.00,'156213㎡',NULL,'','','2023-11-22','','','incomplete','','yes','','2019-06-01','2019-06-01','2019-06-01','2024-12-16','RY026','RY026','','','2026-03-27 08:22:55.463044','2026-03-27 08:22:55.463061',0,NULL),(78,'engineering_supervision',0,'2020','JL2020','金科·集美东方(C-7)地块二标段及幼儿园','completed','executing','unsettled','桂林真龙房地产开发需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',1180000.00,'0',0.00,0.00,'120000㎡',NULL,'','','2023-04-01','','','incomplete','','yes','',NULL,NULL,'2019-08-01',NULL,'RY003','RY027','','','2026-03-27 08:22:55.469052','2026-03-27 08:22:55.469069',0,NULL),(79,'engineering_supervision',0,'2027','JL2027','临桂区两江镇渡头村优质稻产业基地路硬化','completed','executing','unsettled','桂林市临桂区两江镇人民政府','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',21186.00,'0',1237000.00,-1215814.00,'0',NULL,'','','2023-08-01','','','incomplete','','yes','','2023-08-30',NULL,'2023-08-31','2024-11-28','RY003','RY022','13152582589','','2026-03-27 08:22:55.507836','2026-03-27 08:22:55.507854',0,NULL),(80,'engineering_supervision',0,'2028','JL2028','临桂区乡村风貌提升项目（五通、两江）','completed','executing','unsettled','桂林市临桂区名冠产业投资需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',616608.00,'0',1237000.00,-620392.00,'0',NULL,'','',NULL,'','','incomplete','','yes','',NULL,NULL,'2022-08-20',NULL,'RY003','RY033','13877353395','12月12日项目复工，建设单位名称变更为桂林同方泓嘉科技需要限公司','2026-03-27 08:22:55.513767','2026-03-27 08:22:55.513785',0,NULL),(81,'engineering_supervision',0,'2029','JL2029','临桂秧塘工业园十六路建设工程','completed','executing','unsettled','兴临城投','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',281400.00,'0',1237000.00,-955600.00,'0',NULL,'','',NULL,'','','incomplete','','yes','',NULL,NULL,'2019-03-27',NULL,'RY003','RY037','15977444154','','2026-03-27 08:22:55.519519','2026-03-27 08:22:55.519535',0,NULL),(82,'engineering_supervision',0,'2034','JL2034','龙象二路道路建设项目','completed','executing','unsettled','桂林兴象投资开发需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://www.kdocs.cn/l/cg4gXCjui1cz',13800.00,'--',11956.30,1843.70,'道路全长79米，红线宽12米，城市支路',111.00,'桂林市象山区凯风路2号','',NULL,'','','incomplete','','yes','','2021-06-21',NULL,NULL,'2024-06-21','RY026','RY026','','','2026-03-27 08:22:55.548111','2026-03-27 08:22:55.548131',0,NULL),(83,'engineering_supervision',0,'2035','JL2035','年产600万条集装箱袋生产项目科研楼、1#标准厂房、2#标准厂房、3#标准厂房','completed','executing','unsettled','桂林祺润矿业需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',66670.00,'--',11956.30,54713.70,'6667㎡',800.00,'乐和工业园','','2023-06-30','','','incomplete','','yes','',NULL,NULL,NULL,NULL,'RY026','RY026','','','2026-03-27 08:22:55.553831','2026-03-27 08:22:55.553850',0,NULL),(84,'engineering_supervision',0,'2047','JL2047','翔鹏.幸福家苑','completed','executing','unsettled','桂林翔鹏房地产开发需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',360000.00,'0',0.00,0.00,'37000㎡',NULL,'','','2022-06-01','','','incomplete','','no','',NULL,NULL,NULL,NULL,'','','','','2026-03-27 08:22:55.617221','2026-03-27 08:22:55.617236',0,NULL),(85,'engineering_supervision',0,'2050','JL2050','新兴领域特种电线电缆技术升级改造1号厂房','completed','executing','unsettled','桂林国际电缆厂','广西鼎策工程顾问需要限责任公司',NULL,'https://www.kdocs.cn/l/cp1UWApmKapp',161146.00,'--',0.00,161146.00,'11613㎡',NULL,'桂林市七星区英才科技园','',NULL,'','','incomplete','','no','',NULL,NULL,NULL,NULL,'','','','','2026-03-27 08:22:55.632823','2026-03-27 08:22:55.632842',0,NULL),(86,'engineering_supervision',0,'2052','JL2052','兴进漓江悦府','completed','executing','unsettled','桂林兴祺房地产开发需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://kdocs.cn/join/gflobs0?f=101',2311285.18,'0',2249810.96,61474.22,'208205㎡',NULL,'','','2022-08-31','','','incomplete','','no','',NULL,NULL,NULL,NULL,'','','','','2026-03-27 08:22:55.643902','2026-03-27 08:22:55.643915',0,NULL),(87,'engineering_supervision',0,'2060','JL2060','桂林市清风实验学校北片地块D-10-1地块二、三期','completed','executing','unsettled','桂林市兴进投资发展需要限公司','广西鼎策工程顾问需要限责任公司',NULL,'https://www.kdocs.cn/l/ciQYMEOQGXUp',2017258.10,'--',669386.36,1347871.74,'建筑面积约201725.81㎡（其中：地上建筑面积约153404.39㎡，地下室建筑面积约48321.42㎡）',27000.00,'叠彩区滨江北路以西，芳华路以南，江与城小区以北，叠彩万达广场以南','',NULL,'','','incomplete','','no','',NULL,NULL,NULL,NULL,'','','','','2026-03-27 08:22:55.686630','2026-03-27 08:22:55.686647',0,NULL),(88,'engineering_supervision',0,'2061','JL2061','桂林信息科技学院项目一期三批及二期一批次建设工程监理服务','completed','executing','unsettled','桂林信息科技学院','广西鼎策工程顾问需要限责任公司',NULL,'',801188.46,'0',0.00,0.00,'116114 .27㎡',NULL,'桂林市临桂区临桂镇庙岭村大山图公路以南','',NULL,'','','incomplete','','no','',NULL,NULL,NULL,NULL,'','','','','2026-03-27 08:22:55.692171','2026-03-27 08:22:55.692186',0,NULL),(89,'engineering_supervision',0,'2062','JL2062','奇峰纸业','completed','executing','unsettled','0','0',NULL,'https://kdocs.cn/join/gflobs0?f=101',0.00,'0',13300.25,-13300.25,'0',17000.00,'世纪大道以北、西城大道以东','','2023-06-06','','','incomplete','','no','',NULL,NULL,NULL,NULL,'','','','','2026-03-27 08:22:55.697897','2026-03-27 08:22:55.697914',0,NULL),(91,'engineering_supervision',1,'2067','JL2067','兴安县城市公益性公墓项目','under_construction','executing','unsettled','桂林鑫溶投资需要限公司','0',NULL,'',0.00,'0',2.00,-2.00,'0',NULL,'','',NULL,'','','incomplete','','no','','2026-03-28','2026-03-28','2026-03-28',NULL,'','','','','2026-03-27 08:22:55.731325','2026-03-27 08:22:55.731341',0,NULL),(92,'engineering_supervision',0,'2068','JL2068','陆军学院老旧小区改造项目','completed','executing','unsettled','0','广西鼎策工程顾问需要限责任公司',NULL,'',88000.00,'0',4.00,87996.00,'0',NULL,'','',NULL,'','','incomplete','','no','','2026-03-05','2026-03-06','2026-03-10','2026-10-28','','','','','2026-03-27 08:22:55.737077','2026-03-27 08:22:55.737094',0,NULL),(93,'engineering_supervision',1,'2071','JL2071','高铁园','not_started','executing','unsettled','广西鼎策工程顾问有限责任公司','广西灵川八里街工业园区开发总公司','2026-03-30','',200000.00,'',0.00,0.00,'',NULL,'','',NULL,'','','incomplete','','no','',NULL,NULL,NULL,NULL,'','','','','2026-03-29 16:09:09.121863','2026-03-29 18:25:34.264156',0,NULL),(94,'engineering_supervision',1,'2072','JL2072','湘江壹号小区一期、二期公区消防设施设备全面整改项目','not_started','executing','unsettled','广西同城炜烨后勤管理服务集团有限公司','广西鼎策工程顾问有限责任公司','2026-03-30','',20000.00,'',0.00,0.00,'',NULL,'广西桂林市全州县湘江壹号小区内','',NULL,'','','incomplete','','no','',NULL,NULL,NULL,NULL,'','','','','2026-03-29 18:31:27.387133','2026-03-29 18:31:27.387152',0,NULL),(95,'engineering_supervision',1,'HT20260405002212','HT-20260405-5','月球登录工程','not_started','executing','unsettled','宇宙建设有限公司','广西晟昌','2025-10-07','',510000.00,'',0.00,0.00,'',123000000.00,'','',NULL,'','','incomplete','','no','',NULL,NULL,NULL,NULL,'','','','来自审批：4.','2026-04-04 16:22:12.237449','2026-04-07 03:54:36.302228',4,NULL),(96,'engineering_supervision',1,'HT20260405140722','HT-20260405-6','55','not_started','pending_review','unsettled','55','55',NULL,'',55.00,'',360000.00,-359945.00,'',NULL,'','',NULL,'','','incomplete','','no','','2026-04-25','2026-04-30','2026-04-16','2026-04-30','','','','来自审批：55. ','2026-04-05 06:07:22.868848','2026-04-05 06:07:22.868862',5,NULL),(97,'engineering_supervision',1,'HT20260405232807','HT-20260405-2','特高压电抗器生产线建设项目工程监理','not_started','pending_review','unsettled','桂林五环电器制造有限公司','华建嘉质建设有限公司',NULL,'',155900.00,'',0.00,155900.00,'',NULL,'','',NULL,'','','incomplete','','no','','2026-03-20','2026-03-20','2026-04-15','2027-02-15','','','','来自审批：桂林五环电器制造有限公司特高压电抗器生产线建设项目工程监理. 请王总审批','2026-04-05 15:28:07.132452','2026-04-05 15:28:07.132465',10,NULL);
/*!40000 ALTER TABLE `eims_app_projectdetail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_projectdynamic`
--

DROP TABLE IF EXISTS `eims_app_projectdynamic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_projectdynamic` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `project_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_progress` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notice_entry` date DEFAULT NULL,
  `delay_status` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `planned_start_time` date DEFAULT NULL,
  `actual_start_time` date DEFAULT NULL,
  `planned_completion` date DEFAULT NULL,
  `personnel_change` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `operator` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `project_id` bigint DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_projectdynamic_project_code_14c98beb` (`project_code`),
  KEY `eims_app_projectdyna_project_id_4bd1c10d_fk_eims_app_` (`project_id`),
  CONSTRAINT `eims_app_projectdyna_project_id_4bd1c10d_fk_eims_app_` FOREIGN KEY (`project_id`) REFERENCES `eims_app_projectdetail` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_projectdynamic`
--

LOCK TABLES `eims_app_projectdynamic` WRITE;
/*!40000 ALTER TABLE `eims_app_projectdynamic` DISABLE KEYS */;
INSERT INTO `eims_app_projectdynamic` VALUES (9,'2068','1','not_started','2026-03-05','1','2026-03-06','2026-03-10','2026-10-28','','admin','','2026-03-27 22:04:52.985878','2026-03-27 22:04:52.985889',92,0),(10,'2067','33','normal_construction','2026-03-28','','2026-03-28','2026-03-28',NULL,'','admin','','2026-03-27 22:22:42.529485','2026-03-27 22:22:42.529494',91,0),(11,'2067','33','normal_construction','2026-03-28','','2026-03-28','2026-03-28',NULL,'','黎绍昆','','2026-03-28 01:48:37.627693','2026-03-28 01:48:37.627706',91,0),(12,'2063','项目正常推进中','normal_construction','2023-03-09','','2025-02-28','2025-02-28','2026-07-09','','admin','','2026-03-28 06:55:58.181311','2026-03-28 03:16:04.361709',66,0),(13,'HT20260405140722','完成80%','normal_construction','2026-04-25','','2026-04-30','2026-04-16','2026-04-30','','黎绍昆','','2026-04-06 22:57:03.428656','2026-04-06 22:57:03.428667',96,0),(14,'HT20260405140722','完成80%','normal_construction','2026-04-25','','2026-04-30','2026-04-16','2026-04-30','','黎绍昆','','2026-04-06 23:16:11.501899','2026-04-06 23:16:11.501910',96,0),(15,'HT20260405140722','完成80%','stopped','2026-04-25','','2026-04-30','2026-04-16','2026-04-30','','黎绍昆','','2026-04-06 23:16:31.345951','2026-04-06 23:16:31.345963',96,0),(16,'HT20260405232807','已完成地基处理','stopped','2026-03-20','','2026-03-20','2026-04-15','2027-02-15','','黎绍昆','','2026-04-07 05:06:00.856112','2026-04-07 05:06:00.856130',97,0),(17,'HT20260405232807','已完成地基处理','stopped','2026-03-20','','2026-03-20','2026-04-15','2027-02-15','','黎绍昆','','2026-04-07 05:07:46.352169','2026-04-07 05:07:46.352185',97,0),(18,'2019','所有外架已拆除','normal_construction','2019-06-01','','2019-06-01','2019-06-01','2024-12-16','','王璐','','2026-04-07 05:25:32.355900','2026-04-07 05:25:32.355922',77,0),(19,'HT20260405140722','完成80%','completed','2026-04-25','','2026-04-30','2026-04-16','2026-04-30','','王璐','','2026-04-07 06:44:17.817475','2026-04-07 06:44:17.817487',96,0),(20,'HT20260405232807','已完成地基处理','stopped','2026-03-20','','2026-03-20','2026-04-15','2027-02-15','','王璐','','2026-04-07 07:35:43.381350','2026-04-07 07:35:43.381368',97,0),(21,'HT20260405232807','已完成地基处理','normal_construction','2026-03-20','','2026-03-20','2026-04-15','2027-02-15','','王璐','','2026-04-07 07:36:12.188972','2026-04-07 07:36:12.188982',97,0),(22,'HT20260405140722','完成80%','completed','2026-04-25','','2026-04-30','2026-04-16','2026-04-30','','黎绍昆','','2026-04-07 14:14:51.016496','2026-04-07 14:14:51.016507',96,0),(23,'HT20260405140722','完成82%','completed','2026-04-25','','2026-04-30','2026-04-16','2026-04-30','','黎绍昆','','2026-04-07 14:19:03.339233','2026-04-07 14:19:03.339245',96,0),(24,'HT20260405140722','完成82%','completed','2026-04-25','','2026-04-30','2026-04-16','2026-04-30','','秦养付','','2026-04-07 14:42:54.451343','2026-04-07 14:42:54.451352',96,0),(25,'HT20260405140722','完成82%','completed','2026-04-25','','2026-04-30','2026-04-16','2026-04-30','','秦养付','','2026-04-07 15:11:45.394245','2026-04-07 15:11:45.394261',96,0);
/*!40000 ALTER TABLE `eims_app_projectdynamic` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_projectreporter`
--

DROP TABLE IF EXISTS `eims_app_projectreporter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_projectreporter` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `report_period` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `project_id` bigint NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `eims_app_projectreporter_user_id_project_id_dca3996b_uniq` (`user_id`,`project_id`),
  KEY `eims_app_projectrepo_project_id_8e1d13d6_fk_eims_app_` (`project_id`),
  CONSTRAINT `eims_app_projectrepo_project_id_8e1d13d6_fk_eims_app_` FOREIGN KEY (`project_id`) REFERENCES `eims_app_projectdetail` (`id`),
  CONSTRAINT `eims_app_projectreporter_user_id_f72c9860_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_projectreporter`
--

LOCK TABLES `eims_app_projectreporter` WRITE;
/*!40000 ALTER TABLE `eims_app_projectreporter` DISABLE KEYS */;
/*!40000 ALTER TABLE `eims_app_projectreporter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_projectrole`
--

DROP TABLE IF EXISTS `eims_app_projectrole`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_projectrole` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `is_active` tinyint(1) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `project_id` bigint NOT NULL,
  `user_id` int NOT NULL,
  `role_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `eims_app_projectrole_user_id_project_id_role_id_8ab28818_uniq` (`user_id`,`project_id`,`role_id`),
  KEY `eims_app_projectrole_role_id_241b41f7_fk_eims_app_role_id` (`role_id`),
  KEY `eims_app_projectrole_project_id_3e13b9a5_fk_eims_app_` (`project_id`),
  CONSTRAINT `eims_app_projectrole_project_id_3e13b9a5_fk_eims_app_` FOREIGN KEY (`project_id`) REFERENCES `eims_app_projectdetail` (`id`),
  CONSTRAINT `eims_app_projectrole_role_id_241b41f7_fk_eims_app_role_id` FOREIGN KEY (`role_id`) REFERENCES `eims_app_role` (`id`),
  CONSTRAINT `eims_app_projectrole_user_id_29b99657_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_projectrole`
--

LOCK TABLES `eims_app_projectrole` WRITE;
/*!40000 ALTER TABLE `eims_app_projectrole` DISABLE KEYS */;
/*!40000 ALTER TABLE `eims_app_projectrole` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_qrcodeloginsession`
--

DROP TABLE IF EXISTS `eims_app_qrcodeloginsession`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_qrcodeloginsession` (
  `session_id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `scanned_at` datetime(6) DEFAULT NULL,
  `confirmed_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `ip_address` char(39) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `extra_data` json NOT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`session_id`),
  KEY `eims_app_qrcodeloginsession_user_id_f589e34d_fk_auth_user_id` (`user_id`),
  KEY `eims_app_qr_session_b10af3_idx` (`session_id`,`status`),
  KEY `eims_app_qr_expires_b2afeb_idx` (`expires_at`),
  CONSTRAINT `eims_app_qrcodeloginsession_user_id_f589e34d_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_qrcodeloginsession`
--

LOCK TABLES `eims_app_qrcodeloginsession` WRITE;
/*!40000 ALTER TABLE `eims_app_qrcodeloginsession` DISABLE KEYS */;
INSERT INTO `eims_app_qrcodeloginsession` VALUES ('c8a9b1c23ba148dbbf55095d47c35350','pending',NULL,NULL,'2026-04-05 00:09:07.159174','2026-04-04 23:59:07.160410','127.0.0.1','\"{}\"',NULL);
/*!40000 ALTER TABLE `eims_app_qrcodeloginsession` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_role`
--

DROP TABLE IF EXISTS `eims_app_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_role` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `permissions` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_role`
--

LOCK TABLES `eims_app_role` WRITE;
/*!40000 ALTER TABLE `eims_app_role` DISABLE KEYS */;
INSERT INTO `eims_app_role` VALUES (1,'super_admin','拥有系统所有权限','view,edit,submit'),(2,'system_admin','拥有系统管理权限','view,edit,submit'),(3,'project_director','负责项目整体管理和最终审核','view,edit,submit'),(4,'director_rep','协助总监工作，可初审','view,edit,submit'),(5,'supervisor','现场监理，发起填报','view,edit,submit'),(6,'data_clerk','负责资料管理，发起填报','view,edit,submit'),(7,'initiator','普通发起人员','view,edit,submit');
/*!40000 ALTER TABLE `eims_app_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_sealapproval`
--

DROP TABLE IF EXISTS `eims_app_sealapproval`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_sealapproval` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `initiation_time` datetime(6) DEFAULT NULL,
  `seal_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `seal_count` int NOT NULL,
  `document_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `document_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `usage_purpose` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `approval_flow_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `approval_level` int NOT NULL,
  `max_approval_level` int NOT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `submitted_at` datetime(6) DEFAULT NULL,
  `approved_at` datetime(6) DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  `deleted_at` datetime(6) DEFAULT NULL,
  `applicant_id` int DEFAULT NULL,
  `auto_assigned_approver_id` int DEFAULT NULL,
  `current_approver_id` int DEFAULT NULL,
  `department_id` bigint DEFAULT NULL,
  `initiator_id` int DEFAULT NULL,
  `selected_approver_id` int DEFAULT NULL,
  `selected_department_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_sealapproval_applicant_id_aee11b19_fk_auth_user_id` (`applicant_id`),
  KEY `eims_app_sealapprova_auto_assigned_approv_d02f66b1_fk_auth_user` (`auto_assigned_approver_id`),
  KEY `eims_app_sealapprova_current_approver_id_a524e191_fk_auth_user` (`current_approver_id`),
  KEY `eims_app_sealapprova_department_id_f54a611d_fk_eims_app_` (`department_id`),
  KEY `eims_app_sealapproval_initiator_id_300e49b0_fk_auth_user_id` (`initiator_id`),
  KEY `eims_app_sealapprova_selected_approver_id_22023367_fk_auth_user` (`selected_approver_id`),
  KEY `eims_app_sealapprova_selected_department__06a3c16b_fk_eims_app_` (`selected_department_id`),
  CONSTRAINT `eims_app_sealapprova_auto_assigned_approv_d02f66b1_fk_auth_user` FOREIGN KEY (`auto_assigned_approver_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_sealapprova_current_approver_id_a524e191_fk_auth_user` FOREIGN KEY (`current_approver_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_sealapprova_department_id_f54a611d_fk_eims_app_` FOREIGN KEY (`department_id`) REFERENCES `eims_app_department` (`id`),
  CONSTRAINT `eims_app_sealapprova_selected_approver_id_22023367_fk_auth_user` FOREIGN KEY (`selected_approver_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_sealapprova_selected_department__06a3c16b_fk_eims_app_` FOREIGN KEY (`selected_department_id`) REFERENCES `eims_app_department` (`id`),
  CONSTRAINT `eims_app_sealapproval_applicant_id_aee11b19_fk_auth_user_id` FOREIGN KEY (`applicant_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_sealapproval_initiator_id_300e49b0_fk_auth_user_id` FOREIGN KEY (`initiator_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_sealapproval`
--

LOCK TABLES `eims_app_sealapproval` WRITE;
/*!40000 ALTER TABLE `eims_app_sealapproval` DISABLE KEYS */;
INSERT INTO `eims_app_sealapproval` VALUES (1,'请款盖章','2026-04-07 11:50:58.896337','other',4,'燕林学府监理请款资料','','','','请款','pending','user_selected',1,2,'','2026-04-07 11:50:45.762406','2026-04-07 11:50:58.896398','2026-04-07 11:50:58.896318',NULL,0,NULL,3,NULL,NULL,1,3,11,1);
/*!40000 ALTER TABLE `eims_app_sealapproval` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_sealapprovalrecord`
--

DROP TABLE IF EXISTS `eims_app_sealapprovalrecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_sealapprovalrecord` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `comment` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `approval_id` bigint NOT NULL,
  `next_approver_id` int DEFAULT NULL,
  `operator_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_sealapprova_approval_id_85d5580b_fk_eims_app_` (`approval_id`),
  KEY `eims_app_sealapprova_next_approver_id_b0ec816c_fk_auth_user` (`next_approver_id`),
  KEY `eims_app_sealapprovalrecord_operator_id_e5669548_fk_auth_user_id` (`operator_id`),
  CONSTRAINT `eims_app_sealapprova_approval_id_85d5580b_fk_eims_app_` FOREIGN KEY (`approval_id`) REFERENCES `eims_app_sealapproval` (`id`),
  CONSTRAINT `eims_app_sealapprova_next_approver_id_b0ec816c_fk_auth_user` FOREIGN KEY (`next_approver_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `eims_app_sealapprovalrecord_operator_id_e5669548_fk_auth_user_id` FOREIGN KEY (`operator_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_sealapprovalrecord`
--

LOCK TABLES `eims_app_sealapprovalrecord` WRITE;
/*!40000 ALTER TABLE `eims_app_sealapprovalrecord` DISABLE KEYS */;
INSERT INTO `eims_app_sealapprovalrecord` VALUES (1,'submit','提交审批','2026-04-07 11:50:58.903027',1,NULL,3);
/*!40000 ALTER TABLE `eims_app_sealapprovalrecord` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_sealattachment`
--

DROP TABLE IF EXISTS `eims_app_sealattachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_sealattachment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_size` int NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  `approval_id` bigint NOT NULL,
  `uploaded_by_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_sealattachm_approval_id_e0e709ad_fk_eims_app_` (`approval_id`),
  KEY `eims_app_sealattachment_uploaded_by_id_be7ae8c5_fk_auth_user_id` (`uploaded_by_id`),
  CONSTRAINT `eims_app_sealattachm_approval_id_e0e709ad_fk_eims_app_` FOREIGN KEY (`approval_id`) REFERENCES `eims_app_sealapproval` (`id`),
  CONSTRAINT `eims_app_sealattachment_uploaded_by_id_be7ae8c5_fk_auth_user_id` FOREIGN KEY (`uploaded_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_sealattachment`
--

LOCK TABLES `eims_app_sealattachment` WRITE;
/*!40000 ALTER TABLE `eims_app_sealattachment` DISABLE KEYS */;
INSERT INTO `eims_app_sealattachment` VALUES (1,'seal_approvals/2026/04/BC笔记.docx','document','BC笔记.docx',27481,'2026-04-07 11:50:45.768208',0,1,NULL);
/*!40000 ALTER TABLE `eims_app_sealattachment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_smsverificationrecord`
--

DROP TABLE IF EXISTS `eims_app_smsverificationrecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_smsverificationrecord` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `is_deleted` tinyint(1) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `verification_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `verification_code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ip_address` char(39) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_time` datetime(6) NOT NULL,
  `verified_time` datetime(6) DEFAULT NULL,
  `remark` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `eims_app_smsverificationrecord_user_id_ee975cf6_fk_auth_user_id` (`user_id`),
  KEY `eims_app_smsverificationrecord_phone_b38abbeb` (`phone`),
  CONSTRAINT `eims_app_smsverificationrecord_user_id_ee975cf6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_smsverificationrecord`
--

LOCK TABLES `eims_app_smsverificationrecord` WRITE;
/*!40000 ALTER TABLE `eims_app_smsverificationrecord` DISABLE KEYS */;
INSERT INTO `eims_app_smsverificationrecord` VALUES (1,0,'2026-03-29 08:08:49.850149','2026-03-29 08:08:49.850163','18978383227','reset_password','***','success','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','2026-03-29 08:13:49.849869',NULL,'',NULL),(2,0,'2026-03-29 08:16:38.547204','2026-03-29 08:16:38.547221','18978383227','reset_password','***','success','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','2026-03-29 08:21:38.547015',NULL,'',NULL),(3,0,'2026-04-05 00:21:37.008195','2026-04-05 00:21:37.008220','18978383227','reset_password','***','success','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','2026-04-05 00:26:37.007906',NULL,'',NULL),(4,0,'2026-04-05 00:22:53.836141','2026-04-05 00:22:53.836154','18978383227','reset_password','***','success','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','2026-04-05 00:27:53.836005',NULL,'',NULL),(5,0,'2026-04-05 03:41:09.702629','2026-04-05 03:41:09.702644','18978383227','reset_password','***','success','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','2026-04-05 03:46:09.702434',NULL,'',NULL),(6,0,'2026-04-05 04:11:32.479210','2026-04-05 04:11:32.479237','18978383227','reset_password','***','success','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','2026-04-05 04:16:32.478938',NULL,'',NULL);
/*!40000 ALTER TABLE `eims_app_smsverificationrecord` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_userprofile`
--

DROP TABLE IF EXISTS `eims_app_userprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_userprofile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `real_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `gender` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `birthday` date DEFAULT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `wechat` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `eims_app_userprofile_user_id_030bb91f_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_userprofile`
--

LOCK TABLES `eims_app_userprofile` WRITE;
/*!40000 ALTER TABLE `eims_app_userprofile` DISABLE KEYS */;
INSERT INTO `eims_app_userprofile` VALUES (1,'','',NULL,'','',1),(2,'','',NULL,'','',10),(3,'张三','',NULL,'','',17),(4,'黎绍昆','male','1980-09-01','18978383227','',12),(5,'','',NULL,'','',2),(6,'','',NULL,'','',3);
/*!40000 ALTER TABLE `eims_app_userprofile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_wechatqrcodesession`
--

DROP TABLE IF EXISTS `eims_app_wechatqrcodesession`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_wechatqrcodesession` (
  `session_id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `state` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `openid` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `unionid` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `expires_at` datetime(6) NOT NULL,
  `scanned_at` datetime(6) DEFAULT NULL,
  `authorized_at` datetime(6) DEFAULT NULL,
  `ip_address` char(39) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`session_id`),
  UNIQUE KEY `state` (`state`),
  KEY `eims_app_wechatqrcodesession_user_id_24bad2ec_fk_auth_user_id` (`user_id`),
  KEY `eims_app_we_state_a9e8c9_idx` (`state`),
  KEY `eims_app_we_status_bf6e99_idx` (`status`,`expires_at`),
  CONSTRAINT `eims_app_wechatqrcodesession_user_id_24bad2ec_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_wechatqrcodesession`
--

LOCK TABLES `eims_app_wechatqrcodesession` WRITE;
/*!40000 ALTER TABLE `eims_app_wechatqrcodesession` DISABLE KEYS */;
/*!40000 ALTER TABLE `eims_app_wechatqrcodesession` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eims_app_wechatuserbinding`
--

DROP TABLE IF EXISTS `eims_app_wechatuserbinding`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eims_app_wechatuserbinding` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `openid` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `unionid` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nickname` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `headimgurl` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sex` smallint NOT NULL,
  `country` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `province` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `city` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_bound` tinyint(1) NOT NULL,
  `bind_time` datetime(6) NOT NULL,
  `last_login_time` datetime(6) DEFAULT NULL,
  `extra_data` json NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `openid` (`openid`),
  KEY `eims_app_wechatuserbinding_unionid_546ae4d6` (`unionid`),
  KEY `eims_app_we_openid_c1cf12_idx` (`openid`),
  KEY `eims_app_we_unionid_a32803_idx` (`unionid`),
  KEY `eims_app_we_user_id_62f30b_idx` (`user_id`,`is_bound`),
  CONSTRAINT `eims_app_wechatuserbinding_user_id_cf3bc5ee_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eims_app_wechatuserbinding`
--

LOCK TABLES `eims_app_wechatuserbinding` WRITE;
/*!40000 ALTER TABLE `eims_app_wechatuserbinding` DISABLE KEYS */;
/*!40000 ALTER TABLE `eims_app_wechatuserbinding` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed
