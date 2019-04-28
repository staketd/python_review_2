import app
from TOKEN import TOKEN


def main():
    app.init_bot(TOKEN)
    app.bot.polling()


if __name__ == '__main__':
    main()
