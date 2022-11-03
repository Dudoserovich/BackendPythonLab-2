import sqlite3
import pandas as pd


# 1) 2 запроса на выборку для связанных таблиц с условиями и сортировкой
def task1_1(con: sqlite3.Connection) -> None:
    """
    Выдать список всех врачей хирургов мужского пола, их адреса и телефоны.
    Список упорядочить по фамилии в обратном порядке.
    """
    print(pd.read_sql("""
        SELECT full_name, address, phone, s.name
        from doctor
            join specialization s on s.id = doctor.spec_id
        where sex = 'M'
          and s.name = 'Хирург'
        ORDER BY full_name DESC;
    """, con=con))


def task1_2(con: sqlite3.Connection) -> None:
    """
    Для каждого пациента выдать список всех врачей,
    которых когда-либо они посещали, дату посещения и поставленный диагноз.
    """
    print(pd.read_sql("""
        SELECT patient.full_name,
               d.full_name as `Врач`,
               s.s_date || ', ' || s.starting || ':00-' || s.ending || ':00' as `Дата и время посещения`,
               v.diagnosis as `Диагноз`
        FROM patient
                 JOIN visit v on patient.id = v.patient_id
                 JOIN doctor_schedule ds on ds.id = v.registration_id
                 JOIN doctor d on d.id = ds.doctor_id
                 JOIN schedule s on s.id = ds.schedule_id
        WHERE EXISTS
                  (SELECT *
                   FROM visit
                   WHERE patient.id = v.patient_id)
        ORDER BY patient.full_name;
    """, con=con))

# 2) 2 запроса с группировкой и групповыми функциями
def task2_1(con: sqlite3.Connection, s_date: str) -> None:
    """
    Вывести рабочую нагрузку (количество рабочих часов) для каждого врача в указанную дату
    """
    print(pd.read_sql("""
        SELECT d.full_name as `ФИО`, s.s_date as `Дата`, count(s.s_date) as `Количество рабочих часов`
        FROM doctor_schedule
            JOIN doctor d on d.id = doctor_schedule.doctor_id
            JOIN main.schedule s on s.id = doctor_schedule.schedule_id
        where s.s_date = :s_date
        group by d.full_name;
    """, con=con, params={'s_date': s_date}))


def task2_2(con: sqlite3.Connection) -> None:
    """
    Вывести количество врачей всех специальностей
    """
    print(pd.read_sql("""
        SELECT specialization.name as `Специализация`, count(d.id) as `Количество врачей`
        FROM specialization
            JOIN doctor d on specialization.id = d.spec_id
        group by specialization.name;
    """, con=con))


# 3) 2 запроса со вложенными запросами или табличными выражениями
def task3_1(con: sqlite3.Connection) -> None:
    """
    Вывести количество врачей всех специальностей
    """
    print(pd.read_sql("""
        SELECT s.name, count(s.name) as 'Частота посещения'
        FROM visit
            JOIN doctor_schedule ds on ds.id = visit.registration_id
            JOIN doctor d on d.id = ds.doctor_id
            JOIN specialization s on d.spec_id = s.id
            JOIN patient p on visit.patient_id = p.id
        WHERE EXISTS
                  (SELECT *
                   FROM visit
                   WHERE p.id = visit.patient_id)
        group by s.name;
    """, con=con))


def task3_2(con: sqlite3.Connection) -> None:
    """
    3.2 Вывести врачей, у которых опыт работы выше среднего относительно других,
    а так же вывести их специализации
    """
    print(pd.read_sql("""
        SELECT s.name, count(s.name) as 'Частота посещения'
        FROM visit
            JOIN doctor_schedule ds on ds.id = visit.registration_id
            JOIN doctor d on d.id = ds.doctor_id
            JOIN specialization s on d.spec_id = s.id
            JOIN patient p on visit.patient_id = p.id
        WHERE EXISTS
                  (SELECT *
                   FROM visit
                   WHERE p.id = visit.patient_id)
        group by s.name;
    """, con=con))


# 4) 2 запроса корректировки данных (обновление, добавление, удаление и пр)
def task4_1(con: sqlite3.Connection, doctor_id: int, spec_name: str, date: str) -> None:
    """
    Замена врача в расписании врачом той же специализации и который не работает в текущий день
    """
    sql = """
        UPDATE doctor_schedule SET doctor_id =
            (select doctor.id
                FROM doctor
                    join specialization s2 on s2.id = doctor.spec_id
                where doctor.id not in (select doctor_id
                                        from doctor_schedule
                                            JOIN schedule s on s.id = doctor_schedule.schedule_id
                                        where s.s_date = '2022-11-03')
                and s2.name = :spec_name)
        where doctor_id=:doctor_id;
    """
    cur = con.cursor()
    cur.execute(sql, {
        "spec_name": spec_name,
        "doctor_id": doctor_id,
        "date": date
    })
    con.commit()


def task4_2(con: sqlite3.Connection, birthday: str) -> None:
    """
    Замена врача в расписании врачом той же специализации и который не работает в текущий день
    """
    sql = """delete from patient where birthday <= :birthday;"""
    cur = con.cursor()
    cur.execute(sql, {
        "birthday": birthday,
    })
    con.commit()


def main():
    con = sqlite3.connect("medicine.sqlite")

    task1_1(con)
    print('-' * 100)
    task1_2(con)
    print('-' * 100)

    task2_1(con, '2022-11-03')
    print('-' * 100)
    task2_2(con)
    print('-' * 100)

    task3_1(con)
    print('-' * 100)
    task3_2(con)
    print('-' * 100)

    task4_1(con, 10, 'Гинеколог', '2022-11-03')
    task4_2(con, '1944-01-01')

    con.close()