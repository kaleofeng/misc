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

 Date: 18/12/2018 21:49:10
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for tab_qmusic_singerstat
-- ----------------------------
DROP TABLE IF EXISTS `tab_qmusic_singerstat`;
CREATE TABLE `tab_qmusic_singerstat`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `sid` int(10) NOT NULL COMMENT '歌手ID',
  `sname` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '歌手名称',
  `today_persons` int(10) NOT NULL COMMENT '今日助燃人数',
  `total_persons` int(10) NOT NULL COMMENT '总助燃人数',
  `total_albums` int(10) NOT NULL COMMENT '总助燃次数',
  `time` int(10) NOT NULL COMMENT '时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
