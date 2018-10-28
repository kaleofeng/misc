/*
 Navicat Premium Data Transfer

 Source Server         : local docker
 Source Server Type    : MySQL
 Source Server Version : 80013
 Source Host           : 192.168.31.102:3306
 Source Schema         : tool

 Target Server Type    : MySQL
 Target Server Version : 80013
 File Encoding         : 65001

 Date: 25/10/2018 23:08:10
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for tab_bmirecord
-- ----------------------------
DROP TABLE IF EXISTS `tab_bmirecord`;
CREATE TABLE `tab_bmirecord`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `what` int(11) NULL DEFAULT NULL,
  `height` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `factor` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `result` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `ip` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `time` datetime(0) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
