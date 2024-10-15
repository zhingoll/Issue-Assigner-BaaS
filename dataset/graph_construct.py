from pymongo import MongoClient
from py2neo import Graph, Node, Relationship
from datetime import datetime

# 连接到 MongoDB
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['GFI-TEST1']
# repo_issues = db['repo_issue']

# 连接到 Neo4j
graph = Graph("bolt://localhost:7687", auth=("neo4j", ""))

# 删除时使用
# 使用 Cypher 分批删除节点和关系
# def delete_in_batches(graph, batch_size):
#     query = """
#     MATCH (n)
#     WITH n LIMIT $batchSize
#     DETACH DELETE n
#     RETURN count(n) as deletedCount
#     """
#     return graph.run(query, batchSize=batch_size).evaluate()
#
# # 循环直到没有数据可以删除
# total_deleted = 0
# while True:
#     deleted_count = delete_in_batches(graph, 10000) 
#     if deleted_count == 0:
#         break
#     total_deleted += deleted_count
#     print(f"Deleted {deleted_count} nodes in this batch, total deleted: {total_deleted}")
#
# print("All data deleted successfully.")


def format_datetime(dt):
    """Helper function to format datetime objects for Neo4j."""
    if isinstance(dt, datetime):
        return dt.strftime('%Y-%m-%dT%H:%M:%S')
    return dt  # If it's not a datetime object, return as is


# 添加用户节点
def add_user_node(username):
    try:
        user_node = Node("User", name=username)
        graph.merge(user_node, "User", "name")
    except Exception as e:
        print(f"An add_user_node error occurred: {e}")
    return user_node

# 添加 OpenIssue 或 ClosedIssue 节点
def add_open_closed_issue_node(doc, type):
    try:
        properties = {
            'number': doc['number'],
            'created_at': format_datetime(doc['created_at']),
            'repo': doc['name']
        }
        if type == 'OpenIssue':
            properties['updated_at'] = format_datetime(doc.get('updated_at', None))
        elif type == 'ResolvedIssue':
            properties['resolved_at'] = format_datetime(doc.get('resolved_at', None))
            properties['resolver'] = doc.get('resolver', None)

        node = Node(type, **properties)
        graph.merge(node, type, ("repo", "number"))  # Use repo and number as composite key
    except Exception as e:
        print(f"An add_open_closed_issue_node error occurred: {e}")
    return node

def add_open_closed_pr_node(doc, type):
    try:
        properties = {
            'number': doc['number'],
            'created_at': format_datetime(doc['created_at']),
            'repo': doc['name']
        }
        if type == 'OpenPR':
            properties['updated_at'] = format_datetime(doc.get('updated_at', None))
        elif type == 'ClosedPR':
            properties['closed_at'] = format_datetime(doc.get('closed_at', None))
        node = Node(type, **properties)
        graph.merge(node, type, ("repo", "number"))  # Use repo and number as composite key
    except Exception as e:
        print(f"An add_open_closed_pr_node error occurred: {e}")
    return node

def find_pr_node(pr_number,repo):
    try:
        # 查找节点，返回可能的OpenPR或ClosedPR节点
        query = """
        MATCH (n)
        WHERE (n:OpenPR OR n:ClosedPR) AND n.number = $pr_number AND n.repo = $repo
        RETURN n
        """
        # 执行查询，并获取结果
        result = graph.run(query, pr_number=pr_number, repo=repo).data()
        # print(f"找到pr{result}")
        if result:
            return result[0]['n']
    except Exception as e:
        print(f"An find_pr_node error occurred: {e}")
    return None



# 处理事件
def handle_issue_events(issue_node, events):
    if issue_node is None:
        print("Error: issue_node is None. Skipping event handling.")
        return

    tx = graph.begin()
    try:
        for event in events:
            properties = {'created_time': format_datetime(event['time'])}  # 目前简单起见，只为了显示协作行为，具体协作内容暂时不加入其中，未来可拓展。
            rel_type = event['type'].upper()
            if event['type'] == 'assigned':
                user_node = add_user_node(event['assignee']) if event.get('assignee') else None
                if user_node:
                    graph.create(Relationship(issue_node, rel_type, user_node, **properties))
            elif event['type'] == 'labeled':
                user_node = add_user_node(event['actor']) if event.get('actor') else None
                if user_node:
                    graph.create(Relationship(user_node, rel_type, issue_node, **properties))
            elif event['type'] == 'commented':
                user_node = add_user_node(event['actor']) if event.get('actor') else None
                if user_node:
                    graph.create(Relationship(user_node, rel_type, issue_node, **properties))
            elif event['type'] == 'cross-referenced' and 'source' in event:
                target_pr_node = find_pr_node(event['source'],issue_node['repo'])
                if target_pr_node:
                    graph.create(Relationship(issue_node, rel_type, target_pr_node, **properties))
    except Exception as e:
        print(f"An handle_issue_events error occurred: {e}")
    graph.commit(tx)

def handle_pr_events(pr_node,events):
    tx = graph.begin()
    try:
        for event in events:
            properties = {'created_time': format_datetime(event['time'])}
            rel_type = event['type'].upper()
            user_node = add_user_node(event['actor']) if event.get('actor') else None
            if user_node:
                graph.create(Relationship(user_node, rel_type, pr_node, **properties))
    except Exception as e:
        print(f"An handle_pr_events error occurred: {e}")
    graph.commit(tx)

# 导入数据
db_collection = ['open_issue', 'resolved_issue', 'open_pr', 'closed_pr']
def import_data():  # 由于issue和pr之间存在引用的关系，这里关注的是pr解决issue的这个引用关系，所以需要先创建pr
    tx = graph.begin()
    query_conditions = {"owner": "microsoft", "name": "vscode"}
    print("begin open_pr")
    try:
        i = 0
        for doc in db[db_collection[2]].find(query_conditions):
            properties = {'created_time': format_datetime(doc['created_at'])}
            node_type = 'OpenPR'
            node = add_open_closed_pr_node(doc, node_type)  # open pr
            opener = add_user_node(doc['pr_opener'])  # open pr opener
            graph.create(Relationship(opener, "OPENED", node, **properties))
            handle_pr_events(node, doc['reviewer_events'])  # open pr events
            handle_pr_events(node, doc['normal_commenter_events'])  # open pr events
            handle_pr_events(node, doc['label_events'])  # open pr events
            i += 1
            if i % 1000 == 0:
                print("1000 openpr update!!!")
    except Exception as e:
        print(f"An import_data error occurred: {e}")
        graph.rollback(tx)
    print("begin closed_pr")
    try:
        i = 0
        for doc in db[db_collection[3]].find(query_conditions):
            properties = {'created_time': format_datetime(doc['created_at'])}
            node_type = 'ClosedPR'
            node = add_open_closed_pr_node(doc, node_type)  # closed pr
            opener = add_user_node(doc['pr_opener'])  # closed pr opener
            graph.create(Relationship(opener, "OPENED", node, **properties))
            handle_pr_events(node, doc['reviewer_events'])  # closed pr events
            handle_pr_events(node, doc['normal_commenter_events'])  # closed pr events
            handle_pr_events(node, doc['label_events'])  # closed pr events
            i += 1
            if i % 1000 == 0:
                print("1000 ClosedPR update!!!")
    except Exception as e:
        print(f"An import_data error occurred: {e}")
        graph.rollback(tx)
    print("begin open_issue")
    try:
        i = 0
        for doc in db[db_collection[0]].find(query_conditions):
            properties = {'created_time': format_datetime(doc['created_at'])}
            node_type = 'OpenIssue'
            node = add_open_closed_issue_node(doc, node_type)  # open issue
            opener = add_user_node(doc['issue_opener'])  # open issue opener
            graph.create(Relationship(opener, "OPENED", node, **properties))
            handle_issue_events(node, doc['events'])  # open issue events
            i += 1
            if i % 1000 == 0:
                print("1000 OpenIssue update!!!")
    except Exception as e:
        print(f"An import_data error occurred: {e}")
        graph.rollback(tx)
    print("begin resolved_issue")
    try:
        i = 0
        for doc in db[db_collection[1]].find(query_conditions):
            properties = {'created_time': format_datetime(doc['created_at'])}
            node_type = 'ResolvedIssue'
            node = add_open_closed_issue_node(doc, node_type)  # resolved issue
            opener = add_user_node(doc['issue_opener'])  # resolved issue opener
            graph.create(Relationship(opener, "OPENED", node, **properties))
            handle_issue_events(node, doc['events'])  # resolved issue events
            i += 1
            if i % 1000 == 0:
                print("1000 ResolvedIssue update!!!")
    except Exception as e:
        print(f"An import_data error occurred: {e}")
        graph.rollback(tx)

    graph.commit(tx)

import_data()
print("Data import complete.")
