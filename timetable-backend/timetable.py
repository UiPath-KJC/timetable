import pandas as pd
import random

class Teacher:
    def __init__(self, teacher_id, name, subjects, preferred_sections, is_assistant=False, assigned_section=None):
        self.teacher_id = teacher_id
        self.name = name
        self.subjects = subjects
        self.preferred_sections = preferred_sections
        self.is_assistant = is_assistant
        self.assigned_section = assigned_section

class Subject:
    def __init__(self, subject_code, name, weekly_repetitions, is_practical, is_extracurricular):
        self.subject_code = subject_code
        self.name = name
        self.weekly_repetitions = weekly_repetitions
        self.is_practical = is_practical
        self.is_extracurricular = is_extracurricular

class Section:
    def __init__(self, section_id, name, students, batch):
        self.section_id = section_id
        self.name = name
        self.students = students
        self.batch = batch

class Timetable:
    def __init__(self, teachers, subjects, sections):
        self.teachers = teachers
        self.sections = sections
        self.subjects = subjects
        self.teacher_timetable = {}
        self.section_timetable = {}
        self.total_classes = 0

        # Initialize teacher timetable
        for teacher in self.teachers:
            self.teacher_timetable[teacher.teacher_id] = {day: {period: None for period in range(1, 8)} for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}
        
        # Initialize section timetable
        for section in self.sections:
            self.section_timetable[section.section_id] = {day: {period: None for period in range(1, 8)} for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}

    def add_class(self, teacher_id, section_id, subject_code, day, period):
        if self.teacher_timetable[teacher_id][day][period] is not None:
            raise ValueError(f"Teacher {teacher_id} is already assigned a class for {day} period {period}")

        if self.section_timetable[section_id][day][period] is not None:
            raise ValueError(f"Section {section_id} is already assigned a class for {day} period {period}")

        self.total_classes += 1
        self.teacher_timetable[teacher_id][day][period] = (section_id, subject_code)
        self.section_timetable[section_id][day][period] = (subject_code, teacher_id)

    def get_section_batch(self, section):
        return [1, 2, 3, 4] if section.batch == 0 else [5, 6, 7, 8]

    def get_subject(self, subject_code):
        for subject in self.subjects:
            if subject.subject_code == subject_code:
                return subject
        return None

    def get_required_subject(self, section, day, period):
        required_subjects = []
        section_timetable = self.section_timetable[section.section_id]

        for subject in self.subjects:
            is_taught_on_day = any(subject.subject_code in classes for classes in section_timetable.get(day, {}).values() if classes)
            if not is_taught_on_day:
                subject_count = sum(subject.subject_code in classes for week_day in section_timetable for classes in section_timetable.get(week_day, {}).values() if classes)
                if subject_count < subject.weekly_repetitions:
                    required_subjects.append(subject.subject_code)

        return required_subjects

    def is_teacher_available(self, teacher_id, day, period):
        return self.teacher_timetable[teacher_id][day][period] is None

    def find_suitable_teacher(self, subject_code, section, day, period, is_assistant=False):
        for teacher in self.teachers:
            subject = self.get_subject(subject_code)
            if subject.is_extracurricular and teacher.assigned_section and section.section_id in teacher.assigned_section and self.is_teacher_available(teacher.teacher_id, day, period):
                return teacher.teacher_id

            if subject_code in teacher.subjects and section.section_id in teacher.preferred_sections and self.is_teacher_available(teacher.teacher_id, day, period) and teacher.is_assistant == is_assistant:
                return teacher.teacher_id
        return None

    def handle_practical_subject(self, section, day, period, subject_code):
        main_teacher_id = self.find_suitable_teacher(subject_code, section, day, period, False)
        if not main_teacher_id:
            return False

        if period == 7:  # Ensure practicals don't spill over to the next day
            return False

        assistant_teacher_id = self.find_suitable_teacher(subject_code, section, day, period + 1, True)
        if not assistant_teacher_id:
            return False

        if not self.is_teacher_available(main_teacher_id, day, period + 1) or not self.is_teacher_available(assistant_teacher_id, day, period):
            return False

        practical_teachers = f"{main_teacher_id} & {assistant_teacher_id}"
        self.teacher_timetable[main_teacher_id][day][period] = (section.section_id, subject_code)
        self.teacher_timetable[main_teacher_id][day][period + 1] = (section.section_id, subject_code)
        self.teacher_timetable[assistant_teacher_id][day][period] = (section.section_id, subject_code)
        self.teacher_timetable[assistant_teacher_id][day][period + 1] = (section.section_id, subject_code)

        self.section_timetable[section.section_id][day][period] = (subject_code, practical_teachers)
        self.section_timetable[section.section_id][day][period + 1] = (subject_code, practical_teachers)

        self.total_classes += 2
        return True

    def allocate_classes(self):
        for section in self.sections:
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            for day in days:
                # Ensure 2 to 7 classes per day
                periods = list(range(1, 8))
                random.shuffle(periods)
                num_classes = random.randint(2, 7)
                allocated_periods = periods[:num_classes]

                for period in allocated_periods:
                    if period not in self.get_section_batch(section):
                        continue

                    required_subjects = self.get_required_subject(section, day, period)
                    subject_dict = {subject.subject_code: subject for subject in self.subjects}
                    for subject_code in required_subjects:
                        subject = subject_dict[subject_code]
                        if subject.is_practical:
                            if (section.batch == 0 and period == 4) or (section.batch == 1 and period == 7):
                                continue
                            success = self.handle_practical_subject(section, day, period, subject_code)
                            if success:
                                break
                        else:
                            teacher_id = self.find_suitable_teacher(subject_code, section, day, period, False)
                            if teacher_id:
                                try:
                                    self.add_class(teacher_id, section.section_id, subject_code, day, period)
                                    break
                                except ValueError as e:
                                    print(f"Skipping: {e}")
                                    continue

    def generate_timetable(self):
        self.allocate_classes()
        return self.teacher_timetable, self.section_timetable

def timetable_to_excel(teacher_timetable, section_timetable):
    # Create an Excel writer object
    with pd.ExcelWriter('timetable.xlsx', engine='openpyxl') as writer:
        # Create a sheet for each teacher
        for teacher_id, timetable in teacher_timetable.items():
            if teacher_id == "T8":
                continue

            # Prepare a DataFrame for teacher timetable
            teacher_df_list = []
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                periods = [None] * 7
                for period in range(1, 8):
                    class_info = timetable[day].get(period, None)
                    if class_info is not None:
                        section_id, subject_code = class_info
                        periods[period - 1] = f"{section_id} - {subject_code}"
                    else:
                        periods[period - 1] = ""
                teacher_df_list.append({'Day': day, **{f'Period_{i+1}': periods[i] for i in range(7)}})
            
            teacher_df = pd.DataFrame(teacher_df_list)
            teacher_df.to_excel(writer, sheet_name=f'Teacher_{teacher_id}', index=False)

        # Create a sheet for each section
        for section_id, timetable in section_timetable.items():
            # Prepare a DataFrame for section timetable
            section_df_list = []
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                periods = [None] * 7
                for period in range(1, 8):
                    class_info = timetable[day].get(period, None)
                    if class_info is not None:
                        subject_code, teacher_id = class_info
                        periods[period - 1] = f"{subject_code} - {teacher_id}"
                    else:
                        periods[period - 1] = ""
                section_df_list.append({'Day': day, **{f'Period_{i+1}': periods[i] for i in range(7)}})
            
            section_df = pd.DataFrame(section_df_list)
            section_df.to_excel(writer, sheet_name=f'Section_{section_id}', index=False)

# Example usage:
teachers = [
    Teacher('T1', 'Teacher 1', ['S1', 'S2'], ['SecA', 'SecB']),
    Teacher('T2', 'Teacher 2', ['S2', 'S3'], ['SecB']),
    Teacher('T3', 'Teacher 3', ['S1', 'S4'], ['SecC']),
    Teacher('T4', 'Teacher 4', ['S3', 'S4'], ['SecD']),
    Teacher('T5', 'Teacher 5', ['S5', 'S6'], ['SecE']),
    Teacher('T6', 'Teacher 6', ['S5', 'S7'], ['SecF']),
    Teacher('T7', 'Teacher 7', ['S6', 'S8'], ['SecA']),
    Teacher('T8', 'Teacher 8', ['S7', 'S8'], ['SecB'], is_assistant=True)
]

subjects = [
    Subject('S1', 'Subject 1', 3, False, False),
    Subject('S2', 'Subject 2', 2, False, False),
    Subject('S3', 'Subject 3', 3, True, False),
    Subject('S4', 'Subject 4', 2, True, False),
    Subject('S5', 'Subject 5', 1, False, True),
    Subject('S6', 'Subject 6', 4, False, False),
    Subject('S7', 'Subject 7', 3, False, False),
    Subject('S8', 'Subject 8', 2, False, True)
]

sections = [
    Section('SecA', 'Section A', 30, 0),
    Section('SecB', 'Section B', 30, 0),
    Section('SecC', 'Section C', 30, 1),
    Section('SecD', 'Section D', 30, 1),
    Section('SecE', 'Section E', 30, 0),
    Section('SecF', 'Section F', 30, 1)
]

timetable = Timetable(teachers, subjects, sections)
teacher_timetable, section_timetable = timetable.generate_timetable()
timetable_to_excel(teacher_timetable, section_timetable)
