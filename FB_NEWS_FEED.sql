-- phpMyAdmin SQL Dump
-- version 4.8.2
--

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `FB_NEWS_FEED`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `FB_POST`
--

CREATE TABLE `FB_POST` (
  `ID` int(11) NOT NULL,
  `FB_ID` varchar(25) NOT NULL,
  `Link` text,
  `Post_Date` date DEFAULT NULL,
  `Title` varchar(255) DEFAULT NULL,
  `Content` text,
  `Main_Image` text,
  `Created_Date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Updated_Date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `FB_TRACK`
--

CREATE TABLE `FB_TRACK` (
  `ID` int(11) NOT NULL,
  `FB_ID` varchar(25) NOT NULL,
  `Views` int(10) UNSIGNED DEFAULT NULL,
  `Comments` int(10) UNSIGNED DEFAULT NULL,
  `Shares` int(10) UNSIGNED DEFAULT NULL,
  `Reactions` int(10) UNSIGNED DEFAULT NULL,
  `Updated_Date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `FB_POST`
--
ALTER TABLE `FB_POST`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `FB_ID` (`FB_ID`);

--
-- Indices de la tabla `FB_TRACK`
--
ALTER TABLE `FB_TRACK`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `FB_ID` (`FB_ID`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `FB_POST`
--
ALTER TABLE `FB_POST`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `FB_TRACK`
--
ALTER TABLE `FB_TRACK`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
