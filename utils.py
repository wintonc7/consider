import model


def get_role(user):
    """
    Checks and returns if the user is an Instructor or a Student, False if neither.

    Args:
        user: The user whose role is to be retrieved.

    Returns: Instructor or Student or False.

    """
    if user:
        result = model.Instructor.query(model.Instructor.email == user.email().lower()).get()
        if result:
            return result
        else:
            result = model.Student.query(model.Student.email == user.email().lower()).get()
            if result:
                return result
    return False


def get_courses_and_sections(result, course_name, selected_section):
    """

    Args:
        result:
        course_name:
        selected_section:

    Returns:
        object:

    """
    template_values = {}
    courses = model.Course.query(ancestor=result.key).fetch()
    if courses:
        course = None
        template_values['courses'] = courses
        if course_name:
            course_name = course_name.upper()
            course = model.Course.get_by_id(course_name, parent=result.key)
        if not course:
            course = courses[0]
        sections = model.Section.query(ancestor=course.key).fetch()
        template_values['selectedCourse'] = course.name
        if not sections and not course_name:
            sections = model.Section.query(ancestor=courses[0].key).fetch()
        template_values['sections'] = sections
        if sections:
            section = None
            if selected_section:
                selected_section = selected_section.upper()
                section = model.Section.get_by_id(selected_section, parent=course.key)
            if not section:
                section = sections[0]
            template_values['selectedSection'] = section.name
            template_values['selectedSectionObject'] = section
            template_values['students'] = section.students
    return template_values


def check_response(response):
    """

    Args:
        response:

    Returns:

    """
    for i in range(1, len(response)):
        if response[i] not in ['support', 'neutral', 'disagree']:
            return True
    return False
