import larktime

dtp = larktime.DateTimeParser()

while True:
    text = input('>>> ')

    print(dtp.parse(text))
