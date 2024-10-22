import networkx as nx
from neo4j import GraphDatabase
import pandas as pd

uri = "bolt://localhost:7687"
username = "neo4j"
password = ""
driver = GraphDatabase.driver(uri, auth=(username, password))

owner = 'microsoft'
name = 'vscode'

query = f"""
// 查询用户直接与Issue相关的活动
MATCH (u:User)-[r]->(i)
WHERE (i:OpenIssue OR i:ResolvedIssue) AND NOT u.name ENDS WITH '[bot]' 
AND i.repo = '{name}'
RETURN u.name AS UserName, type(r) AS EventType, i.number AS IssueNumber,i.created_at AS IssueCreatedTime

UNION

// 查询通过PR交叉引用到Issue的用户活动
MATCH (u:User)-[r]->(pr)<-[:`CROSS-REFERENCED`]-(i)
WHERE (pr:OpenPR OR pr:ClosedPR) AND (i:OpenIssue OR i:ResolvedIssue) AND NOT u.name ENDS WITH '[bot]' 
AND pr.repo = '{name}'
RETURN u.name AS UserName, type(r) AS EventType, i.number AS IssueNumber,i.created_at AS IssueCreatedTime
"""


def fetch_data(query):
    with driver.session() as session:
        result = session.run(query)
        data = pd.DataFrame([r.values() for r in result], columns=result.keys())
    return data

def construct_graph(df):
    # 创建图
    G = nx.Graph()
    # 添加节点和边
    for _, row in df.iterrows():
        user = row['UserName']
        issue_number = f"{row['IssueNumber']}"
        event_type = row['EventType']
        issue_created_time = row['IssueCreatedTime']

        # 添加节点
        G.add_node(user, node_type='User', name=user)
        G.add_node(issue_number, node_type='Issue', issue_created_time=issue_created_time, issue_number=issue_number)

        # 处理边和权重
        if G.has_edge(user, issue_number):
            G[user][issue_number]['weight'] += 1
        else:
            G.add_edge(user, issue_number, weight=1, event_type=event_type)

    # 查看节点和边的情况
    print('number of nodes', G.number_of_nodes())
    print('number of edges', G.number_of_edges())
    # 计算不同类型节点的数量
    node_types = {'Issue': 0, 'User': 0}
    # 遍历所有节点和它们的属性
    for node, attrs in G.nodes(data=True):
        node_type = attrs.get('node_type')  # 获取节点类型
        if node_type in node_types:
            node_types[node_type] += 1
    # 打印不同类型的节点数量
    print("Number of issue nodes:", node_types['Issue'])
    print("Number of user nodes:", node_types['User'])
    return G