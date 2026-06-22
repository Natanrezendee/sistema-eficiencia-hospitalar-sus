-- =====================================================
-- BANCO DE DADOS: EFICIENCIA_HOSPITALAR
-- =====================================================


CREATE DATABASE IF NOT EXISTS eficiencia_hospitalar
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;


USE eficiencia_hospitalar;


-- =====================================================
-- TABELA: HOSPITAL
-- =====================================================


CREATE TABLE hospital (
    id_hospital        INT UNSIGNED AUTO_INCREMENT,
    cnpj               CHAR(14)     NOT NULL,
    nome               VARCHAR(255) NOT NULL,
    cidade             VARCHAR(150) NOT NULL,
    endereco           VARCHAR(300) NOT NULL,
    capacidade_leitos  INT UNSIGNED NOT NULL,


    PRIMARY KEY (id_hospital),


    CONSTRAINT uq_cnpj
        UNIQUE (cnpj)
) ENGINE=InnoDB;


-- =====================================================
-- TABELA: MEDICO
-- =====================================================


CREATE TABLE medico (
    id_medico     INT UNSIGNED AUTO_INCREMENT,
    crm           VARCHAR(30)  NOT NULL,
    nome          VARCHAR(255) NOT NULL,
    telefone      VARCHAR(20),
    especialidade VARCHAR(150),


    PRIMARY KEY (id_medico),


    CONSTRAINT uq_crm
        UNIQUE (crm)
) ENGINE=InnoDB;


-- =====================================================
-- TABELA: PACIENTE
-- =====================================================


CREATE TABLE paciente (
    id_paciente     INT UNSIGNED AUTO_INCREMENT,
    cns             CHAR(15)     NOT NULL,
    cpf             CHAR(11)     NOT NULL,
    nome            VARCHAR(255) NOT NULL,
    data_nascimento DATE         NOT NULL,
    sexo            ENUM('M', 'F', 'Outro') NOT NULL,
    telefone        VARCHAR(20),


    PRIMARY KEY (id_paciente),


    CONSTRAINT uq_cns
        UNIQUE (cns),


    CONSTRAINT uq_cpf
        UNIQUE (cpf)
) ENGINE=InnoDB;


-- =====================================================
-- TABELA: ATENDIMENTO
-- =====================================================


CREATE TABLE atendimento (
    id_atendimento    INT UNSIGNED AUTO_INCREMENT,


    id_paciente       INT UNSIGNED NOT NULL,
    id_hospital       INT UNSIGNED NOT NULL,
    id_medico         INT UNSIGNED NOT NULL,


    data_hora_entrada DATETIME     NOT NULL,
    triagem           ENUM(
                          'Vermelho',
                          'Laranja',
                          'Amarelo',
                          'Verde',
                          'Azul'
                      ) NOT NULL,
    sintomas          VARCHAR(1000) NOT NULL,
    diagnostico       VARCHAR(500)  NOT NULL,


    desfecho          ENUM(
                          'Alta médica',
                          'Evasão',
                          'Transferência',
                          'Óbito'
                      ) NOT NULL,


    causa_obito       VARCHAR(500),
    data_obito        DATETIME,


    PRIMARY KEY (id_atendimento),


    CONSTRAINT fk_at_paciente
        FOREIGN KEY (id_paciente)
        REFERENCES paciente(id_paciente)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,


    CONSTRAINT fk_at_hospital
        FOREIGN KEY (id_hospital)
        REFERENCES hospital(id_hospital)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,


    CONSTRAINT fk_at_medico
        FOREIGN KEY (id_medico)
        REFERENCES medico(id_medico)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- =====================================================
-- ÍNDICES
-- =====================================================


CREATE INDEX idx_atendimento_data
ON atendimento(data_hora_entrada);


CREATE INDEX idx_atendimento_paciente
ON atendimento(id_paciente);


-- =====================================================
-- TRIGGER: VALIDAÇÃO DE ÓBITO (INSERT)
-- =====================================================


DELIMITER $$


CREATE TRIGGER trg_atendimento_bi
BEFORE INSERT ON atendimento
FOR EACH ROW
BEGIN


    IF NEW.desfecho = 'Óbito' THEN


        IF NEW.causa_obito IS NULL
           OR TRIM(NEW.causa_obito) = '' THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT =
            'Causa do óbito obrigatória quando o desfecho for Óbito';
        END IF;


        IF NEW.data_obito IS NULL THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT =
            'Data do óbito obrigatória quando o desfecho for Óbito';
        END IF;


        IF NEW.data_obito < NEW.data_hora_entrada THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT =
            'Data do óbito não pode ser anterior à data de entrada';
        END IF;


    ELSE


        SET NEW.causa_obito = NULL;
        SET NEW.data_obito  = NULL;


    END IF;


END$$


DELIMITER ;


-- =====================================================
-- TRIGGER: VALIDAÇÃO DE ÓBITO (UPDATE)
-- =====================================================


DELIMITER $$


CREATE TRIGGER trg_atendimento_bu
BEFORE UPDATE ON atendimento
FOR EACH ROW
BEGIN


    IF NEW.desfecho = 'Óbito' THEN


        IF NEW.causa_obito IS NULL
           OR TRIM(NEW.causa_obito) = '' THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT =
            'Causa do óbito obrigatória quando o desfecho for Óbito';
        END IF;


        IF NEW.data_obito IS NULL THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT =
            'Data do óbito obrigatória quando o desfecho for Óbito';
        END IF;


        IF NEW.data_obito < NEW.data_hora_entrada THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT =
            'Data do óbito não pode ser anterior à data de entrada';
        END IF;


    ELSE


        SET NEW.causa_obito = NULL;
        SET NEW.data_obito  = NULL;


    END IF;


END$$


DELIMITER ;
