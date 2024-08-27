import colorama

DB_DIRECTORY = 'db'

SIMILARITY_MESSAGES = {
    (0, 0.2): f'{colorama.Fore.RED}Wrong! The answer was: $answer{colorama.Style.RESET_ALL}',
    (0.2, 0.4): f'{colorama.Fore.RED}Not quite! The answer was: $answer{colorama.Style.RESET_ALL}',
    (0.4, 0.6): f'{colorama.Fore.YELLOW}Almost correct! The answer was: $answer{colorama.Style.RESET_ALL}',
    (0.6, 0.8): f'{colorama.Fore.GREEN}Good job!{colorama.Style.RESET_ALL}',
    (0.8, 1): f'{colorama.Fore.GREEN}Correct!{colorama.Style.RESET_ALL}',
}