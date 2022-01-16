# Authors:
#   Wenhan TANG - 11/2020
#   ...
file_status = False 
def interpretor(cmd):
    global file_status
    if len(cmd.strip()) == 0:
        return "continue"
    
    if cmd.strip()[0] == "#":
        # check if the command is a comment
        return "continue"
    
    cmd_list = cmd.split("&:")
    assert len(cmd_list) == 2, "NGS interpretor: Syntax Error: " + cmd
    command = cmd_list[0].strip().lower()
    content = cmd_list[1].strip()

    # check if the  command can be recognized.
    assert command in ["open", "mod", "add", "del", "delg", "save"], "NGS interpretor: Command Error: " + command + " couldn't be recognized."
    # All the command except "open" can't be executed if no files are opened. 
    if command != "open":
        assert file_status, "NGS interpretor: No files are opened yet."

    # If command is "open", the file_status can be set to True, if the file couldn't be open normally, don't worry, the Error will be raised in other place.
    if command == "open":
        file_status = True

    return {"command": command, "content": content}
 
