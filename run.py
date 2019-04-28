import app
from TOKEN import TOKEN
import os


def main():
    port = int(os.environ.get("PORT", 5000))
    app.init_bot(TOKEN)
    app.bot.polling()


if __name__ == '__main__':
    main()