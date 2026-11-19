-- =====================================================
-- CITAFACIL
-- Estructura de la base de datos
-- Compatible con MariaDB 10.4.32
-- Sin registros de ejemplo
-- =====================================================

CREATE DATABASE IF NOT EXISTS `gestion_citas`
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE `gestion_citas`;

SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================
-- TABLA: establecimiento
-- =====================================================

CREATE TABLE IF NOT EXISTS `establecimiento` (
    `Id_ESTABLECIMIENTO` INT(11) NOT NULL AUTO_INCREMENT,
    `NOMBRE_COMERCIAL` VARCHAR(100) NOT NULL,
    `NOMBRE` VARCHAR(50) NOT NULL,
    `APELLIDO` VARCHAR(50) NOT NULL,
    `TELEFONO` VARCHAR(20) DEFAULT NULL,
    `EMAIL` VARCHAR(100) NOT NULL,
    `DIRECCION` VARCHAR(100) DEFAULT NULL,
    `CONTRASENA` VARCHAR(255) DEFAULT NULL,
    `CORREO_VERIFICADO` TINYINT(1) NOT NULL DEFAULT 0,
    `ESTADO` TINYINT(1) NOT NULL DEFAULT 0,
    `WHATSAPP_PHONE_NUMBER_ID` VARCHAR(50) DEFAULT NULL,
    PRIMARY KEY (`Id_ESTABLECIMIENTO`),
    UNIQUE KEY `EMAIL` (`EMAIL`),
    UNIQUE KEY `UK_ESTABLECIMIENTO_WHATSAPP_PHONE_ID` (`WHATSAPP_PHONE_NUMBER_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: usuario
-- =====================================================

CREATE TABLE IF NOT EXISTS `usuario` (
    `Id_USUARIO` INT(11) NOT NULL AUTO_INCREMENT,
    `Id_ESTABLECIMIENTO` INT(11) DEFAULT NULL,
    `NOMBRE` VARCHAR(100) NOT NULL,
    `CORREO` VARCHAR(100) NOT NULL,
    `TELEFONO` VARCHAR(20) DEFAULT NULL,
    `CONTRASEÑA` VARCHAR(255) NOT NULL,
    `CARGO` ENUM('cliente') NOT NULL DEFAULT 'cliente',
    `ESTADO` TINYINT(1) NOT NULL DEFAULT 0,
    `CORREO_VERIFICADO` TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (`Id_USUARIO`),
    UNIQUE KEY `CORREO` (`CORREO`),
    KEY `idx_usuario_establecimiento` (`Id_ESTABLECIMIENTO`),
    CONSTRAINT `fk_usuario_establecimiento`
        FOREIGN KEY (`Id_ESTABLECIMIENTO`)
        REFERENCES `establecimiento` (`Id_ESTABLECIMIENTO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: cliente
-- =====================================================

CREATE TABLE IF NOT EXISTS `cliente` (
    `Id_CLIENTE` INT(11) NOT NULL AUTO_INCREMENT,
    `Id_USUARIO` INT(11) DEFAULT NULL,
    `NOMBRE` VARCHAR(100) NOT NULL,
    `TELEFONO` VARCHAR(20) NOT NULL,
    `CORREO` VARCHAR(100) DEFAULT NULL,
    `Id_ESTABLECIMIENTO` INT(11) NOT NULL,
    PRIMARY KEY (`Id_CLIENTE`),
    UNIQUE KEY `UK_CLIENTE_ESTABLECIMIENTO_TELEFONO` (`Id_ESTABLECIMIENTO`, `TELEFONO`),
    UNIQUE KEY `UK_CLIENTE_USUARIO_ESTABLECIMIENTO` (`Id_USUARIO`, `Id_ESTABLECIMIENTO`),
    KEY `idx_cliente_correo` (`CORREO`),
    CONSTRAINT `FK_CLIENTE_ESTABLECIMIENTO`
        FOREIGN KEY (`Id_ESTABLECIMIENTO`)
        REFERENCES `establecimiento` (`Id_ESTABLECIMIENTO`),
    CONSTRAINT `FK_CLIENTE_USUARIO`
        FOREIGN KEY (`Id_USUARIO`)
        REFERENCES `usuario` (`Id_USUARIO`)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: servicio
-- =====================================================

CREATE TABLE IF NOT EXISTS `servicio` (
    `Id_SERVICIO` INT(11) NOT NULL AUTO_INCREMENT,
    `Id_ESTABLECIMIENTO` INT(11) NOT NULL,
    `NOMBRE` VARCHAR(100) NOT NULL,
    `DESCRIPCION` TEXT DEFAULT NULL,
    `DURACION_MINUTOS` INT(11) NOT NULL,
    `PRECIO` DECIMAL(10,2) DEFAULT 0.00,
    `ESTADO` TINYINT(1) DEFAULT 1,
    PRIMARY KEY (`Id_SERVICIO`),
    KEY `idx_servicio_establecimiento` (`Id_ESTABLECIMIENTO`),
    CONSTRAINT `fk_servicio_establecimiento`
        FOREIGN KEY (`Id_ESTABLECIMIENTO`)
        REFERENCES `establecimiento` (`Id_ESTABLECIMIENTO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: cita
-- =====================================================

CREATE TABLE IF NOT EXISTS `cita` (
    `Id_CITA` INT(11) NOT NULL AUTO_INCREMENT,
    `Id_ESTABLECIMIENTO` INT(11) NOT NULL,
    `Id_CLIENTE` INT(11) NOT NULL,
    `Id_SERVICIO` INT(11) NOT NULL,
    `FECHA` DATE NOT NULL,
    `HORA_INICIO` TIME NOT NULL,
    `HORA_FIN` TIME NOT NULL,
    `ESTADO` ENUM('pendiente', 'confirmada', 'cancelada', 'completada') NOT NULL DEFAULT 'pendiente',
    `FECHA_CREACION` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`Id_CITA`),
    UNIQUE KEY `uq_cita_hora_inicio` (`Id_ESTABLECIMIENTO`, `FECHA`, `HORA_INICIO`),
    KEY `fk_cita_servicio` (`Id_SERVICIO`),
    KEY `idx_cita_fecha` (`FECHA`),
    KEY `idx_cita_estado` (`ESTADO`),
    KEY `idx_cita_cliente` (`Id_CLIENTE`),
    CONSTRAINT `fk_cita_cliente`
        FOREIGN KEY (`Id_CLIENTE`)
        REFERENCES `cliente` (`Id_CLIENTE`),
    CONSTRAINT `fk_cita_establecimiento`
        FOREIGN KEY (`Id_ESTABLECIMIENTO`)
        REFERENCES `establecimiento` (`Id_ESTABLECIMIENTO`),
    CONSTRAINT `fk_cita_servicio`
        FOREIGN KEY (`Id_SERVICIO`)
        REFERENCES `servicio` (`Id_SERVICIO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: horario
-- =====================================================

CREATE TABLE IF NOT EXISTS `horario` (
    `Id_HORARIO` INT(11) NOT NULL AUTO_INCREMENT,
    `Id_ESTABLECIMIENTO` INT(11) NOT NULL,
    `DIA` ENUM('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo') NOT NULL,
    `HORA_INICIO` TIME NOT NULL,
    `HORA_FIN` TIME NOT NULL,
    `ESTADO` TINYINT(1) DEFAULT 1,
    `HORA_INICIO_DESCANSO` TIME DEFAULT NULL,
    `HORA_FIN_DESCANSO` TIME DEFAULT NULL,
    PRIMARY KEY (`Id_HORARIO`),
    KEY `idx_horario_establecimiento_dia` (`Id_ESTABLECIMIENTO`, `DIA`),
    CONSTRAINT `fk_horario_establecimiento`
        FOREIGN KEY (`Id_ESTABLECIMIENTO`)
        REFERENCES `establecimiento` (`Id_ESTABLECIMIENTO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: notificacion
-- =====================================================

CREATE TABLE IF NOT EXISTS `notificacion` (
    `Id_NOTIFICACION` INT(11) NOT NULL AUTO_INCREMENT,
    `Id_CITA` INT(11) NOT NULL,
    `CANAL` ENUM('correo', 'sms', 'whatsapp') NOT NULL,
    `TIPO` ENUM('confirmacion', 'recordatorio', 'cancelacion') NOT NULL,
    `ESTADO` ENUM('pendiente', 'enviada', 'fallida') NOT NULL DEFAULT 'pendiente',
    `FECHA_SOLICITUD` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `FECHA_PROGRAMADA` DATETIME DEFAULT NULL,
    `FECHA_ENVIO` DATETIME DEFAULT NULL,
    `INTENTOS` TINYINT(3) UNSIGNED NOT NULL DEFAULT 0,
    `RESPUESTA` TEXT DEFAULT NULL,
    PRIMARY KEY (`Id_NOTIFICACION`),
    UNIQUE KEY `uq_notificacion_cita_canal_tipo` (`Id_CITA`, `CANAL`, `TIPO`),
    KEY `idx_notificacion_estado_fecha` (`ESTADO`, `FECHA_PROGRAMADA`),
    CONSTRAINT `fk_notificacion_cita`
        FOREIGN KEY (`Id_CITA`)
        REFERENCES `cita` (`Id_CITA`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: token_autenticacion
-- =====================================================

CREATE TABLE IF NOT EXISTS `token_autenticacion` (
    `ID_TOKEN` INT(11) NOT NULL AUTO_INCREMENT,
    `ID_USUARIO` INT(11) DEFAULT NULL,
    `ID_ESTABLECIMIENTO` INT(11) DEFAULT NULL,
    `TOKEN_HASH` CHAR(64) NOT NULL,
    `TIPO` ENUM('verificacion_email', 'recuperacion_password') NOT NULL,
    `EXPIRA_EN` DATETIME NOT NULL,
    `USADO_EN` DATETIME DEFAULT NULL,
    `CREADO_EN` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`ID_TOKEN`),
    UNIQUE KEY `TOKEN_HASH` (`TOKEN_HASH`),
    KEY `FK_TOKEN_USUARIO` (`ID_USUARIO`),
    KEY `FK_TOKEN_ESTABLECIMIENTO` (`ID_ESTABLECIMIENTO`),
    CONSTRAINT `FK_TOKEN_ESTABLECIMIENTO`
        FOREIGN KEY (`ID_ESTABLECIMIENTO`)
        REFERENCES `establecimiento` (`Id_ESTABLECIMIENTO`)
        ON DELETE CASCADE,
    CONSTRAINT `FK_TOKEN_USUARIO`
        FOREIGN KEY (`ID_USUARIO`)
        REFERENCES `usuario` (`Id_USUARIO`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;

