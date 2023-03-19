DROP DATABASE IF EXISTS healthunit;
CREATE DATABASE IF NOT EXISTS healthunit;
USE healthunit;

CREATE TABLE IF NOT EXISTS pessoa (
ID MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
CPF CHAR(11) NOT NULL UNIQUE,
Nome VARCHAR(20) NOT NULL,
Telefone CHAR(11) NOT NULL, 
Email VARCHAR(20) NOT NULL,
CEP CHAR(8) NOT NULL,
Complem_Endereco VARCHAR(20) NOT NULL,
Idade TINYINT UNSIGNED NOT NULL,
Genero CHAR(1) NOT NULL,
Nascimento DATE NOT NULL,
CONSTRAINT PK_Pessoa PRIMARY KEY (ID)
);

CREATE TABLE IF NOT EXISTS paciente (
ID MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
ID_Pessoa MEDIUMINT UNSIGNED NOT NULL UNIQUE,
CONSTRAINT PK_Paciente PRIMARY KEY (ID),
CONSTRAINT FK_Pessoa_Paciente FOREIGN KEY (ID_Pessoa) REFERENCES pessoa(ID)
);
CREATE TABLE IF NOT EXISTS  profissional (
ID TINYINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
ID_Pessoa MEDIUMINT UNSIGNED NOT NULL UNIQUE,
CONSTRAINT PK_Profissional PRIMARY KEY (ID),
CONSTRAINT FK_Pessoa_Profissional FOREIGN KEY (ID_Pessoa) REFERENCES pessoa(ID)
);

CREATE TABLE IF NOT EXISTS  avaliacao_profissional (
ID_Profissional TINYINT UNSIGNED NOT NULL,
ID_Paciente MEDIUMINT UNSIGNED NOT NULL,
Nota TINYINT UNSIGNED NOT NULL,
Descricao TEXT,
CONSTRAINT FK_Profissional_Avaliado FOREIGN KEY (ID_Profissional) REFERENCES profissional(ID),
CONSTRAINT FK_Paciente_Avaliou_Profissional FOREIGN KEY (ID_Paciente) REFERENCES paciente(ID),
CONSTRAINT AK_Avaliacao_Profissional UNIQUE(ID_Profissional, ID_Paciente)
);

CREATE TABLE IF NOT EXISTS  avaliacao_unidade (
ID_Paciente MEDIUMINT UNSIGNED NOT NULL UNIQUE,
Nota TINYINT UNSIGNED NOT NULL,
Descricao TEXT,
CONSTRAINT FK_Paciente_Avaliou_Unidade FOREIGN KEY (ID_Paciente) REFERENCES paciente(ID)
);

CREATE TABLE IF NOT EXISTS  medico (
ID TINYINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
ID_Profissional TINYINT UNSIGNED NOT NULL UNIQUE,
CONSTRAINT PK_Medico PRIMARY KEY (ID),
CONSTRAINT FK_Profissional_Medico FOREIGN KEY (ID_Profissional) REFERENCES profissional(ID)
);
CREATE TABLE IF NOT EXISTS especializacao (
ID TINYINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
Nome VARCHAR(20) NOT NULL UNIQUE,
Descricao TEXT,
CONSTRAINT PK_Especializacao PRIMARY KEY (ID)
);

CREATE TABLE IF NOT EXISTS  especializacao_medico (
ID_Especializacao TINYINT UNSIGNED NOT NULL,
ID_Medico TINYINT UNSIGNED NOT NULL,
CONSTRAINT FK_Especializacao_do_Medico FOREIGN KEY (ID_Especializacao) REFERENCES especializacao(ID),
CONSTRAINT FK_Medico_com_Especializacao FOREIGN KEY (ID_Medico) REFERENCES medico(ID),
CONSTRAINT AK_Especializacao_Medico UNIQUE(ID_Especializacao, ID_Medico)
);


CREATE TABLE IF NOT EXISTS  recepcionista (
ID TINYINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
ID_Profissional TINYINT UNSIGNED NOT NULL UNIQUE,
CONSTRAINT PK_Recepcionista PRIMARY KEY (ID),
CONSTRAINT FK_Profissional_Recepcionista FOREIGN KEY (ID_Profissional) REFERENCES profissional(ID)
);
CREATE TABLE IF NOT EXISTS  farmaceutico (
ID TINYINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
ID_Profissional TINYINT UNSIGNED NOT NULL UNIQUE,
CONSTRAINT PK_Farmaceutico PRIMARY KEY (ID),
CONSTRAINT FK_Profissional_Farmaceutico FOREIGN KEY (ID_Profissional) REFERENCES profissional(ID)
);

CREATE TABLE IF NOT EXISTS  doenca (
ID SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
Nome VARCHAR(20) NOT NULL UNIQUE,
Descricao Text,
CONSTRAINT PK_Doenca PRIMARY KEY (ID)
);
CREATE TABLE IF NOT EXISTS  remedio (
ID SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
Nome VARCHAR(20) NOT NULL UNIQUE,
Descricao Text,
CONSTRAINT PK_Remedio PRIMARY KEY (ID)
);
CREATE TABLE IF NOT EXISTS  doenca_remedio (
ID_Doenca SMALLINT UNSIGNED NOT NULL,
ID_Remedio SMALLINT UNSIGNED NOT NULL,
CONSTRAINT FK_Doenca FOREIGN KEY (ID_Doenca) REFERENCES doenca(ID),
CONSTRAINT FK_Remedio FOREIGN KEY (ID_Remedio) REFERENCES remedio(ID),
CONSTRAINT AK_Doenca_Remedio UNIQUE(ID_Doenca, ID_Remedio)
);

CREATE TABLE IF NOT EXISTS  doenca_paciente (
ID_Doenca SMALLINT UNSIGNED NOT NULL,
ID_Paciente MEDIUMINT UNSIGNED NOT NULL,
CONSTRAINT FK_Doenca_no_Paciente FOREIGN KEY (ID_Doenca) REFERENCES doenca(ID),
CONSTRAINT FK_Paciente_com_Doenca FOREIGN KEY (ID_Paciente) REFERENCES paciente(ID),
CONSTRAINT AK_Doenca_Paciente UNIQUE(ID_Doenca, ID_Paciente)
);

CREATE TABLE IF NOT EXISTS  estoque (
ID MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
ID_Remedio SMALLINT UNSIGNED NOT NULL,
Quantidade SMALLINT UNSIGNED NOT NULL,
Data_Fabricacao DATE NOT NULL,
Data_Validade DATE NOT NULL,
CONSTRAINT PK_Estoque PRIMARY KEY (ID),
CONSTRAINT FK_Remedio_em_Estoque FOREIGN KEY (ID_Remedio) REFERENCES remedio(ID)
);


CREATE TABLE IF NOT EXISTS calendario (
ID SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
Data_Calendar DATE NOT NULL UNIQUE,
Dia_Semana ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
Feriado BOOLEAN NOT NULL,
CONSTRAINT PK_Calendario PRIMARY KEY (ID)
);

CREATE TABLE IF NOT EXISTS calendario_especializacao_medico (
ID INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
ID_Calendario SMALLINT UNSIGNED NOT NULL,
ID_Especializacao TINYINT UNSIGNED NOT NULL,
ID_Medico TINYINT UNSIGNED NOT NULL,
Tempo_Inicial TIME NOT NULL,
Tempo_Final TIME NOT NULL,
CONSTRAINT PK_Calendario_Especializacao_Medico PRIMARY KEY (ID),
CONSTRAINT FK_ID_Especializacao_Medico FOREIGN KEY (ID_Especializacao, ID_Medico) REFERENCES especializacao_medico(ID_Especializacao, ID_Medico),
CONSTRAINT FK_ID_Calendario FOREIGN KEY (ID_Calendario) REFERENCES calendario(ID),
CONSTRAINT AK_Calendario_Especializacao_Medico_Inicial UNIQUE(ID_Calendario, ID_Especializacao, ID_Medico, Tempo_Inicial),
CONSTRAINT AK_Calendario_Especializacao_Medico_Final UNIQUE(ID_Calendario, ID_Especializacao, ID_Medico, Tempo_Final)
);

CREATE TABLE IF NOT EXISTS consulta (
ID INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
ID_Calendario_Especializacao_Medico INT UNSIGNED NOT NULL,
Tempo_Inicial TIME NOT NULL,
Tempo_Final TIME NOT NULL,
CONSTRAINT PK_Consulta PRIMARY KEY (ID),
CONSTRAINT FK_Consulta FOREIGN KEY (ID_Calendario_Especializacao_Medico) REFERENCES calendario_especializacao_medico(ID),
CONSTRAINT AK_Consulta_Inicial UNIQUE(ID_Calendario_Especializacao_Medico, Tempo_Inicial),
CONSTRAINT AK_Consulta_Final UNIQUE(ID_Calendario_Especializacao_Medico, Tempo_Final)
);

CREATE TABLE IF NOT EXISTS consulta_disponivel (
ID_Consulta INT UNSIGNED NOT NULL UNIQUE,
CONSTRAINT FK_Consulta_Disponivel FOREIGN KEY (ID_Consulta) REFERENCES consulta(ID)
);

CREATE TABLE IF NOT EXISTS consulta_paciente_reservada (
ID_Consulta INT UNSIGNED NOT NULL UNIQUE,
ID_Paciente MEDIUMINT UNSIGNED NOT NULL,
Realizada BOOLEAN NOT NULL,
CONSTRAINT FK_Consulta_do_Paciente_Reservada FOREIGN KEY (ID_Consulta) REFERENCES consulta(ID),
CONSTRAINT FK_Paciente_da_Consulta_Reservada FOREIGN KEY (ID_Paciente) REFERENCES paciente(ID)
);


CREATE TABLE IF NOT EXISTS receita (
ID INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
ID_Paciente MEDIUMINT UNSIGNED NOT NULL,
ID_Consulta INT UNSIGNED NOT NULL UNIQUE,
Data_Validade DATE NOT NULL,
CONSTRAINT FK_Consulta_Paciente_Reservada FOREIGN KEY (ID_Paciente, ID_Consulta) REFERENCES consulta_paciente_reservada(ID_Paciente, ID_Consulta)
);

CREATE TABLE IF NOT EXISTS receita_remedio (
ID_Receita INT UNSIGNED NOT NULL,
ID_Remedio SMALLINT UNSIGNED NOT NULL,
Quantidade TINYINT UNSIGNED NOT NULL,
CONSTRAINT FK_Receita_com_remedio FOREIGN KEY (ID_Receita) REFERENCES receita(ID),
CONSTRAINT FK_Remedio_na_receita FOREIGN KEY (ID_Remedio) REFERENCES remedio(ID),
CONSTRAINT AK_Receita_Remedio UNIQUE(ID_Receita, ID_Remedio)
);

CREATE TABLE IF NOT EXISTS receita_remedio_reservada (
ID_Receita INT UNSIGNED NOT NULL,
ID_Remedio SMALLINT UNSIGNED NOT NULL,
CONSTRAINT FK_Receita_Remedio_Reservada FOREIGN KEY (ID_Receita, ID_Remedio) REFERENCES receita_remedio(ID_Receita, ID_Remedio),
CONSTRAINT AK_Doenca_Paciente UNIQUE(ID_Receita, ID_Remedio)
);

CREATE TABLE IF NOT EXISTS receita_remedio_retirada (
ID_Receita INT UNSIGNED NOT NULL,
ID_Remedio SMALLINT UNSIGNED NOT NULL,
CONSTRAINT FK_Receita_Remedio_Retirada FOREIGN KEY (ID_Receita, ID_Remedio) REFERENCES receita_remedio(ID_Receita, ID_Remedio),
CONSTRAINT AK_Doenca_Paciente UNIQUE(ID_Receita, ID_Remedio)
);