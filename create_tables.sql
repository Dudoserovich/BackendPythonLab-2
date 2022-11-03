DROP TABLE IF EXISTS patient;
CREATE TABLE patient
(
    id              INTEGER  PRIMARY KEY AUTOINCREMENT CHECK ( id <= 9999 ),
    full_name       CHAR(50) NOT NULL unique,
    address         CHAR(50) NOT NULL,
    sex             CHAR(1)  CHECK ( sex in ('M', 'F') ) not null default 'M',
    birthday        DATE     NOT NULL
);

DROP TABLE IF EXISTS specialization;
CREATE TABLE specialization
(
    id   INTEGER PRIMARY KEY AUTOINCREMENT CHECK ( id <= 9999 ) NOT NULL,
    name CHAR(50) NOT NULL unique
);

DROP TABLE IF EXISTS doctor;
CREATE TABLE doctor
(
    id              INTEGER   PRIMARY KEY AUTOINCREMENT CHECK ( id <= 9999 ),
    spec_id         INTEGER  not null check ( spec_id between 1 and 9999 ),
    full_name       CHAR(50) NOT NULL unique,
    sex             CHAR(1)  CHECK ( sex in ('M', 'F') ) not null default 'M',
    address         CHAR(40) NOT NULL,
    phone           CHAR(20) NOT NULL,
    work_experience integer  NOT NULL CHECK ( work_experience between 1 and 99 ),
    FOREIGN KEY (spec_id) references specialization(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- starting и ending может быть null, когда, например, ыходной день
DROP TABLE IF EXISTS schedule;
CREATE TABLE schedule (
    id              INTEGER  PRIMARY KEY AUTOINCREMENT CHECK ( id <= 9999 ),
    s_date          date     not null,
    starting        time,
    ending          time
);

DROP TABLE IF EXISTS place;
CREATE TABLE place (
    id      INTEGER     PRIMARY KEY AUTOINCREMENT CHECK ( id <= 9999 ),
    name    VARCHAR(20) not null unique
);

-- patient_id может быть пустым, когда на какое-то время не назначен приём
DROP TABLE IF EXISTS doctor_schedule;
CREATE TABLE doctor_schedule (
    id              INTEGER   PRIMARY KEY AUTOINCREMENT CHECK ( id <= 9999 ),
    doctor_id       INTEGER   not null CHECK ( doctor_id <= 9999 ),
    schedule_id     INTEGER   not null CHECK ( schedule_id <= 9999 ),
    place_id        INTEGER   not null CHECK ( place_id <= 9999 ),
    FOREIGN KEY (doctor_id)     references doctor (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (schedule_id)   references schedule (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (place_id)      references place (id) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS visit;
CREATE TABLE visit
(
    id              INTEGER      PRIMARY KEY AUTOINCREMENT CHECK ( id <= 99999 ),
    registration_id integer      not null check ( registration_id between 1 and 9999 ),
    patient_id      integer      not null check ( patient_id between 1 and 9999 ),
    symptoms        VARCHAR(100) not null,
    diagnosis       VARCHAR(100) not null,
    FOREIGN KEY (registration_id) references doctor_schedule (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (patient_id)    references patient (id) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS medicine;
CREATE TABLE medicine
(
    id          INTEGER  PRIMARY KEY AUTOINCREMENT CHECK ( id <= 99999 ),
    name        VARCHAR(30)  not null unique,
    usage       VARCHAR(100) not null,
    actions     VARCHAR(80)  not null,
    effects     VARCHAR(80)
);

DROP TABLE IF EXISTS appointment;
CREATE TABLE appointment
(
    visit_id    integer check ( visit_id between 1 and 99999 ),
    medicine_id integer check ( medicine_id between 1 and 99999 ),
    amount      integer not null check ( amount between 1 and 99 ),
    PRIMARY KEY (visit_id, medicine_id),
    FOREIGN KEY (visit_id)    references visit (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (medicine_id) references medicine (id) ON DELETE CASCADE ON UPDATE CASCADE
);