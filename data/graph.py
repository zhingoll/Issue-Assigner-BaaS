import networkx as nx
import pandas as pd

def fetch_data(query,driver):
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

    # 计算不同类型节点的数量
    node_types = {'Issue': 0, 'User': 0}
    # 遍历所有节点和它们的属性
    for _, attrs in G.nodes(data=True):
        node_type = attrs.get('node_type')  # 获取节点类型
        if node_type in node_types:
            node_types[node_type] += 1
    return G