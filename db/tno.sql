-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 16, 2025 at 11:02 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `tno`
--

-- --------------------------------------------------------

--
-- Table structure for table `chat_messages`
--

CREATE TABLE `chat_messages` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `chat_messages`
--

INSERT INTO `chat_messages` (`id`, `user_id`, `message`, `timestamp`) VALUES
(1, 8, 'asdasd', '2025-02-16 06:45:26'),
(2, 8, 'asd', '2025-02-16 06:45:40'),
(3, 8, 'asdasd', '2025-02-16 06:45:41'),
(4, 7, 'asdasd', '2025-02-16 06:45:52'),
(5, 7, 'asdasd', '2025-02-16 09:51:17'),
(6, 7, 'asdasdasd', '2025-02-16 09:51:19');

-- --------------------------------------------------------

--
-- Table structure for table `chat_messages2`
--

CREATE TABLE `chat_messages2` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `chat_messages2`
--

INSERT INTO `chat_messages2` (`id`, `user_id`, `receiver_id`, `message`, `timestamp`) VALUES
(1, 7, 8, '123123', '2025-02-16 07:17:11'),
(2, 8, 7, 'asdasd', '2025-02-16 07:17:19');

-- --------------------------------------------------------

--
-- Table structure for table `chat_sessions`
--

CREATE TABLE `chat_sessions` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `receiver_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `trade_items`
--

CREATE TABLE `trade_items` (
  `ID` int(11) NOT NULL,
  `userID` int(11) NOT NULL,
  `image` varchar(255) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `trade_items`
--

INSERT INTO `trade_items` (`ID`, `userID`, `image`, `name`, `description`, `price`, `created_at`) VALUES
(1, 7, 'tr', 'test1', 'test1', 10.00, '2025-02-16 08:43:35');

-- --------------------------------------------------------

--
-- Table structure for table `userpass`
--

CREATE TABLE `userpass` (
  `ID` int(11) NOT NULL,
  `UserName` varchar(45) NOT NULL,
  `UserPass` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `userpass`
--

INSERT INTO `userpass` (`ID`, `UserName`, `UserPass`) VALUES
(7, 'usertest1', '1234'),
(8, 'usertest2', '1234'),
(9, 'usertest3', '1234');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `chat_messages2`
--
ALTER TABLE `chat_messages2`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `receiver_id` (`receiver_id`);

--
-- Indexes for table `chat_sessions`
--
ALTER TABLE `chat_sessions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`,`receiver_id`),
  ADD KEY `receiver_id` (`receiver_id`);

--
-- Indexes for table `trade_items`
--
ALTER TABLE `trade_items`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `userID` (`userID`);

--
-- Indexes for table `userpass`
--
ALTER TABLE `userpass`
  ADD PRIMARY KEY (`ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `chat_messages`
--
ALTER TABLE `chat_messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `chat_messages2`
--
ALTER TABLE `chat_messages2`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `chat_sessions`
--
ALTER TABLE `chat_sessions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `trade_items`
--
ALTER TABLE `trade_items`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `userpass`
--
ALTER TABLE `userpass`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD CONSTRAINT `chat_messages_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `userpass` (`ID`);

--
-- Constraints for table `chat_messages2`
--
ALTER TABLE `chat_messages2`
  ADD CONSTRAINT `chat_messages2_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `userpass` (`ID`),
  ADD CONSTRAINT `chat_messages2_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `userpass` (`ID`);

--
-- Constraints for table `chat_sessions`
--
ALTER TABLE `chat_sessions`
  ADD CONSTRAINT `chat_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `userpass` (`ID`),
  ADD CONSTRAINT `chat_sessions_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `userpass` (`ID`);

--
-- Constraints for table `trade_items`
--
ALTER TABLE `trade_items`
  ADD CONSTRAINT `trade_items_ibfk_1` FOREIGN KEY (`userID`) REFERENCES `userpass` (`ID`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
