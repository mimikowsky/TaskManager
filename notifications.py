from winotify import Notification, audio, Notifier
from os import getcwd


def show_notification(task, title, message):
    one_hour_left_notification = Notification(app_id="Task Manager", 
                                            title = title, 
                                            msg = message, 
                                            duration="short", 
                                            icon = f"{getcwd()}\static\calendar_icon.webp"
                                            )
    one_hour_left_notification.set_audio(audio.Default, loop=False)
    one_hour_left_notification.add_actions(label="Przejdź do strony", launch=f"http://localhost:5000/task/{task.id}")
    one_hour_left_notification.show()



