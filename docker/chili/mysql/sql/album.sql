/*
 Navicat Premium Data Transfer

 Source Server         : local docker
 Source Server Type    : MySQL
 Source Server Version : 80013
 Source Host           : 192.168.31.102:3306
 Source Schema         : album

 Target Server Type    : MySQL
 Target Server Version : 80013
 File Encoding         : 65001

 Date: 25/10/2018 23:08:00
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for album_today
-- ----------------------------
DROP TABLE IF EXISTS `album_today`;
CREATE TABLE `album_today`  (
  `singer` int(11) NOT NULL COMMENT '歌手',
  `rank` int(11) NOT NULL COMMENT '排名',
  `call_num` int(11) NOT NULL COMMENT '购买数量',
  `uin` bigint(20) NOT NULL COMMENT 'UIN',
  `nick` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '昵称',
  `pic` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '头像',
  `time` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '时间',
  PRIMARY KEY (`singer`, `rank`, `time`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for album_total
-- ----------------------------
DROP TABLE IF EXISTS `album_total`;
CREATE TABLE `album_total`  (
  `singer` int(11) NOT NULL COMMENT '歌手',
  `rank` int(11) NOT NULL COMMENT '排名',
  `call_num` int(11) NOT NULL COMMENT '购买数量',
  `uin` bigint(20) NOT NULL COMMENT 'UIN',
  `nick` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '昵称',
  `pic` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '头像',
  `time` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '时间',
  PRIMARY KEY (`singer`, `rank`, `time`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
