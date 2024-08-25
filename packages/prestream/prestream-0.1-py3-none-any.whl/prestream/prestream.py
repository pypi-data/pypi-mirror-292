import os
import sys
import subprocess

def clear_console():
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Linux, Termux
        os.system('clear')

def get_source_url(language):
    return input("Введите источник видео (например, YouTube): " if language == 'R' else "Enter the video source (e.g., YouTube): ").strip()

def run_streaming(language, method):
    if method == '1':
        format_option = input("Введите формат для `-f` (например, best): " if language == 'R' else "Enter the format for `-f` (e.g., best): ")
        source_url = get_source_url(language)
        url = input("Введите URL для онлайн стрима: " if language == 'R' else "Enter the URL for the online stream: ")
        stream_key = input("Введите ключ трансляции: " if language == 'R' else "Enter the stream key: ")
        command = f'yt-dlp -f {format_option} -o - {source_url} | ffmpeg -re -i - -c copy -f flv "{url}/{stream_key}"'
    else:
        video_input = input("Введите путь к файлу или его имя для офлайн стрима (в кавычках): " if language == 'R' else "Enter the file path or name for offline stream (in quotes): ")
        url = input("Введите URL для стрима: " if language == 'R' else "Enter the URL for the stream: ")
        stream_key = input("Введите ключ трансляции: " if language == 'R' else "Enter the stream key: ")
        command = f'ffmpeg -re -stream_loop -1 -i {video_input} -c:v libx264 -c:a aac -f flv "{url}/{stream_key}"'

    try:
        subprocess.run(command, shell=True)
    except KeyboardInterrupt:
        pass

def main():
    language = ''
    while language not in ['E', 'R']:
        language = input("Choose language/Выбери язык (E/R): ").strip().upper()
    
    while True:
        clear_console()
        method = ''
        while method not in ['1', '2']:
            method = input("Выберите метод стриминга (1 - Онлайн, 2 - Офлайн): " if language == 'R' else "Choose streaming method (1 - Online, 2 - Offline): ").strip()

        run_streaming(language, method)

        try:
            input()  # Wait for Ctrl+D or Ctrl+C
        except (EOFError, KeyboardInterrupt):
            choice = ''
            while choice not in ['Y', 'N']:
                choice = input("Продолжить работу со скриптом? (Y/N): " if language == 'R' else "Continue working with the script? (Y/N): ").strip().upper()
            if choice == 'N':
                clear_console()
                sys.exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_console()
        sys.exit()
