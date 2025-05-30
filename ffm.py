import ffmpeg

path_to_video = 'D:\SELF\programming\VocabularyApp\The.AmazingThe.Amazing.World.of.Gumball.S01E01E02.The Responsible. The DVD'

# Команда для витягування субтитрів з відео в змінну
out, err = ffmpeg.input(path_to_video).output('pipe:1').run(capture_stdout=True, capture_stderr=True)

# Перетворюємо байти в рядок (UTF-8)
subtitles = out.decode('utf-8')

# Вивести субтитри
print(subtitles)
