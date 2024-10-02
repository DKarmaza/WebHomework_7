from sqlalchemy import Column, Integer, String, ForeignKey, Date, CheckConstraint, create_engine, func
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from faker import Faker
from datetime import datetime
import random

Base = declarative_base()
#моделі для БД
class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    group_name = Column(String, nullable=False)

class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    course_name = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    teacher = relationship('Teacher', back_populates='courses')

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'))
    group = relationship('Group', back_populates='students')

class Grade(Base):
    __tablename__ = 'grades'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    grade = Column(Integer, CheckConstraint('grade >= 1 AND grade <= 100'), nullable=False)
    grade_date = Column(Date, nullable=False)
    student = relationship('Student', back_populates='grades')
    course = relationship('Course', back_populates='grades')

Teacher.courses = relationship('Course', order_by=Course.id, back_populates='teacher')
Student.grades = relationship('Grade', order_by=Grade.id, back_populates='student')
Group.students = relationship('Student', order_by=Student.id, back_populates='group')
Course.grades = relationship('Grade', order_by=Grade.id, back_populates='course')
#створення самої бази

engine = create_engine("sqlite:///dbhomework_2")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
fake = Faker()

def seed_data():

    groups = ['Group A', 'Group B', 'Group C']
    for group_name in groups:
        session.add(Group(group_name=group_name))
    session.commit()

    teachers = []
    for _ in range(4):
        teacher = Teacher(first_name=fake.first_name(), last_name=fake.last_name())
        session.add(teacher)
        teachers.append(teacher)
    session.commit()
    
    courses = ['Mathematics', 'Physics', 'History', 'Programming', 'Philosophy']
    for course_name in courses:
        teacher = random.choice(teachers)
        session.add(Course(course_name=course_name, teacher=teacher))
    session.commit()

    groups = session.query(Group).all()
    for _ in range(50):
        student = Student(first_name=fake.first_name(), last_name=fake.last_name(), group=random.choice(groups))
        session.add(student)
    session.commit()

    students = session.query(Student).all()
    courses = session.query(Course).all()
    for student in students:
        for course in courses:
            for _ in range(5):
                grade = random.randint(50, 100)
                grade_date = fake.date_between(start_date='-1y', end_date='today')
                session.add(Grade(student=student, course=course, grade=grade, grade_date=grade_date))
    session.commit()
#вибір данних

def select_1():
    return session.query(Student, func.avg(Grade.grade)).join(Grade).group_by(Student.id).order_by(func.avg(Grade.grade).desc()).limit(5).all()

def select_2(course_name):
    return session.query(Student, func.avg(Grade.grade)).join(Grade).join(Course).filter(Course.course_name == course_name).group_by(Student.id).order_by(func.avg(Grade.grade).desc()).first()

def select_3(course_name):
    return session.query(Group.group_name, func.avg(Grade.grade))\
        .select_from(Group)\
        .join(Student, Group.id == Student.group_id)\
        .join(Grade, Student.id == Grade.student_id)\
        .join(Course, Grade.course_id == Course.id)\
        .filter(Course.course_name == course_name)\
        .group_by(Group.id)\
        .all()

def select_4():
    return session.query(func.avg(Grade.grade)).scalar()

def select_5(teacher_id):
    return session.query(Course.course_name).filter(Course.teacher_id == teacher_id).all()

def select_6(group_name):
    return session.query(Student).join(Group).filter(Group.group_name == group_name).all()

def select_7(group_name, course_name):
    return session.query(Student, Grade.grade).join(Grade).join(Course).join(Group).filter(Group.group_name == group_name, Course.course_name == course_name).all()

def select_8(teacher_id):
    return session.query(func.avg(Grade.grade)).join(Course).filter(Course.teacher_id == teacher_id).scalar()

def select_9(student_id):
    return session.query(Course.course_name).join(Grade).filter(Grade.student_id == student_id).all()

def select_10(student_id, teacher_id):
    return session.query(Course.course_name).join(Grade).filter(Grade.student_id == student_id, Course.teacher_id == teacher_id).all()
#головна частина коду

if __name__ == "__main__":
    seed_data()

    print("Top 5 students by grades:")
    for student, avg_grade in select_1():
        print(f"\n {student.first_name} {student.last_name} - {avg_grade}")

    course_name = "Mathematics"
    print(f"\n Student with highest mark in {course_name}:")
    student, avg_grade = select_2(course_name)
    print(f"{student.first_name} {student.last_name} - {avg_grade}")

    print(f"\nAverage grades in groups for {course_name}:")
    for group_name, avg_grade in select_3(course_name):
        print(f"{group_name} - {avg_grade}")

    print(f"\nOverall average grade:")
    print(select_4())
