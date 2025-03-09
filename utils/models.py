class Student:
    def __init__(self, name, gpa, preferences):
        self.name = name
        self.gpa = gpa
        self.preferences = [pref.strip() for pref in preferences]  # Ordered list of preferred schools
        self.current_proposal = 0  # Index of the next school to propose

    def propose(self):
        if self.current_proposal < len(self.preferences):
            school = self.preferences[self.current_proposal]
            self.current_proposal += 1
            return school
        return None  # No more schools to propose


class School:
    def __init__(self, name, quota):
        self.name = name
        self.quota = quota
        self.accepted_students = []  # List of (gpa, student_name)
    
    def consider(self, student):
        self.accepted_students.append((student.gpa, student.name))
        self.accepted_students.sort(reverse=True, key=lambda x: x[0])  # Sort by GPA
        if len(self.accepted_students) > self.quota:
            return self.accepted_students.pop()  # Remove lowest-ranked student
        return None
