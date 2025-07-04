-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 04-07-2025 a las 21:02:04
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
-- Estructura de tabla para la tabla `docente`
--

CREATE TABLE `docente` (
  `ID_Docente` int(11) NOT NULL,
  `Nombre` varchar(50) NOT NULL,
  `Apellido_P` varchar(50) NOT NULL,
  `Apellido_M` varchar(50) NOT NULL,
  `Correo` varchar(100) NOT NULL,
  `Telefono` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `docente`
--

INSERT INTO `docente` (`ID_Docente`, `Nombre`, `Apellido_P`, `Apellido_M`, `Correo`, `Telefono`) VALUES
(1, 'Lucía', 'Hernández', 'Cruz', 'lucia.hernandez@uttlax.edu.mx', '2461234567'),
(2, 'Carlos', 'Ramírez', 'López', 'carlos.ramirez@uttlax.edu.mx', '2469876543'),
(3, 'María', 'Gómez', 'Salinas', 'maria.gomez@uttlax.edu.mx', '2465566778'),
(4, 'Jorge', 'Martínez', 'Vega', 'jorge.martinez@uttlax.edu.mx', '2461112233'),
(5, 'Ana', 'Torres', 'Díaz', 'ana.torres@uttlax.edu.mx', '2463334455');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estudiante`
--

CREATE TABLE `estudiante` (
  `ID_Estudiante` int(11) NOT NULL,
  `Nombre` varchar(50) NOT NULL,
  `Apellido_P` varchar(50) NOT NULL,
  `Apellido_M` varchar(50) NOT NULL,
  `Correo` varchar(100) NOT NULL,
  `Telefono` varchar(20) DEFAULT NULL,
  `Edad` int(11) DEFAULT NULL,
  `Grado_Grupo` varchar(20) DEFAULT NULL,
  `carrera` varchar(100) NOT NULL,
  `Contraseña` varchar(255) NOT NULL,
  `Matricula` varchar(50) DEFAULT NULL,
  `Sexo` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `estudiante`
--

INSERT INTO `estudiante` (`ID_Estudiante`, `Nombre`, `Apellido_P`, `Apellido_M`, `Correo`, `Telefono`, `Edad`, `Grado_Grupo`, `carrera`, `Contraseña`, `Matricula`, `Sexo`) VALUES
(1, 'Sandro Giovanny ', 'Olivares', 'Apolinar', 'sandroutt@gmail.com', '2472054695', 18, '3A', 'TIADSM', 'CBTIS2021', '20242IDSM056', NULL),
(2, 'Denisse', 'Hernandez ', 'Vasquez', 'denisseutt@gmail.com', '2471245656', 19, '3A', 'TIAEV', 'den123', '20242IDSM050', NULL),
(3, 'Erick', 'Morales', 'Baltazar', 'erik@gmail.com', '2471234563', 19, '3A', 'TIADSM', 'erik', '20242IDSM051', NULL),
(4, 'Prueba', 'Sol', 'Perez', 'prueba@gmail.com', '2471405924', 19, '3A', 'TIADSM', 'ola', '20242IDSM012', 'H');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `inscripcion`
--

CREATE TABLE `inscripcion` (
  `ID_Inscripcion` int(11) NOT NULL,
  `ID_Estudiante` int(11) NOT NULL,
  `ID_Taller` int(11) NOT NULL,
  `Fecha_Inscripcion` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `taller`
--

CREATE TABLE `taller` (
  `ID_Taller` int(11) NOT NULL,
  `Nombre_Taller` varchar(100) NOT NULL,
  `ID_Docente` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `taller`
--

INSERT INTO `taller` (`ID_Taller`, `Nombre_Taller`, `ID_Docente`) VALUES
(1, 'Fútbol Universitario', 1),
(2, 'Básquetbol Intercolegial', 2),
(3, 'Atletismo y Resistencia', 3);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `docente`
--
ALTER TABLE `docente`
  ADD PRIMARY KEY (`ID_Docente`),
  ADD UNIQUE KEY `Correo` (`Correo`);

--
-- Indices de la tabla `estudiante`
--
ALTER TABLE `estudiante`
  ADD PRIMARY KEY (`ID_Estudiante`),
  ADD UNIQUE KEY `Correo` (`Correo`);

--
-- Indices de la tabla `inscripcion`
--
ALTER TABLE `inscripcion`
  ADD PRIMARY KEY (`ID_Inscripcion`),
  ADD KEY `ID_Estudiante` (`ID_Estudiante`),
  ADD KEY `ID_Taller` (`ID_Taller`);

--
-- Indices de la tabla `taller`
--
ALTER TABLE `taller`
  ADD PRIMARY KEY (`ID_Taller`),
  ADD KEY `ID_Docente` (`ID_Docente`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `docente`
--
ALTER TABLE `docente`
  MODIFY `ID_Docente` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `estudiante`
--
ALTER TABLE `estudiante`
  MODIFY `ID_Estudiante` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `inscripcion`
--
ALTER TABLE `inscripcion`
  MODIFY `ID_Inscripcion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `taller`
--
ALTER TABLE `taller`
  MODIFY `ID_Taller` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `inscripcion`
--
ALTER TABLE `inscripcion`
  ADD CONSTRAINT `inscripcion_ibfk_1` FOREIGN KEY (`ID_Estudiante`) REFERENCES `estudiante` (`ID_Estudiante`) ON DELETE CASCADE,
  ADD CONSTRAINT `inscripcion_ibfk_2` FOREIGN KEY (`ID_Taller`) REFERENCES `taller` (`ID_Taller`) ON DELETE CASCADE;

--
-- Filtros para la tabla `taller`
--
ALTER TABLE `taller`
  ADD CONSTRAINT `taller_ibfk_1` FOREIGN KEY (`ID_Docente`) REFERENCES `docente` (`ID_Docente`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
