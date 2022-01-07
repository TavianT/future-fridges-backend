from datetime import datetime
import os
class ActivityLog():
    LOG_PATH = "./logs/"

    def getCurrentFilePath():
        current_date = datetime.now().strftime('%d_%m_%Y')
        file_name = f'activity_log_{current_date}.txt'
        return os.path.join(ActivityLog.LOG_PATH, file_name)
    
    def writeToLogFile(str_to_write):
        current_time = datetime.now().strftime("%H:%M:%S")
        str_to_write = f'{current_time}: {str_to_write}'
        file_path = ActivityLog.getCurrentFilePath()
        with open (file_path, 'a') as log_file:
            log_file.write(str_to_write)

    def writeUpdateFridgeContentActivityToLog(fridge_content, old_quantity):
        str_to_write = ''
        if old_quantity < fridge_content.quantity:
            str_to_write = f'{fridge_content.last_inserted_by.name} has added {fridge_content.item.name} to the fridge increasing the quantity to {fridge_content.quantity}\n'
        else:
            str_to_write = f'{fridge_content.last_inserted_by.name} has removed {fridge_content.item.name} from the fridge decreasing the quantity to {fridge_content.quantity}\n'
        ActivityLog.writeToLogFile(str_to_write)
        
            
    def writeNewFridgeContentActivityToLog(fridge_content):
        expiration_date = fridge_content.expiration_date.strftime('%d/%m/%Y')
        str_to_write = f'{fridge_content.last_inserted_by.name} has inserted {fridge_content.item.name} into the fridge with a quantity of {fridge_content.quantity} - it expires on {expiration_date}\n'
        ActivityLog.writeToLogFile(str_to_write)