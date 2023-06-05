from winotify import Notification, audio
from os import getcwd

def show_one_hour_left_notification():
    one_hour_left_notification = Notification(app_id="Task Manager", 
                                            title = "Została godzina!", 
                                            msg = "Została godzina do końca deadline'u", 
                                            duration="short", 
                                            icon = f"{getcwd()}\static\calendar_icon.webp"
                                            )
    one_hour_left_notification.set_audio(audio.Default, loop=False)
    one_hour_left_notification.add_actions(label="Przejdź do strony", launch="http://localhost:5000/")
    one_hour_left_notification.show()
