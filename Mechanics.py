class Mechanics:
    def try_execute(self, code_str: str):
        try:
            exec(code_str)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print("Ошибка исполнения кода:")
            print(tb)

    def print_error(self, error: str):
        print(f"Механика ошибки: {error}")
