from pprint import pprint

class Teacher:
    """Represents a teacher with details like ID, name, subjects, preferences, and timetable."""
    def __init__(self, teacher_id, name, subjects, preferred_sections, is_assistant=False, assigned_section=None):
        """
        Initializes a Teacher object with the provided details.

        Args:
            teacher_id (str): Unique identifier for the teacher.
            name (str): Name of the teacher.
            subjects (list): List of subject codes the teacher can teach.
            preferred_sections (list): List of preferred section IDs.
            is_assistant (bool, optional): Flag indicating if the teacher is an assistant. Defaults to False.
        """
        self.teacher_id = teacher_id  # Unique identifier for the teacher
        self.name = name  # Name of the teacher
        self.subjects = subjects  # List of subjects the teacher can teach
        self.preferred_sections = preferred_sections  # List of preferred sections
        self.is_assistant = is_assistant  # Flag indicating if the teacher is an assistant
        self.assigned_section = assigned_section  # Section ID if the teacher is a class animator

class Subject:
    """Represents a subject with details like code, name, repetitions, and type."""
    def __init__(self, subject_code, name, weekly_repetitions, is_practical, is_extracurricular):
        """
        Initializes a Subject object with the provided details.

        Args:
            subject_code (str): Unique code for the subject.
            name (str): Name of the subject.
            weekly_repetitions (int): Number of times the subject should be taught per week.
            is_practical (bool): Flag indicating if the subject is practical.
            is_extracurricular (bool): Flag indicating if the subject is extracurricular.
        """
        self.subject_code = subject_code  # Unique code for the subject
        self.name = name  # Name of the subject
        self.weekly_repetitions = weekly_repetitions  # Number of times the subject should be taught per week
        self.is_practical = is_practical  # Flag indicating if the subject is practical
        self.is_extracurricular = is_extracurricular  # Flag indicating if the subject is (eg. CA) extracurricular

class Section:
    """Represents a section with details like ID, name, students, batch, and timetable."""
    def __init__(self, section_id, name, students, batch):
        """
        Initializes a Section object with the provided details.

        Args:
            section_id (str): Unique identifier for the section.
            name (str): Name of the section.
            students (list): List of student names in the section.
            batch (int): Batch of the section (0 for morning, 1 for evening).
        """
        self.section_id = section_id  # Unique identifier for the section
        self.name = name  # Name of the section
        self.students = students  # List of students in the section
        self.batch = batch  # Batch of the section (0 for morning, 1 for evening)

class Timetable:
    def __init__(self, teachers,subjects, sections):
        """Initializes a Timetable object with teacher, section, and subject data.

        Args:
            teachers (list): List of Teacher objects.
            sections (list): List of Section objects.
            subjects (list): List of Subject objects.
        """
        self.teachers = teachers
        self.sections = sections
        self.subjects = subjects
        self.teacher_timetable = {}
        self.section_timetable = {}

        self.total_classes = 0 #Total needed classes - (4 subjects * 3 rep + 1 Practical * 2 rep )/Per section(4 Sections ) = 56

        # Initialize teacher and section timetables
        for teacher in self.teachers:
            self.teacher_timetable[teacher.teacher_id] = {}
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                self.teacher_timetable[teacher.teacher_id][day] = {}
                for period in range(1, 9):
                    self.teacher_timetable[teacher.teacher_id][day][period] = None
        
        for section in self.sections:
            self.section_timetable[section.section_id] = {}
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                self.section_timetable[section.section_id][day] = {}
                for period in range(1, 9):
                    self.section_timetable[section.section_id][day][period] = None

    def add_class(self, teacher_id, section_id, subject_code, day, period):
        """Adds a class to the teacher and section timetables.

        Args:
            teacher_id (str): ID of the teacher assigned the class.
            section_id (str): ID of the section taking the class.
            subject_code (str): Code of the subject being assigned.
            day (str): Day of the week for the class.
            period (int): Period number for the class.

        Raises:
            ValueError: If the class is already assigned to the teacher or section.
        """

        # Check if the class is already assigned to the teacher
        if self.teacher_timetable[teacher_id][day].get(period) is not None:
            raise ValueError(f"Teacher {teacher_id} is already assigned a class for {day} period {period}")

        # Check if the class is already assigned to the section
        if self.section_timetable[section_id][day].get(period) is not None:
            raise ValueError(f"Section {section_id} is already assigned a class for {day} period {period}")

        self.total_classes+=1

        # Update teacher timetable
        self.teacher_timetable[teacher_id][day][period] = (section_id, subject_code)

        # Update section timetable
        self.section_timetable[section_id][day][period] = (subject_code, teacher_id)

    def get_section_batch(self,section):
        """Returns the batch (morning/evening) of a section."""
        return [1,2,3,4] if section.batch == 0 else [5,6,7,8]
    
    def get_subject(self, subject_code):
        """Retrieves a subject object based on its subject code.

        Args:
            subject_code (str): The code of the subject to retrieve.

        Returns:
            Subject: The subject object if found, otherwise None.
        """

        for subject in self.subjects:
            if subject.subject_code == subject_code:
                return subject
        return None


    def get_required_subject(self,section, day, period):

        """Determines required subjects for a section based on weekly repetitions."""
        required_subjects = []
        section_timetable = self.section_timetable[section.section_id]  # Access section timetable through Timetable instance

        for subject in self.subjects:

            # To check the subject is taught or not on a particular day 
            is_taught_on_day = False
            for classes in section_timetable.get(day, {}).values():
                if classes is not None and subject.subject_code in classes:
                    is_taught_on_day=True
            
            if not is_taught_on_day:  # Check if subject not assigned for the day
                # To check how many times the particular subject is taught in a week
                subject_count = 0
                for week_day in section_timetable:
                    for classes in section_timetable.get(week_day, {}).values():
                        if classes is not None and subject.subject_code in classes :
                            subject_count+=1
                if subject_count < subject.weekly_repetitions:  # Check if required repetitions not met
                    required_subjects.append(subject.subject_code)

        return required_subjects

    def is_teacher_available(self,teacher_id, day, period):
        """Checks if a teacher is available for a given day and period."""
        
        return self.teacher_timetable[teacher_id][day].get(period) is None  # Check if the period is free

    def find_suitable_teacher(self,subject_code, section, day, period, is_assistant=False):
        """Finds a suitable teacher for a given subject, section, day, and period."""
        for teacher in self.teachers:

            subject = self.get_subject(subject_code)

            # Check if the subject is extracurricular and for class animator
            if subject.is_extracurricular and teacher.assigned_section and section.section_id in teacher.assigned_section and self.is_teacher_available(teacher.teacher_id, day, period):
                return teacher.teacher_id
        
            if subject_code in teacher.subjects and \
            section.section_id in teacher.preferred_sections and \
            self.is_teacher_available(teacher.teacher_id, day, period) and \
            teacher.is_assistant == is_assistant:
                return teacher.teacher_id
        return None  # Return None if no suitable teacher found

    def handle_practical_subject(self, section, day, period, subject_code):
        """Handles allocation of practical subjects with main and assistant teachers.

        Args:
            section (Section): Section object for which the subject is being assigned.
            day (str): Day of the week.
            period (int): Period number.
            subject_code (str): Code of the practical subject.

        Returns:
            bool: True if successful, False otherwise.
        """

        # Find main teacher
        main_teacher_id = self.find_suitable_teacher(subject_code, section, day, period, False)
        if not main_teacher_id:
            return False

        # Find assistant teacher
        assistant_teacher_id = self.find_suitable_teacher(subject_code, section, day, period + 1, True)
        if not assistant_teacher_id:
            return False

        # Combine teacher IDs
        practical_teachers = f"{main_teacher_id} & {assistant_teacher_id}"

        # Update teacher timetables
        self.teacher_timetable[main_teacher_id][day][period] = (section.section_id, subject_code)
        self.teacher_timetable[main_teacher_id][day][period + 1] = (section.section_id, subject_code)
        self.teacher_timetable[assistant_teacher_id][day][period] = (section.section_id, subject_code)
        self.teacher_timetable[assistant_teacher_id][day][period + 1] = (section.section_id, subject_code)

        # Update section timetable
        self.section_timetable[section.section_id][day][period] = (subject_code, practical_teachers)
        self.section_timetable[section.section_id][day][period + 1] = (subject_code, practical_teachers)

        self.total_classes+=2

        return True


    def generate_timetable(self):

        for section in self.sections:
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                period = 1
                while period<9:  # Assuming 8 periods per day

                    period_consumed = 1
                    # Check the batch 
                    if period not in self.get_section_batch(section):
                        period+=period_consumed
                        continue
                        
                    required_subjects = self.get_required_subject(section, day, period)
                    subject_dict = {subject.subject_code: subject for subject in self.subjects}
                    for subject_code in required_subjects:

                        subject = subject_dict[subject_code]  # Access subject using dictionary
                        if subject.is_practical:
                            # Iterating to next subject if 2 period are not free for practical
                            if (section.batch == 0 and period == 4) or (section.batch == 1 and period == 8 ):
                                continue
                            success = self.handle_practical_subject(section, day, period, subject_code)
                            if success:
                                period_consumed += 1
                                break
                        else:
                            teacher_id = self.find_suitable_teacher(subject_code, section, day, period, False)
                            if teacher_id:
                                self.add_class(teacher_id, section.section_id, subject_code, day, period)
                                break
                    period += period_consumed
        return timetable


# Sample data
teachers = [
    Teacher("T1", "Teacher 1", ["M", "S","S-P"], ["A", "B"], False , ["A"]),
    Teacher("T2", "Teacher 2", ["M", "S","S-P"], ["C", "D"], False , ["B"]),
    Teacher("T3", "Teacher 3", ["M", "S","S-P"], ["A", "B","E"], True),  # Assistant teacher
    Teacher("T4", "Teacher 4", ["M", "S","S-P"], ["C", "D","F"], True),  # Assistant teacher
    Teacher("T5", "Teacher 5", ["E", "H"], ["A", "B"], False , ["C"]),
    Teacher("T6", "Teacher 6", ["E", "H"], ["C", "D"], False , ["D"]),
    Teacher("T7", "Teacher 7", ["M", "S","S-P"], ["E", "F"], False , ["E"]),
    Teacher("T8", "Teacher 8", ["E", "H"], ["E", "F"], False , ["F"]),
]

subjects = [
    Subject("M", "Math", 3, False, False),
    Subject("H", "History", 3, False, False),
    Subject("S-P", "Science_Practical", 2, True, False),
    Subject("CA", "Current_Affair", 1, False, True),
    Subject("S", "Science", 3, False, False),
    Subject("E", "English", 3, False, False),
]

sections = [
    Section("A", "Section A", ["Student1", "Student2"], 0),  # Morning section
    Section("B", "Section B", ["Student3", "Student4"], 1),  # Evening section
    Section("C", "Section C", ["Student1", "Student2"], 0),
    Section("D", "Section D", ["Student1", "Student2"], 1),
    Section("E", "Section E", ["Student1", "Student2"], 0),
    Section("F", "Section F", ["Student1", "Student2"], 1)
]

# Create a timetable object
timetable = Timetable(teachers,subjects, sections)

# Generate the timetable
timetable.generate_timetable()

# Printing sections Timetable
for sec in sections:
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        print("\nSection - " , sec.name , " and Day - ",day,"\n")
        pprint(timetable.section_timetable[sec.section_id][day])

# Printing Teachers Timetable
# for tec in teachers:
#     for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
#         print("\nTeacher Name - " , tec.name , " and Day - ",day,"\n")
#         pprint(timetable.teacher_timetable[tec.teacher_id][day])


print("Total classes Expected for 6 Section - 90 and Total classes Occuring - " , timetable.total_classes)
