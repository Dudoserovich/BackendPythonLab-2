import sqlite3
from faker import Faker
from faker.generator import random
import datetime
from datetime import timedelta


def fake_spec(con: sqlite3.Connection) -> None:
    names = [
        'Терапевт',
        'Хирург',
        'Педиатр',
        'Гинеколог',
        'Психиатр-нарколог',
        'Невролог',
        'Офтальмолог',
        'Окулист',
        'Оториноларинголог'
    ]

    sql = """ 
    INSERT or ignore INTO specialization(name)
    VALUES(:name)
    """

    for name in names:
        cur = con.cursor()
        cur.execute(sql, {"name": name})
    con.commit()


def fake_place(con: sqlite3.Connection, count: int) -> None:
    sql = """ 
    INSERT or ignore INTO place(name)
    VALUES(:name)
    """

    nums = list(range(1, count+1))

    for i in range(len(nums)):
        cur = con.cursor()
        cur.execute(sql, {"name": 'Поликлиника №1, Кабинет №' + str(nums[i])})
    con.commit()


def fake_medicine(con: sqlite3.Connection, fake: Faker, count: int):
    sql = """ 
    INSERT or ignore INTO medicine(name, usage, actions, effects)
    VALUES(:name, :usage, :actions, :effects)
    """

    for i in range(count):
        name = fake.word()
        usage = fake.sentence(nb_words=10, variable_nb_words=False)
        actions = fake.sentence(nb_words=10, variable_nb_words=False)
        effects = fake.sentence(nb_words=10, variable_nb_words=False)

        cur = con.cursor()
        cur.execute(sql, {"name": name, "usage": usage, "actions": actions, "effects": effects})
    con.commit()


def fake_patient(con: sqlite3.Connection, fake: Faker, count: int):
    sql = """ 
    INSERT or ignore INTO patient(full_name, address, sex, birthday)
    VALUES(:full_name, :address, :sex, :birthday)
    """

    for i in range(count):
        profile = fake.simple_profile()

        cur = con.cursor()
        cur.execute(sql, {
            "full_name": profile['name'],
            "address": profile['address'],
            "sex": profile['sex'],
            "birthday": profile['birthdate']
        })
    con.commit()


def fake_doctor(con: sqlite3.Connection, fake: Faker, count: int):
    sql = """ 
    INSERT or ignore INTO doctor(spec_id, full_name, sex, address, phone, work_experience)
    VALUES(:spec_id, :full_name, :sex, :address, :phone, :work_experience)
    """

    cur = con.cursor()
    cur.execute("select id from specialization")

    specs = cur.fetchall()
    specIds = list(map(lambda x: x[0], specs))

    for i in range(count):
        profile = fake.simple_profile()

        cur = con.cursor()
        cur.execute(sql, {
            "spec_id": random.choice(specIds),
            "full_name": profile['name'],
            "sex": profile['sex'],
            "address": profile['address'],
            "phone": fake.phone_number(),
            "work_experience": random.randint(1, 8)
        })
    con.commit()


def fake_schedule(con: sqlite3.Connection, count: int):
    sql = """ 
    INSERT or ignore INTO schedule(s_date, starting, ending)
    VALUES(:s_date, :starting, :ending)
    """

    times = list(map(lambda hours: datetime.time(hours, 0), list(range(8, 20, 1))))

    for i in range(count):
        date = datetime.date.today() + timedelta(days=i)

        for time in times:
            cur = con.cursor()
            cur.execute(sql, {
                "s_date": date,
                "starting": time.hour,
                "ending": datetime.time(time.hour+1, 0).hour
            })
        con.commit()


def fake_doctor_schedule(con: sqlite3.Connection, count: int):
    sql = """ 
    INSERT or ignore INTO doctor_schedule(doctor_id, schedule_id, place_id)
    VALUES(:doctor_id, :schedule_id, :place_id)
    """

    cur = con.cursor()
    cur.execute("select id from place")
    places = cur.fetchall()
    placeIds = list(map(lambda x: x[0], places))

    cur = con.cursor()
    cur.execute("select id from doctor")
    doctors = cur.fetchall()
    doctorsIds = list(map(lambda x: x[0], doctors))

    for i in range(count):
        date = datetime.date.today() + timedelta(days=i)

        cur = con.cursor()
        cur.execute("select id from schedule where s_date=:date", {"date": date})
        schedules = cur.fetchall()
        schedulesIds = list(map(lambda x: x[0], schedules))

        for scheduleId in schedulesIds:

            j = 0
            for doctorId in doctorsIds:
                cur = con.cursor()
                cur.execute(sql, {
                    "doctor_id": doctorId,
                    "schedule_id": scheduleId,
                    "place_id": placeIds[j]
                })
                j += 1

            con.commit()


def fake_visit(con: sqlite3.Connection, fake: Faker, count: int):
    sql = """ 
    INSERT or ignore INTO visit(registration_id, patient_id, symptoms, diagnosis)
    VALUES(:registration_id, :patient_id, :symptoms, :diagnosis)
    """

    cur = con.cursor()
    cur.execute("select id from patient")
    patient = cur.fetchall()
    patientIds = list(map(lambda x: x[0], patient))

    cur = con.cursor()
    cur.execute("select id from doctor_schedule")
    registrations = cur.fetchall()
    registrationIds = list(map(lambda x: x[0], registrations))

    i = 0
    for patientId in patientIds[:count]:
        cur = con.cursor()
        cur.execute(sql, {
            "registration_id": registrationIds[i],
            "patient_id": patientId,
            "symptoms": fake.sentence(nb_words=10, variable_nb_words=False),
            "diagnosis": fake.sentence(nb_words=10, variable_nb_words=False)
        })
        i += 1
    con.commit()


def fake_appointment(con: sqlite3.Connection):
    sql = """ 
    INSERT or ignore INTO appointment(visit_id, medicine_id, amount)
    VALUES(:visit_id, :medicine_id, :amount)
    """

    cur = con.cursor()
    cur.execute("select id from visit")
    visit = cur.fetchall()
    visitIds = list(map(lambda x: x[0], visit))

    cur = con.cursor()
    cur.execute("select id from medicine")
    medicine = cur.fetchall()
    medicineIds = list(map(lambda x: x[0], medicine))

    for visitId in visitIds:
        cur = con.cursor()
        cur.execute(sql, {
            "visit_id": visitId,
            "medicine_id": random.choice(medicineIds),
            "amount": random.randint(1, 4)
        })
    con.commit()


def main():
    fake = Faker('ru_RU')
    con = sqlite3.connect("medicine.sqlite")

    fake_spec(con)
    fake_place(con, 10)
    fake_medicine(con, fake, 10)
    fake_patient(con, fake, 30)
    fake_doctor(con, fake, 10)
    fake_schedule(con, 10)

    # заполнение расписания на текущий день для всех врачей
    # Добавится 120 записей (10 врачей * 12 временных отрезков расписания)
    fake_doctor_schedule(con, 1)

    fake_visit(con, fake, 4)
    fake_appointment(con)

    con.close()


if __name__ == '__main__':
    main()