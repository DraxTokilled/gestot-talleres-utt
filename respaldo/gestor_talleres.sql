-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 02-08-2025 a las 06:13:36
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `gestor_talleres`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `docentes`
--

CREATE TABLE `docentes` (
  `id_Docente` int(11) NOT NULL,
  `Matricula_Docente` varchar(20) DEFAULT NULL,
  `Nombre_D` varchar(100) DEFAULT NULL,
  `Apellido_P_D` varchar(100) DEFAULT NULL,
  `Apellido_M_D` varchar(100) DEFAULT NULL,
  `Correo_D` varchar(100) DEFAULT NULL,
  `Cedula_P_D` varchar(50) DEFAULT NULL,
  `Taller_Impartir` varchar(100) DEFAULT NULL,
  `Estatus` varchar(20) DEFAULT NULL,
  `Foto_CredencialD` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `docentes`
--

INSERT INTO `docentes` (`id_Docente`, `Matricula_Docente`, `Nombre_D`, `Apellido_P_D`, `Apellido_M_D`, `Correo_D`, `Cedula_P_D`, `Taller_Impartir`, `Estatus`, `Foto_CredencialD`) VALUES
(1, '20250328UTT', 'Diana', 'Ahuatzi', 'Reyes', 'dianalizeth@utt.com', '27263984778287', 'voleibol', 'A', 'copia_logo_utt.jpg');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estudiante`
--

CREATE TABLE `estudiante` (
  `id` int(11) NOT NULL,
  `Matricula` varchar(20) DEFAULT NULL,
  `Nombre` varchar(100) DEFAULT NULL,
  `Apellido_P` varchar(100) DEFAULT NULL,
  `Apellido_M` varchar(100) DEFAULT NULL,
  `Carrera` varchar(100) DEFAULT NULL,
  `Genero` varchar(20) DEFAULT NULL,
  `Edad` int(11) DEFAULT NULL,
  `NSS` varchar(20) DEFAULT NULL,
  `Grado_Grupo` varchar(20) DEFAULT NULL,
  `Telefono` varchar(20) DEFAULT NULL,
  `Tutor` varchar(100) DEFAULT NULL,
  `Telefono_Emergencia` varchar(20) DEFAULT NULL,
  `Correo` varchar(100) DEFAULT NULL,
  `Taller_Inscripcion` varchar(100) DEFAULT NULL,
  `Horario` varchar(100) DEFAULT NULL,
  `Contraseña` varchar(100) DEFAULT NULL,
  `Foto_Credencial` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `estudiante`
--

INSERT INTO `estudiante` (`id`, `Matricula`, `Nombre`, `Apellido_P`, `Apellido_M`, `Carrera`, `Genero`, `Edad`, `NSS`, `Grado_Grupo`, `Telefono`, `Tutor`, `Telefono_Emergencia`, `Correo`, `Taller_Inscripcion`, `Horario`, `Contraseña`, `Foto_Credencial`) VALUES
(1, '20250328IDSM', 'Tania ', 'Cazares', 'Olivares', 'TIDSM', 'M', 19, '377628789MTL', '3 A', '2415670938', 'Ruth Cervantes', '2418672483', 'taniacazoli@utt.com', 'voleibol', 'Martes 14:00-17:00', 'guerrerautt', 'logo.jpg'),
(2, '20250377IDSM', 'Alan', 'Perez', 'Avendaño', 'TIEVND', 'H', 18, '35210541344', '3 A', '2349865055', 'Alfredo Ruiz', '2346737363', 'alanpav@utt.com', 'atletismo', 'Lunes 16:00-17:00', 'guerreroutt', 'copia_logo_utt.jpg');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `taller`
--

CREATE TABLE `taller` (
  `id_taller` int(11) NOT NULL,
  `Nombre_T` varchar(100) DEFAULT NULL,
  `Nombre_D` varchar(100) DEFAULT NULL,
  `Dias_T` varchar(255) DEFAULT NULL,
  `Horarios` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`Horarios`)),
  `Estatus` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `taller`
--

INSERT INTO `taller` (`id_taller`, `Nombre_T`, `Nombre_D`, `Dias_T`, `Horarios`, `Estatus`) VALUES
(1, 'Baile', 'Ana Leal Ramos', '', '{\"Lunes\": \"15:00-17:00\", \"Mi\\u00e9rcoles\": \"14:30-16:30\"}', 'B');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `docentes`
--
ALTER TABLE `docentes`
  ADD PRIMARY KEY (`id_Docente`),
  ADD UNIQUE KEY `unique_Matricula_Docente` (`Matricula_Docente`),
  ADD UNIQUE KEY `unique_Cedula_P_D` (`Cedula_P_D`),
  ADD UNIQUE KEY `unique_Correo_D` (`Correo_D`);

--
-- Indices de la tabla `estudiante`
--
ALTER TABLE `estudiante`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `Matricula` (`Matricula`),
  ADD UNIQUE KEY `NSS` (`NSS`),
  ADD UNIQUE KEY `Correo` (`Correo`);

--
-- Indices de la tabla `taller`
--
ALTER TABLE `taller`
  ADD PRIMARY KEY (`id_taller`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `estudiante`
--
ALTER TABLE `estudiante`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `taller`
--
ALTER TABLE `taller`
  MODIFY `id_taller` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
