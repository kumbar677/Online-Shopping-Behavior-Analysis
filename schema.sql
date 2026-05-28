-- DataSense.AI - Database Schema
-- Run this file to create all required tables:
--   mysql -u root -p shopping_analysis < schema.sql

CREATE DATABASE IF NOT EXISTS shopping_analysis;
USE shopping_analysis;

-- 1. businesses (no dependencies)
CREATE TABLE IF NOT EXISTS `businesses` (
  `business_id` int NOT NULL AUTO_INCREMENT,
  `company_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `logo_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`business_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 2. datasets (depends on businesses)
CREATE TABLE IF NOT EXISTS `datasets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `business_id` int NOT NULL,
  `dataset_name` varchar(255) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'processing',
  `is_deleted` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `total_rows` int DEFAULT '0',
  `inserted_rows` int DEFAULT '0',
  `failed_rows` int DEFAULT '0',
  `processing_time` float DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_datasets_deleted` (`is_deleted`),
  KEY `idx_datasets_business` (`business_id`),
  CONSTRAINT `datasets_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`business_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 3. users (depends on businesses, datasets)
CREATE TABLE IF NOT EXISTS `users` (
  `user_id` varchar(100) NOT NULL,
  `business_id` int NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `age` int DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `dataset_id` int DEFAULT NULL,
  PRIMARY KEY (`business_id`,`user_id`),
  KEY `idx_users_business` (`business_id`),
  KEY `dataset_id` (`dataset_id`),
  KEY `idx_user_analytics` (`business_id`,`country`,`gender`,`age`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`business_id`) ON DELETE CASCADE,
  CONSTRAINT `users_ibfk_2` FOREIGN KEY (`dataset_id`) REFERENCES `datasets` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 4. products (depends on businesses, datasets)
CREATE TABLE IF NOT EXISTS `products` (
  `product_id` varchar(100) NOT NULL,
  `business_id` int NOT NULL,
  `product_name` varchar(100) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `brand` varchar(100) DEFAULT NULL,
  `discount` decimal(5,2) DEFAULT NULL,
  `dataset_id` int DEFAULT NULL,
  PRIMARY KEY (`business_id`,`product_id`),
  KEY `idx_products_business` (`business_id`),
  KEY `dataset_id` (`dataset_id`),
  KEY `idx_product_analytics` (`business_id`,`category`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`business_id`) ON DELETE CASCADE,
  CONSTRAINT `products_ibfk_2` FOREIGN KEY (`dataset_id`) REFERENCES `datasets` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 5. orders (depends on businesses, users, products, datasets)
CREATE TABLE IF NOT EXISTS `orders` (
  `order_id` varchar(100) NOT NULL,
  `business_id` int NOT NULL,
  `user_id` varchar(100) DEFAULT NULL,
  `product_id` varchar(100) NOT NULL,
  `quantity` int DEFAULT NULL,
  `order_date` date DEFAULT NULL,
  `total_amount` decimal(10,2) DEFAULT NULL,
  `payment_method` varchar(50) DEFAULT NULL,
  `order_status` varchar(50) DEFAULT NULL,
  `dataset_id` int DEFAULT NULL,
  PRIMARY KEY (`business_id`,`order_id`,`product_id`),
  KEY `business_id` (`business_id`,`user_id`),
  KEY `business_id_2` (`business_id`,`product_id`),
  KEY `idx_orders_date` (`order_date`),
  KEY `idx_orders_business_date` (`business_id`,`order_date`),
  KEY `idx_orders_dataset` (`dataset_id`),
  KEY `idx_orders_business_dataset` (`business_id`,`dataset_id`),
  KEY `idx_order_analytics` (`business_id`,`payment_method`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`business_id`) ON DELETE CASCADE,
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`business_id`, `user_id`) REFERENCES `users` (`business_id`, `user_id`) ON DELETE CASCADE,
  CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`business_id`, `product_id`) REFERENCES `products` (`business_id`, `product_id`) ON DELETE CASCADE,
  CONSTRAINT `orders_ibfk_4` FOREIGN KEY (`dataset_id`) REFERENCES `datasets` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 6. password_resets (depends on businesses)
CREATE TABLE IF NOT EXISTS `password_resets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `otp` varchar(6) NOT NULL,
  `expiry_time` datetime NOT NULL,
  `is_used` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_password_resets_email` (`email`),
  CONSTRAINT `fk_pr_business` FOREIGN KEY (`email`) REFERENCES `businesses` (`email`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 7. upload_errors (depends on datasets)
CREATE TABLE IF NOT EXISTS `upload_errors` (
  `id` int NOT NULL AUTO_INCREMENT,
  `dataset_id` int NOT NULL,
  `table_name` varchar(50) DEFAULT NULL,
  `error_row` int DEFAULT NULL,
  `error_message` text,
  `raw_data` varchar(500) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_errors_dataset` (`dataset_id`),
  CONSTRAINT `upload_errors_ibfk_1` FOREIGN KEY (`dataset_id`) REFERENCES `datasets` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
