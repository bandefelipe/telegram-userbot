{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.tesseract
  ];

  # Definindo o script principal
  entrypoint = "python3 userbot.py";
}