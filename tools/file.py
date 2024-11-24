from re import split

class FileIO():
    '''
    Mainly targeting datasets of the type "userid \t itemid \t rate"
    '''
    @staticmethod
    def read_interact_file(file: str):
        interact_data = []
        try:
            with open(file, 'r') as f:
                for line in f:
                    row = split('\t', line.strip())
                    user_id, issue_id, weight = row
                    interact_data.append([user_id, issue_id, float(weight)])
        except FileNotFoundError:
            print(f"Error: The file '{file}' does not exist.")
        except ValueError:
            print("Error: Data format error, please check the file contents.")
        return interact_data

    @staticmethod
    def read_user_file(file: str):
        # Currently, only scenarios with interactive behavior are being considered
        pass
