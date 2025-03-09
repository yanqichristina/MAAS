def deferred_acceptance(students, schools):
    unmatched_students = list(students.values())
    
    while unmatched_students:
        student = unmatched_students.pop(0)
        school_name = student.propose()
        if school_name is not None:
            removed_student = schools[school_name].consider(student)
            if removed_student:
                unmatched_students.append(students[removed_student[1]])
    
    student_assignments = {s.name: None for s in students.values()}
    school_enrollments = {school.name: [] for school in schools.values()}
    
    for school in schools.values():
        for gpa, student_name in school.accepted_students:
            student_assignments[student_name] = school.name
            school_enrollments[school.name].append(student_name)
    
    return student_assignments, school_enrollments
