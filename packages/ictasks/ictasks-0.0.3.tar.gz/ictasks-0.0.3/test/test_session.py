from ictasks.session import Session


def test_taskfarm_session():

    job_id = "1234"
    nodelist = "localhost"

    session = Session(job_id, nodelist)
    session.tasklist = "echo 'hello from task 1'\necho 'hello from task 2'"
    session.settings.set("keep", True)
    #session.run()
