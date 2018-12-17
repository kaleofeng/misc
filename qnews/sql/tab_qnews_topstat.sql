/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50720
Source Host           : localhost:3306
Source Database       : album

Target Server Type    : MYSQL
Target Server Version : 50720
File Encoding         : 65001

Date: 2018-12-12 18:20:17
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for tab_qnews_topstat
-- ----------------------------
DROP TABLE IF EXISTS `tab_qnews_topstat`;
CREATE TABLE `tab_qnews_topstat` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `sid` int(10) NOT NULL COMMENT '明星ID',
  `sname` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '明星名称',
  `total` int(10) NOT NULL COMMENT '总量',
  `time` int(10) NOT NULL COMMENT '时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
