-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema toutou
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema toutou
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `toutou` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci ;
USE `toutou` ;

-- -----------------------------------------------------
-- Table `toutou`.`espece`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `toutou`.`espece` ;

CREATE TABLE IF NOT EXISTS `toutou`.`espece` (
  `id` INT NOT NULL,
  `nom` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;


-- -----------------------------------------------------
-- Table `toutou`.`animal`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `toutou`.`animal` ;

CREATE TABLE IF NOT EXISTS `toutou`.`animal` (
  `id` INT NOT NULL,
  `nom` VARCHAR(45) NOT NULL,
  `date_de_naissance` DATE NULL DEFAULT NULL,
  `date_ajout` DATE NULL DEFAULT NULL,
  `espece` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `espece_idx` (`espece` ASC) VISIBLE,
  CONSTRAINT `espece`
    FOREIGN KEY (`espece`)
    REFERENCES `toutou`.`espece` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
