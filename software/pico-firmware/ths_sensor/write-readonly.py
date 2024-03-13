# If you accidentally turn the device onto readonly mode, you can use this to attempt to switch off that setting

with open("code.py", "r") as file:
    file_contents = file.read()

file_contents = file_contents.replace(
    '"import_errors.log", "a"', '"import_errors.log", "w"'
)

with open("code.py", "w") as file:
    file.write(file_contents)


with open("boot.py", "r") as file:
    file_contents = file.read()

file_contents = file_contents.replace("readonly=False", "readonly=True")

with open("boot.py", "w") as file:
    file.write(file_contents)
