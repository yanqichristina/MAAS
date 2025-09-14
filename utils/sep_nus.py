import streamlit as st
import pandas as pd

class Student:
    def __init__(self, name, gpa, total_score, major, seniority, nationality, preferences): # preferences is a list of [schoolname, semester]
        self.name = name
        self.gpa = gpa
        self.total_score = total_score
        self.major = major
        self.seniority = seniority
        self.nationality = nationality
        self.preferences = preferences  # Ordered list of preferred schools and study semesters
        self.current_proposal = 0  # Index of the next school to propose

    def propose(self):
        if self.current_proposal < len(self.preferences):
            school = self.preferences[self.current_proposal][0]  # Get the school name
            self.current_proposal += 1
            return school
        return None  # No more schools to propose


class Program:
    def __init__(self, schoolName, sem, major_incl, major_excl, quota, minGPA, seniority, nationality_excl):
        self.schoolName = schoolName
        self.sem = sem
        self.major_incl = major_incl
        self.major_excl = major_excl
        self.quota = quota
        self.minGPA = minGPA
        self.seniority = seniority
        self.nationality_excl = nationality_excl
        self.accepted_students = []  # List of (totalScore, student_name)
    
    def consider(self, student):
        # Check if student meets study semester requirement
        if (
            not pd.isna(self.sem) and 
            student.preferences[student.current_proposal - 1][1] != 'Any available semester' and 
            student.preferences[student.current_proposal - 1][1] != self.sem
        ):
            rejected_reason = f"semester requirement not met"
            return (student.total_score, student.name), rejected_reason  # Student does not meet semester requirement

        # Check if student meets major requirements
        if self.major_incl != [] and student.major not in self.major_incl:
            rejected_reason = f"major requirement not met"
            return (student.total_score, student.name), rejected_reason  # Student does not meet major requirement
        
        if self.major_excl != [] and student.major in self.major_excl:
            rejected_reason = f"major requirement not met"
            return (student.total_score, student.name), rejected_reason  # Student does not meet major requirement
        
        # Check if student meets minimum GPA requirement
        if not pd.isna(self.minGPA) and student.gpa < self.minGPA:
            rejected_reason = f"minimum GPA {self.minGPA} not met"
            return (student.total_score, student.name), rejected_reason  # Student does not meet GPA requirement

        # Check if student meets seniority requirement
        if not pd.isna(self.seniority) and student.seniority != self.seniority:
            rejected_reason = f"seniority requirement not met"
            return (student.total_score, student.name), rejected_reason  # Student does not meet seniority requirement
        
        # Check if student meets nationality requirement
        if self.nationality_excl != [] and student.nationality in self.nationality_excl:
            rejected_reason = f"nationality requirement not met"
            return (student.total_score, student.name), rejected_reason  # Student does not meet seniority requirement

        # Compare student's total score with accepted students
        self.accepted_students.append((student.total_score, student.name))
        self.accepted_students.sort(reverse=True, key=lambda x: x[0])  # Sort by total score in descending order
        # Remove the lowest-ranked student if quota is reached
        if len(self.accepted_students) > self.quota:
            rejected_reason = f"maximum quota {self.quota} reached. Accepted students: {[(name, total_score) for total_score, name in self.accepted_students[:-1]]}"
            return self.accepted_students.pop(), rejected_reason  # Remove lowest-ranked student
        return None, None  # No student removed

def deferred_acceptance(students, programs):
    unmatched_students = list(students.values())

    # Create a DataFrame to record the matching process
    columns = ['Student Name', 'Total Score', 'Action', 'Choice Number', 'School Name', 'Reason']
    matching_process_df = pd.DataFrame(columns=columns)

    with st.expander("See detailed matching process"):
        with st.container(height=300, border=False):
            # st.write("Deferred Acceptance Algorithm:")
            st.divider()
            
            while len(unmatched_students)>0:
                student = unmatched_students.pop(0)
                school_name = student.propose()
                if school_name is not None:
                    # Record the proposal action
                    new_row = {
                        'Student Name': student.name,
                        'Total Score': student.total_score,
                        'Action': 'proposed to',
                        'Choice Number': student.current_proposal,
                        'School Name': school_name,
                        'Reason': None
                    }

                    if matching_process_df.empty:
                        matching_process_df = pd.DataFrame([new_row], columns=columns)
                    else:
                        matching_process_df = pd.concat([matching_process_df, pd.DataFrame([new_row])], ignore_index=True)
                    st.write(f"{student.name} propose to Choice {student.current_proposal} -- {school_name}")
                    
                    # loop through all programs offered by the school, and consider the student for each one
                    accepted = False
                    for programID, program in programs.items():
                        if program.schoolName == school_name:
                            # st.write(program)
                            removed_student, rejected_reason = program.consider(student)
                            if removed_student is None:
                                accepted = True
                                break 
                            if removed_student:
                                # Record the rejection action     
                                new_row = {
                                    'Student Name': removed_student[1],
                                    'Total Score': removed_student[0],
                                    'Action': 'rejected by',
                                    'Choice Number': None,
                                    'School Name': school_name + f' ProgramID: {programID}',
                                    'Reason': rejected_reason
                                }
                                matching_process_df = pd.concat([matching_process_df, pd.DataFrame([new_row])], ignore_index=True)
                                st.write(f"{removed_student[1]} (GPA:{removed_student[0]}) is rejected by {school_name} because {rejected_reason}")

                                if removed_student[1] != student.name:
                                    unmatched_students.append(students[removed_student[1]])
                                    accepted = True
                                    break  # If the proposing student is not rejected, stop considering other programs

                    if not accepted:
                        unmatched_students.append(student)
                    
    
    student_assignments = {s.name: None for s in students.values()}
    program_enrollments = {programID: [] for programID in programs.keys()}
    
    for programID, program in programs.items():
        for totalScore, student_name in program.accepted_students:
            student_assignments[student_name] = programID
            program_enrollments[programID].append(student_name)
    
    return student_assignments, program_enrollments, matching_process_df