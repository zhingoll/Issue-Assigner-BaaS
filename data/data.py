class Data:
    def __init__(self, config, train_data, test_data):
        self.config = config
        self.train_data = train_data
        self.test_data = test_data

class Repo:
    def __init__(self,owner,name,topics,language) -> None:
        pass

class Issue:
    def __init__(self,owner,name,number,user,state,created_time,closed_time,labels,title,body) -> None:
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

