class Data:
    def __init__(self, config, train, valid, test):
        self.config = config
        self.train_data = train
        self.valid_data = valid
        self.test_data = test

class Repo:
    def __init__(self) -> None:
        pass

class Issue:
    def __init__(self) -> None:
        pass

class PR:
    def __init__(self) -> None:
        pass

class PR_Review:
    def __init__(self) -> None:
        pass

class Commit:
    def __init__(self) -> None:
        pass

class User:
    def __init__(self,commit:Commit,pr:PR,pr_review:PR_Review) -> None:
        self.commit = commit
        self.pr = pr
        self.pr_review = pr_review

