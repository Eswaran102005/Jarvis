from features.voice import speak, listen

speak("Hello, I am working")

command = listen()
print("You said:", command)