from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Функция-обработчик команды /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет, я простой бот! Как дела, ?')


# Функция-обработчик команды /help
def help_command(update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Я могу помочь с простыми вопросами. Задавай, вопрос!')
def rad_command(update: Update, context: CallbackContext)-> None:
    update.message.reply_text('my creator by Devcooder')


def main():
    # Вставь свой токен сюда
    updater = Updater("test")


    # Регистрация обработчиков
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("help", help_command))
    updater.dispatcher.add_handler(CommandHandler("rad", rad_command))


    # Запуск бота
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
