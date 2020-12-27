import input_output_system.telegram_bot as tg_bot
import input_output_system.dialogs as dialogsf
import time_manager.clock as clock

print("starting...")
rt = clock.repeated_timer(30, clock.alarm)
bot = tg_bot.bot(dialogsf.dialog_with_customer,dialogsf.dialog_about_create_course,dialogsf.dialog_about_lern_course)
bot.start()

