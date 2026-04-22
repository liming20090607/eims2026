-- ============================================
-- Multi-System Database Creation Script
-- Creates 4 independent databases for the multi-system architecture
-- ============================================

-- Create database for 广西鼎策工程顾问有限责任公司
CREATE DATABASE IF NOT EXISTS eims_dingce 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Create database for 广西晟昌工程科技有限责任公司
CREATE DATABASE IF NOT EXISTS eims_shengchang 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Create database for 广西嘉诚达工程造价咨询有限公司
CREATE DATABASE IF NOT EXISTS eims_jiachengda 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Create database for root admin backend
CREATE DATABASE IF NOT EXISTS eims_root 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Show all created databases
SHOW DATABASES LIKE 'eims_%';
