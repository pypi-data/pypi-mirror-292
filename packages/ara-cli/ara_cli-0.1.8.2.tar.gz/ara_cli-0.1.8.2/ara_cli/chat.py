import os
import glob
import cmd2
from os import sys
from ara_cli.prompt_handler import send_prompt
from ara_cli.prompt_extractor import extract_responses
from ara_cli.directory_navigator import DirectoryNavigator
from ara_cli.prompt_handler import load_givens
from ara_cli.template_manager import TemplatePathManager
from ara_cli.ara_config import ConfigManager


class Chat(cmd2.Cmd):
    CATEGORY_CHAT_CONTROL = "Chat control commands"

    INTRO = """/***************************************/
                 araarar        
               aa       ara      
             aa    aa   aara     
             a        araarar    
             a        ar  ar     
           aa          ara     
          a               a     
          a               aa    
           a              a     
   ar      aa           aa     
    (c) ara chat by talsen team     
              aa      aa       
               aa    a         
                a aa          
                 aa    
/***************************************/
Start chatting (type 'HELP'/'h' for available commands, 'QUIT'/'q' to exit chat mode):"""

    def __init__(self, chat_name, reset=None):
        super().__init__(
            allow_cli_args=False,
            )
        self.prompt = "ara> "
        self.create_default_aliases()
        self.intro = Chat.INTRO

        self.default_chat_content = "# ara prompt:\n"
        self.chat_name = self.setup_chat(chat_name, reset)
        self.chat_history = []
        self.message_buffer = []

    def create_default_aliases(self):
        self.aliases["QUIT"] = "quit"
        self.aliases["q"] = "quit"
        self.aliases["r"] = "RERUN"
        self.aliases["s"] = "SEND"
        self.aliases["c"] = "CLEAR"
        self.aliases["HELP"] = "help"
        self.aliases["h"] = "help"
        self.aliases["n"] = "NEW"
        self.aliases["e"] = "EXTRACT"
        self.aliases["l"] = "LOAD"
        self.aliases["lr"] = "LOAD_RULES"
        self.aliases["li"] = "LOAD_INTENTION"
        self.aliases["lc"] = "LOAD_COMMANDS"
        self.aliases["lg"] = "LOAD_GIVENS"

    def setup_chat(self, chat_name, reset=None):
        if os.path.exists(chat_name):
            return self.handle_existing_chat(chat_name, reset=reset)
        if os.path.exists(f"{chat_name}.md"):
            return self.handle_existing_chat(f"{chat_name}.md", reset=reset)
        if os.path.exists(f"{chat_name}_chat.md"):
            return self.handle_existing_chat(f"{chat_name}_chat.md", reset=reset)
        return self.initialize_new_chat(chat_name)

    def handle_existing_chat(self, chat_file, reset=None):
        if not os.path.exists(chat_file):
            print(f"Given chat file {chat_file} does not exist. Provide an existing chat file or create a new chat with its chat name only 'ara chat <chat_name>'. A file extension is not needed for a chat file!")
            sys.exit(1)
        chat_file_short = os.path.split(chat_file)[-1]
        
        if reset is None:
            user_input = input(f"{chat_file_short} already exists. Do you want to reset the chat? (y/N): ")
            if user_input.lower() == 'y':
                self.create_empty_chat_file(chat_file)
        elif reset:
            self.create_empty_chat_file(chat_file)
        print(f"Reloaded {chat_file_short} content")
        return chat_file

    def initialize_new_chat(self, chat_name):
        if chat_name.endswith(".md"):
            chat_name_md = chat_name
        else:
            if not chat_name.endswith("chat"):
                chat_name = f"{chat_name}_chat"
            chat_name_md = f"{chat_name}.md"
        self.create_empty_chat_file(chat_name_md)
        # open(chat_name_md, 'a', encoding='utf-8').close()
        chat_name_md_short = os.path.split(chat_name_md)[-1]
        print(f"Created new chat file {chat_name_md_short}")
        return chat_name_md

    def start_non_interactive(self):
        with open(self.chat_name, 'r') as file:
            content = file.read()
        print(content)

    def start(self):
        self.cmdloop()

    def get_user_input(self):
        user_input = ""
        while True:
            line = input()
            if not line:
                continue
            line_split = line.split()
            if line_split[0] in self.commands.keys():
                additional_input = "".join(line_split[1:])
                return (line_split[0], f"{user_input.strip()}", additional_input)
            user_input += f"{line}\n"

    def get_last_non_empty_line(self, file):
        stripped_line = ""
        lines = file.readlines()
        for line in reversed(lines):
            stripped_line = line.strip()
            if stripped_line:
                break
        return stripped_line

    def send_message(self):
        prompt_to_send = "\n".join([message for message in self.chat_history])
        role_marker = "# ara response:\n"
        print(role_marker)

        with open(self.chat_name, 'a+', encoding='utf-8') as file:
            if self.get_last_non_empty_line(file) != role_marker:
                file.write(role_marker)
            response = []
            for chunk in send_prompt(prompt_to_send):
                response.append(chunk)
                print(chunk.content, end="", flush=True)
                file.write(chunk.content)
                file.flush()
            print()

        self.message_buffer.clear()

    def save_message(self, role, message):
        role_marker = f"# {role}:"
        with open(self.chat_name, 'r', encoding='utf-8') as file:
            stripped_line = self.get_last_non_empty_line(file)
        line_to_write = f"{message}\n\n"
        if stripped_line != role_marker:
            line_to_write = f"{role_marker}\n{message}\n\n"

        with open(self.chat_name, 'a', encoding='utf-8') as file:
            file.write(line_to_write)
        self.chat_history.append(line_to_write)

    def resend_message(self):
        with open(self.chat_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if lines:
            index_to_remove = self.find_last_reply_index(lines)
            if index_to_remove is not None:
                with open(self.chat_name, 'w', encoding='utf-8') as file:
                    file.writelines(lines[:index_to_remove])
            self.chat_history = self.load_chat_history(self.chat_name)
            self.send_message()

    def find_last_reply_index(self, lines):
        index_to_remove = None
        for i, line in enumerate(reversed(lines)):
            if line.strip().startswith("# ara prompt"):
                break
            if line.strip().startswith("# ara response"):
                index_to_remove = len(lines) - i - 1
                break
        return index_to_remove

    def append_strings(self, strings):
        output = '\n'.join(strings)
        with open(self.chat_name, 'a') as file:
            file.write(output + '\n')

    def load_chat_history(self, chat_file):
        chat_history = []
        if os.path.exists(chat_file):
            with open(chat_file, 'r', encoding='utf-8') as file:
                chat_history = file.readlines()
        return chat_history

    def create_empty_chat_file(self, chat_file):
        with open(chat_file, 'w', encoding='utf-8') as file:
            file.write(self.default_chat_content)
        self.chat_history = []

    def load_file(self, file_name, prefix="", suffix=""):
        current_directory = os.path.dirname(self.chat_name)
        file_path = os.path.join(current_directory, file_name)
        if not os.path.exists(file_path):
            file_path = file_name
        if not os.path.exists(file_path):
            print(f"File {file_name} not found")
            return False
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
        with open(self.chat_name, 'a', encoding='utf-8') as chat_file:
            write_content = f"{prefix}{file_content}{suffix}\n\n"
            chat_file.write(write_content)
            return True
        return False

    def _load_helper(self, directory, pattern, file_type):
        directory_path = os.path.join(os.path.dirname(self.chat_name), directory)
        file_pattern = os.path.join(directory_path, pattern)

        matching_files = glob.glob(file_pattern)

        if not matching_files:
            print(f"No {file_type} file found.")
            return

        if len(matching_files) > 1:
            print(f"Multiple {file_type} files found:")
            for i, file in enumerate(matching_files):
                print(f"{i + 1}: {os.path.basename(file)}")
            choice = input("Please choose a file to load (enter number): ")
            try:
                choice_index = int(choice) - 1
                if choice_index < 0 or choice_index >= len(matching_files):
                    print("Invalid choice. Aborting load.")
                    return
                file_path = matching_files[choice_index]
            except ValueError:
                print("Invalid input. Aborting load.")
                return
        else:
            file_path = matching_files[0]

        if self.load_file(file_path):
            print(f"Loaded {file_type} from {os.path.basename(file_path)}")

    def _help_menu(self, verbose: bool = False):
        super()._help_menu(verbose)
        if self.aliases:
            aliases = [f"{alias} -> {command}" for alias, command in self.aliases.items()]
            self._print_topics("Aliases", aliases, verbose)

    def do_quit(self, _):
        """Exit ara-cli"""
        print("Chat ended")
        return super().do_quit(_)

    def onecmd_plus_hooks(self, line):
        # store the full line for use with default()
        self.full_input = line
        return super().onecmd_plus_hooks(line)

    def default(self, line):
        self.message_buffer.append(self.full_input)

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_LOAD(self, file_name):
        """Load a file and append its contents to chat file. Can be given the file name in-line. Will attempt to find the file relative to chat file first, then treat the given path as absolute."""
        if file_name == "":
            file_name = input("What file do you want to load? ")
        file_pattern = os.path.join(os.path.dirname(self.chat_name), file_name)
        matching_files = glob.glob(file_pattern)
        if not matching_files:
            print(f"No files matching pattern {file_name} found.")
            return
        for file_path in matching_files:
            prefix = f"File: {file_path}\n```\n"
            suffix = "\n```\n"
            if not os.path.isdir(file_path) and self.load_file(file_path, prefix=prefix, suffix=suffix):
                print(f"Loaded contents of file {file_path}")

    def complete_LOAD(self, text, line, begidx, endidx):
        return [x for x in glob.glob(text + '*')]

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_NEW(self, chat_name):
        """Create a new chat. Optionally provide a chat name in-line: NEW new_chat"""
        if chat_name == "":
            chat_name = input("What should be the new chat name? ")
        current_directory = os.path.dirname(self.chat_name)
        chat_file_path = os.path.join(current_directory, chat_name)
        self.__init__(chat_file_path)

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_RERUN(self, _):
        """Rerun the last prompt in the chat file."""
        self.resend_message()

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_CLEAR(self, _):
        """Clear the chat and the file containing it."""
        user_input = input("Are you sure you want to clear the chat? (y/N): ")
        if user_input.lower() != 'y':
            return
        self.create_empty_chat_file(self.chat_name)
        self.chat_history = self.load_chat_history(self.chat_name)
        print(f"Cleared content of {self.chat_name}")

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_LOAD_RULES(self, rules_name):
        """Load rules from ./prompt.data/*.rules.md or from a specified template directory if an argument is given. Specify global/<rules_template> to access globally defined rules templates"""
        if not rules_name:
            self._load_helper("prompt.data", "*.rules.md", "rules")
            return
        
        if rules_name.startswith("global/"):
            directory = f"{TemplatePathManager.get_template_base_path()}/prompt-modules/rules/"
            self._load_helper(directory, rules_name.removeprefix("global/"), "rules")
            return
        ara_config = ConfigManager.get_config()
        local_templates_path = ara_config.local_prompt_templates_dir
        rules_directory = f"{local_templates_path}/custom-prompt-modules/rules"
        self._load_helper(rules_directory, rules_name, "rules")

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_LOAD_INTENTION(self, intention_name):
        """Load intention from ./prompt.data/*.intention.md or from a specified template directory if an argument is given. Specify global/<intention_template> to access globally defined intention templates"""
        if not intention_name:
            self._load_helper("prompt.data", "*.intention.md", "intention")
            return
        
        if intention_name.startswith("global/"):
            directory = f"{TemplatePathManager.get_template_base_path()}/prompt-modules/intentions/"
            self._load_helper(directory, intention_name.removeprefix("global/"), "intention")
            return
        ara_config = ConfigManager.get_config()
        local_templates_path = ara_config.local_prompt_templates_dir
        intention_directory = f"{local_templates_path}/custom-prompt-modules/intentions"
        self._load_helper(intention_directory, intention_name, "intention")

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_LOAD_COMMANDS(self, commands_name):
        """Load commands from ./prompt.data/*.commands.md or from a specified template directory if an argument is given. Specify global/<commands_template> to access globally defined commands templates"""
        if not commands_name:
            self._load_helper("prompt.data", "*.commands.md", "commands")
            return
        
        if commands_name.startswith("global/"):
            directory = f"{TemplatePathManager.get_template_base_path()}/prompt-modules/commands/"
            self._load_helper(directory, commands_name.removeprefix("global/"), "commands")
            return
        ara_config = ConfigManager.get_config()
        local_templates_path = ara_config.local_prompt_templates_dir
        commands_directory = f"{local_templates_path}/custom-prompt-modules/commands"
        self._load_helper(commands_directory, commands_name, "commands")

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_EXTRACT(self, _):
        """Search for markdown code blocks containing \"# [x] extract\" as first line and \"# filename: <path/filename>\" as second line and copy the content of the code block to the specified file. The extracted code block is then marked with \"# [v] extract\""""
        extract_responses(self.chat_name, True)
        print("End of extraction")

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_LOAD_GIVENS(self, file_name):
        """Load all files listed in a ./prompt.data/config.prompt_givens.md"""
        base_directory = os.path.dirname(self.chat_name)

        if file_name == "":
            file_name = f"{base_directory}/prompt.data/config.prompt_givens.md"

        # Check the relative path first
        relative_givens_path = os.path.join(base_directory, file_name)
        if os.path.exists(relative_givens_path):
            givens_path = relative_givens_path
        elif os.path.exists(file_name):  # Check the absolute path
            givens_path = file_name
        else:
            print(f"No givens file found at {relative_givens_path} or {file_name}")
            user_input = input("Please specify a givens file: ")
            if os.path.exists(os.path.join(base_directory, user_input)):
                givens_path = os.path.join(base_directory, user_input)
            elif os.path.exists(user_input):
                givens_path = user_input
            else:
                print(f"No givens file found at {user_input}. Aborting.")
                return

        cwd = os.getcwd()
        navigator = DirectoryNavigator()
        navigator.navigate_to_target()
        os.chdir('..')
        content, image_data = load_givens(givens_path)
        os.chdir(cwd)

        with open(self.chat_name, 'a', encoding='utf-8') as chat_file:
            chat_file.write(content)

        print(f"Loaded files listed and marked in {givens_path}")

    @cmd2.with_category(CATEGORY_CHAT_CONTROL)
    def do_SEND(self, _):
        """Send prompt to the LLM."""
        message = "\n".join(self.message_buffer)
        self.save_message("ara prompt", message)
        self.send_message()