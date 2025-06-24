from datetime import datetime

WAKEWORD = 'jarv'
STOPWORD = 'stop'


class Reminder:
    def __init__(self, message: str, time: datetime):
        self.message = message.lower()
        self.time = time

    def __repr__(self):
        return f"Reminder(message={self.message}, time={self.time})"
    
    def __eq__(self, other):
        if isinstance(other, Reminder):
            return self.message == other.message and self.time == other.time
        return False




class Reminders:
    reminders:list[Reminder]= []
    
    def __init__(self):
        self.reminders = []
    
    
    def load_reminder_from_file(self, file_path: str):
        try:
            with open(file_path, 'r') as file:
                self.reminders.clear()
                for line in file:
                    message, time_str = line.strip().split('|')
                    time = datetime.fromisoformat(time_str)
                    self.add_reminder(message, time)
            return "Reminders loaded successfully."
        except Exception as e:
            return f"Error loading reminders: {e}"
        
        
    def save_reminders_to_file(self, file_path: str):
        try:
            with open(file_path, 'a') as file:
                for reminder in self.reminders:
                    file.write(f"{reminder.message}|{reminder.time.isoformat()}\n")
            return "Reminders saved successfully."
        except Exception as e:
            return f"Error saving reminders: {e}"
    
    
    
    def __repr__(self):
        return f"Reminders(reminders={self.reminders})"
    
    def __eq__(self, other):
        if isinstance(other, Reminders):
            return self.reminders == other.reminders
        return False
    
    def add_reminder(self, message: str, time: datetime):
        reminder = Reminder(message, time)
        self.reminders.append(reminder)
        self.reminders.sort(key=lambda x: x.time)
        return f"Reminder added: {reminder}"
    
    def get_reminders(self):
        if not self.reminders:
            return "No reminders set."
        return "\n".join(str(reminder) for reminder in self.reminders)
    
    def remove_reminder(self, message: str):
        for reminder in self.reminders:
            if reminder.message == message:
                self.reminders.remove(reminder)
                return f"Removed reminder: {reminder}"
        return f"No reminder found with message: {message}"
    
    def clear_reminders(self):
        self.reminders.clear()
        return "All reminders cleared."
    
    def find_reminder_msg(self, message: str):
        import re
        message = message.lower()
        for reminder in self.reminders:
            if re.search(message, reminder.message, re.IGNORECASE) :
                return f"Found reminder: {reminder}"
        return "No matching reminder found."

    def find_reminder_time(self, time: datetime):
        for reminder in self.reminders:
            if reminder.time == time:
                return f"Found reminder: {reminder}"
        return "No matching reminder found."