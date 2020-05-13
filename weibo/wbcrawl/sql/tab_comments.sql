/*
 Navicat Premium Data Transfer

 Source Server         : L P cent - cent.metazion.int
 Source Server Type    : MySQL
 Source Server Version : 80013
 Source Host           : cent.metazion.int:3306
 Source Schema         : tool

 Target Server Type    : MySQL
 Target Server Version : 80013
 File Encoding         : 65001

 Date: 13/05/2020 22:05:52
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for tab_comments
-- ----------------------------
DROP TABLE IF EXISTS `tab_comments`;
CREATE TABLE `tab_comments`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `cid` bigint(20) NOT NULL,
  `ctext` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` int(10) NOT NULL,
  `total_number` int(10) NOT NULL,
  `like_count` int(10) NOT NULL,
  `liked_by_blogger` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `cindex` smallint(5) NOT NULL,
  `post_id` bigint(20) NOT NULL,
  `author_id` bigint(20) NOT NULL,
  `author_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `gender` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `urank` smallint(5) NOT NULL,
  `followers_count` int(10) NOT NULL,
  `follow_count` int(10) NOT NULL,
  `record_time` int(10) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
