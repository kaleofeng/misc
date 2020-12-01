/*
 Navicat Premium Data Transfer

 Source Server         : L Venus - 192.168.31.102
 Source Server Type    : MySQL
 Source Server Version : 80011
 Source Host           : 192.168.31.102:3306
 Source Schema         : album

 Target Server Type    : MySQL
 Target Server Version : 80011
 File Encoding         : 65001

 Date: 12/12/2018 22:05:57
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for tab_album_total
-- ----------------------------
DROP TABLE IF EXISTS `tab_album_total`;
CREATE TABLE `tab_album_total`  (
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
