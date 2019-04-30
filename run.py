import app

if __name__ == '__main__':
    app.bot.remove_webhook()
    app.bot.polling()