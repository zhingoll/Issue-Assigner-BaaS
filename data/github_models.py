from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class Repo(BaseModel):
    owner: str
    name: str
    language: Optional[str]
    languages: Optional[List[Dict[str, Any]]]
    repo_created_at: datetime
    description: Optional[str]
    topics: Optional[List[str]]
    readme: Optional[str]
    updated_at: Optional[datetime]

class Star(BaseModel):
    owner: str
    name: str
    user: str
    starred_at: datetime

class Commit(BaseModel):
    owner: str
    name: str
    sha: str
    author: Optional[str]
    authored_at: datetime
    committer: Optional[str]
    committed_at: datetime
    message: str

class RepoIssue(BaseModel):
    owner: str
    name: str
    number: int
    user: Optional[str]
    state: str
    created_at: datetime
    closed_at: Optional[datetime]
    title: Optional[str]
    body: Optional[str]
    labels: Optional[List[str]]
    is_pull: bool
    merged_at: Optional[datetime]

class ResolvedIssue(BaseModel):
    owner: str
    name: str
    number: int
    created_at: datetime
    resolved_at: Optional[datetime]
    resolver: List[str]
    events: List[Dict[str, Any]]
    issue_opener: Optional[str]

class OpenIssue(BaseModel):
    owner: str
    name: str
    number: int
    created_at: datetime
    updated_at: datetime
    events: List[Dict[str, Any]]
    issue_opener: Optional[str]

class ClosedPr(BaseModel):
    owner: str
    name: str
    number: int
    created_at: datetime
    closed_at: Optional[datetime]
    reviewer_events: List[Dict[str, Any]]
    normal_commenter_events: List[Dict[str, Any]]
    label_events: List[Dict[str, Any]]
    pr_opener: Optional[str]

class OpenPr(BaseModel):
    owner: str
    name: str
    number: int
    created_at: datetime
    updated_at: datetime
    reviewer_events: List[Dict[str, Any]]
    normal_commenter_events: List[Dict[str, Any]]
    label_events: List[Dict[str, Any]]
    pr_opener: Optional[str]

class GitHubFetchLog(BaseModel):
    owner: str
    name: str
    pid: int
    update_begin: datetime
    update_end: Optional[datetime]
    user_github_login: Optional[str]
    updated_issues: int = 0
    updated_resolved_issues: int = 0
    updated_open_issues: int = 0
    updated_closed_prs: int = 0
    updated_open_prs: int = 0
    rate: int = 0
    rate_repo_stat: int = 0
    rate_resolved_issue: int = 0
    rate_open_issue: int = 0
    rate_closed_pr: int = 0
    rate_open_pr: int = 0

class IssueContent(BaseModel):
    owner: str 
    name: str 
    number: int 
    title: str 
    body: str 
